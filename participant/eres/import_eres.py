# Databricks notebook source
# MAGIC %md
# MAGIC # Premier cas · Des fichiers ERES aux situations publiables
# MAGIC Dans votre édition d’essai, chargez le ZIP daté dans un volume Unity Catalog accessible en lecture et écriture. Renseignez son chemin et votre code personnel affiché dans le parcours. Exécutez les cellules dans l’ordre sur un compute Python compatible avec les volumes. Chaque lot utilise son propre schéma dans le catalogue du volume.

# COMMAND ----------
import csv
import hashlib
import io
import json
import re
import tempfile
from datetime import datetime
from pathlib import Path
from zipfile import ZipFile
from pyspark.sql import functions as F

dbutils.widgets.text("archive", "", "Chemin /Volumes/... du ZIP daté")
dbutils.widgets.text("equipe", "", "Code personnel affiché dans Mon parcours")
# COMMAND ----------
archive = Path(dbutils.widgets.get("archive").strip())
team = dbutils.widgets.get("equipe").strip()
if not re.fullmatch(r"[a-z][a-z0-9_]{0,29}", team):
    raise ValueError("Choisir votre code personnel en minuscules, sans espace.")
if len(archive.parts) < 6 or archive.parts[:2] != ("/", "Volumes") or ".." in archive.parts:
    raise ValueError("Fournir le chemin complet du ZIP dans votre volume Unity Catalog.")
catalog = archive.parts[2]
if not re.fullmatch(r"[A-Za-z0-9_-]+", catalog):
    raise ValueError("Le nom du catalogue doit contenir des lettres, chiffres, tirets ou underscores.")
fingerprints = {'20261123_HARVEST.zip': '39596a5ab3e6db067945e8e143af8d7c0aab696432b2688ba3c5a14fe80e2cca', '20261124_HARVEST.zip': '3e25b6f671b5b6ce488aa8358300ef240b844e7fcb4ce6aa87f02ad0cddcf7de'}
if archive.name not in fingerprints:
    raise ValueError("Choisir une des deux archives datées du kit.")
digest = hashlib.sha256(archive.read_bytes()).hexdigest()
if digest != fingerprints[archive.name]:
    raise ValueError("Empreinte différente du jeu d’atelier distribué.")
stamp = archive.name[:8]
lot = datetime.strptime(stamp, "%Y%m%d").date()
schema = f"atelier_eres_{team}_{stamp}_{digest[:8]}"
namespace = f"`{catalog}`.`{schema}`"
marker = f"harvest-eres-v6/{digest}"
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {namespace} COMMENT '{marker}'")
properties = spark.sql(f"DESCRIBE SCHEMA EXTENDED {namespace}").collect()
if not any(row[1] == marker for row in properties):
    raise ValueError("Le schéma existe déjà avec une autre provenance.")
spark.sql(f"USE CATALOG `{catalog}`")
spark.sql(f"USE SCHEMA `{schema}`")
print(f"Lot {lot} · schéma {namespace}")
display(spark.sql("SELECT current_user() AS identite, current_catalog() AS catalogue, current_schema() AS schema"))

# COMMAND ----------
# MAGIC %md
# MAGIC ## Bronze · inspecter les sources
# MAGIC Comparer les lignes du fichier POS aux enregistrements de bronze_pos. Garder la date de lot, le fichier et le numéro de ligne pour retrouver une anomalie. Un rejeu de la même archive reprend les objets de cette édition.
# COMMAND ----------
families = ["REF", "CLI", "ENT", "CTR", "SUB_CTR", "TYP", "POS", "MVT"]
with ZipFile(archive) as source, tempfile.TemporaryDirectory(prefix="eres_", dir=str(archive.parent)) as staging:
    names = [f"{stamp}_HARVEST_{family}.csv" for family in families]
    if sorted(source.namelist()) != sorted(names):
        raise ValueError("Le kit d’atelier attend huit membres CSV datés.")
    for family, name in zip(families, names):
        table = f"{namespace}.`bronze_{family.lower()}`"
        if spark.catalog.tableExists(table):
            continue
        staged = Path(staging) / name
        with source.open(name) as raw, staged.open("w", encoding="utf-8", newline="") as output:
            reader = csv.reader(io.TextIOWrapper(raw, encoding="utf-8", newline=""), delimiter=";", strict=True)
            writer = csv.writer(output, delimiter=";", lineterminator="\n")
            writer.writerow(next(reader) + ["ligne_csv"])
            for line, row in enumerate(reader, 2):
                writer.writerow(row + [line])
        bronze = (spark.read.option("header", True).option("delimiter", ";").option("mode", "FAILFAST")
                  .csv(str(staged)).withColumn("ligne_csv", F.col("ligne_csv").cast("int"))
                  .withColumn("fichier", F.lit(name)).withColumn("date_lot", F.lit(lot)))
        bronze.write.format("delta").mode("ignore").saveAsTable(table)
display(spark.sql("SELECT fichier, ligne_csv, date_valeur, montant_brut, montant_disponible, montant_indisponible FROM bronze_pos ORDER BY ligne_csv LIMIT 10"))

# COMMAND ----------
# MAGIC %md
# MAGIC ## Silver et Gold · exécuter et expliquer les règles
# MAGIC À chaque table de revue, repérer le grain, les clés et la première règle bloquante. La dernière date est choisie parmi les positions valides de chaque compte.
# COMMAND ----------
spark.sql("""
CREATE VIEW IF NOT EXISTS silver_contrats AS
SELECT c.code_contrat, c.code_client, c.code_type_contrat, c.code_conseiller,
       r.code_parent AS cabinet_id, c.code_ent, e.raison_sociale, c.statut,
       try_cast(concat(substr(c.date_signature,7,4),'-',substr(c.date_signature,4,2),'-',substr(c.date_signature,1,2)) AS DATE) AS ouverture
FROM bronze_ctr c JOIN bronze_cli p ON c.code_client = p.code_client
JOIN bronze_ref r ON c.code_conseiller = r.code AND r.type = 'conseiller'
LEFT JOIN bronze_ent e ON c.code_ent = e.code_ent
""")

# COMMAND ----------
spark.sql("""
CREATE VIEW IF NOT EXISTS silver_positions AS
WITH typed AS (
  SELECT p.date_lot, p.fichier, p.ligne_csv, c.code_client, c.code_contrat, c.statut, c.cabinet_id,
         p.code_sous_contrat, p.code_instrument, t.code AS support_reconnu,
         try_cast(concat(substr(p.date_valeur,7,4),'-',substr(p.date_valeur,4,2),'-',substr(p.date_valeur,1,2)) AS DATE) AS date_valorisation,
         try_cast(concat(substr(p.date_vl,7,4),'-',substr(p.date_vl,4,2),'-',substr(p.date_vl,1,2)) AS DATE) AS date_cotation,
         try_cast(p.quantite AS DECIMAL(18,4)) AS quantite,
         try_cast(p.prix AS DECIMAL(18,4)) AS cours,
         try_cast(p.montant_brut AS DECIMAL(18,2)) AS valeur_euro,
         try_cast(p.montant_disponible AS DECIMAL(18,2)) AS disponible,
         try_cast(p.montant_indisponible AS DECIMAL(18,2)) AS indisponible
  FROM bronze_pos p LEFT JOIN bronze_sub_ctr s ON p.code_sous_contrat = s.code_sous_contrat
  LEFT JOIN silver_contrats c ON s.code_contrat = c.code_contrat
  LEFT JOIN bronze_typ t ON t.groupe = 'CODE_INSTRUMENT' AND p.code_instrument = t.code
)
SELECT typed.*, CASE
  WHEN code_contrat IS NULL OR support_reconnu IS NULL THEN 'REFERENCE_ABSENTE'
  WHEN date_valorisation IS NULL OR date_valorisation > date_lot THEN 'DATE_INVALIDE'
  WHEN statut = 'O' AND date_valorisation < date_lot - INTERVAL '3' YEAR THEN 'DATE_TROP_ANCIENNE'
  WHEN quantite IS NULL OR cours IS NULL OR valeur_euro IS NULL OR disponible IS NULL OR indisponible IS NULL THEN 'MONTANT_INCOMPLET'
  WHEN disponible + indisponible <> valeur_euro OR disponible > valeur_euro THEN 'VENTILATION'
  WHEN abs(valeur_euro - quantite * cours) > 1 AND abs(valeur_euro - quantite * cours) > 0.005 * abs(valeur_euro) THEN 'COURS_QUANTITE'
  ELSE 'VALIDE' END AS regle
FROM typed
""")

# COMMAND ----------
spark.sql("""
CREATE VIEW IF NOT EXISTS gold_client AS
SELECT code_client AS client_id, 'PP' AS type_atelier, nom AS libelle FROM bronze_cli
UNION ALL SELECT code_ent, 'PM', raison_sociale FROM bronze_ent
""")

# COMMAND ----------
spark.sql("""
CREATE VIEW IF NOT EXISTS gold_produit AS
SELECT DISTINCT code_type_contrat AS produit_id, 'ERES' AS fournisseur_id FROM silver_contrats
""")

# COMMAND ----------
spark.sql("""
CREATE VIEW IF NOT EXISTS gold_compte AS
SELECT code_contrat AS compte_id, code_client AS client_id, code_type_contrat AS produit_id,
       ouverture, code_conseiller AS apporteur_id, cabinet_id FROM silver_contrats
""")

# COMMAND ----------
spark.sql("""
CREATE VIEW IF NOT EXISTS revue_positions AS
WITH dates AS (
  SELECT p.*, max(CASE WHEN regle = 'VALIDE' THEN date_valorisation END)
              OVER (PARTITION BY date_lot, code_contrat) AS derniere_date_valide
  FROM silver_positions p
)
SELECT dates.*, CASE WHEN regle <> 'VALIDE' THEN 'REJETEE'
                     WHEN date_valorisation < derniere_date_valide THEN 'HISTORIQUE'
                     ELSE 'PUBLIEE' END AS decision
FROM dates
""")

# COMMAND ----------
spark.sql("""
CREATE VIEW IF NOT EXISTS gold_situation AS
SELECT date_lot, code_client AS client_id, code_contrat AS compte_id, code_sous_contrat AS groupe_id,
       code_instrument AS support_id, date_valorisation, date_cotation, quantite, cours, valeur_euro
FROM revue_positions WHERE decision = 'PUBLIEE'
""")

# COMMAND ----------
spark.sql("""
CREATE VIEW IF NOT EXISTS bilan_lot AS
SELECT date_lot, count(*) AS lues,
       sum(CASE WHEN decision='PUBLIEE' THEN 1 ELSE 0 END) AS publiees,
       sum(CASE WHEN decision='HISTORIQUE' THEN 1 ELSE 0 END) AS historiques,
       sum(CASE WHEN decision='REJETEE' THEN 1 ELSE 0 END) AS rejetees
FROM revue_positions GROUP BY date_lot
""")

# COMMAND ----------
spark.sql("""
CREATE VIEW IF NOT EXISTS mouvements_groupes AS
SELECT code_operation, code_instruction, type_operation, code_sous_contrat,
       count(*) AS lignes, count(nullif(code_instrument,'')) AS details,
       sum(cast(montant_brut AS DECIMAL(18,2))) AS brut_source_non_signe
FROM bronze_mvt GROUP BY code_operation, code_instruction, type_operation, code_sous_contrat
""")

# COMMAND ----------
# MAGIC %md
# MAGIC ## Vérifier le lot
# MAGIC Comparer ce bilan aux pièces sources avant de l’utiliser dans Genie. PUBLIEE désigne une ligne de la vue Gold de cet exercice. L’envoi O2S et le calcul des flux signés restent des prolongements.
# COMMAND ----------
display(spark.sql("SELECT * FROM bilan_lot"))
display(spark.sql("SELECT decision, regle, count(*) AS positions FROM revue_positions GROUP BY decision, regle ORDER BY decision, regle"))
display(spark.sql("SELECT * FROM revue_positions WHERE decision='REJETEE' ORDER BY ligne_csv LIMIT 5"))
display(spark.sql("SELECT * FROM mouvements_groupes WHERE lignes > details ORDER BY code_operation LIMIT 5"))
print(f"Dans Genie, sélectionner {namespace}.revue_positions et {namespace}.bilan_lot. Pour le parcours fonds, utiliser le même catalogue et le même schéma.")

# COMMAND ----------
# MAGIC %md
# MAGIC ## Préparer le parcours suivant · données de fonds
# MAGIC Ces petites vues utilisent le jeu synthétique du parcours suivant, avec son propre instant d’observation au 20 octobre.
# COMMAND ----------
spark.sql("""
CREATE VIEW IF NOT EXISTS contract_observations AS SELECT * FROM VALUES
('C001', '2026-10-20', 'P01', 'json-v2', 'p01_20261020.json', 'm2', 20025, 20025, 20100, NULL),
('C002', '2026-10-20', 'P02', 'legacy-csv', 'p02_20261020.csv', 'm1', 4830000, 483000, 4900000, NULL),
('C003', '2026-10-20', 'P02', 'legacy-csv', 'p02_20261020.csv', 'm1', 350000, NULL, NULL, 'INVALID_DECIMAL'),
('C004', '2026-10-20', 'P03', 'custom-xml', 'p03_20261020.xml', 'm2', NULL, NULL, NULL, 'AMOUNT_MISSING'),
('C005', '2026-10-20', 'P01', 'json-v2', 'p01_20261020.json', 'm2', 800000, 800000, 825000, NULL),
('C006', '2026-10-20', 'P03', 'custom-xml', 'p03_20261020.xml', 'm2', 640000, 640000, NULL, NULL) AS seed(contract_id, business_date, provider_id, format_family, source_file, mapping_version, supplier_cents, normalized_cents, analytical_cents, conversion_error)
""")

# COMMAND ----------
spark.sql("""
CREATE VIEW IF NOT EXISTS fund_expectations AS SELECT * FROM VALUES
('F001', '2026-10-20', 1, '2026-10-20 08:00:00', 'Jour de valorisation'),
('F002', '2026-10-20', 1, '2026-10-20 08:00:00', 'Jour de valorisation'),
('F003', '2026-10-20', 1, '2026-10-20 08:00:00', 'Jour de valorisation'),
('F004', '2026-10-20', 0, '2026-10-20 08:00:00', 'Pas de VL attendue selon le calendrier de ce fonds'),
('F005', '2026-10-20', 1, '2026-10-20 12:00:00', 'Échéance à midi UTC'),
('F006', '2026-10-20', 1, '2026-10-20 08:00:00', 'Jour de valorisation') AS seed(fund_id, nav_date, expected, deadline_utc, calendar_note)
""")

# COMMAND ----------
spark.sql("""
CREATE VIEW IF NOT EXISTS fund_observations AS SELECT * FROM VALUES
('F001', '2026-10-20', 102, 100, '2026-10-20 07:30:00', 2, 'f001_v2.csv'),
('F002', '2026-10-20', 100, 100, '2026-10-20 07:45:00', 1, 'f002_v1.csv'),
('F006', '2026-10-20', 202, 200, '2026-10-20 09:30:00', 2, 'f006_v2.csv') AS seed(fund_id, nav_date, nav_eur, previous_nav_eur, received_at_utc, source_version, source_file)
""")

# COMMAND ----------
spark.sql("""
CREATE VIEW IF NOT EXISTS calculation_state AS SELECT * FROM VALUES
('F001', 'F001:daily_return', 1, 1, 'percent'),
('F001', 'F001:risk_score', 1, 3, 'score'),
('F002', 'F002:daily_return', 1, 0, 'percent'),
('F003', 'F003:daily_return', 1, 0.5, 'percent'),
('F003', 'F003:risk_score', 1, 4, 'score'),
('F006', 'F006:daily_return', 1, 0.5, 'percent') AS seed(fund_id, calculation_id, consumed_source_version, output_value, output_unit)
""")

# COMMAND ----------
spark.sql("""
CREATE VIEW IF NOT EXISTS contract_review AS SELECT c.*,
  CASE WHEN supplier_cents IS NULL THEN 'SOURCE_INCOMPLETE'
       WHEN conversion_error IS NOT NULL OR normalized_cents IS NULL THEN 'CONVERSION_FAILED'
       WHEN supplier_cents <> normalized_cents THEN 'VALUE_CHANGED'
       ELSE 'PRESERVED' END AS review_status,
  normalized_cents - supplier_cents AS normalization_delta_cents
FROM contract_observations c
""")

# COMMAND ----------
spark.sql("""
CREATE VIEW IF NOT EXISTS fund_freshness AS SELECT e.fund_id, e.nav_date, e.expected, e.deadline_utc, e.calendar_note,
       o.nav_eur, o.previous_nav_eur, o.received_at_utc, o.source_version, o.source_file,
       CASE WHEN e.expected = 0 THEN 'NOT_EXPECTED'
            WHEN o.fund_id IS NULL OR o.received_at_utc > '2026-10-20 10:00:00'
              THEN CASE WHEN e.deadline_utc <= '2026-10-20 10:00:00' THEN 'MISSING' ELSE 'WAITING' END
            WHEN o.received_at_utc > e.deadline_utc THEN 'LATE_RECEIVED'
            ELSE 'ON_TIME' END AS arrival_status,
       CASE WHEN o.received_at_utc <= '2026-10-20 10:00:00' AND o.previous_nav_eur > 0
            THEN 100.0 * (o.nav_eur / (1.0 * o.previous_nav_eur) - 1.0)
            ELSE NULL END AS daily_return_pct
FROM fund_expectations e
LEFT JOIN fund_observations o
  ON e.fund_id = o.fund_id AND e.nav_date = o.nav_date
""")

# COMMAND ----------
spark.sql("""
CREATE VIEW IF NOT EXISTS calculation_review AS SELECT s.fund_id, s.calculation_id, s.consumed_source_version, s.output_value, s.output_unit,
       f.source_version, f.arrival_status,
       CASE WHEN f.arrival_status IN ('MISSING', 'WAITING', 'NOT_EXPECTED') OR f.source_version IS NULL THEN 'WAIT_SOURCE'
            WHEN f.source_version > s.consumed_source_version THEN 'RECOMPUTE_CANDIDATE'
            WHEN f.source_version = s.consumed_source_version THEN 'CURRENT'
            ELSE 'VERSION_CONFLICT' END AS calculation_status
FROM calculation_state s
LEFT JOIN fund_freshness f ON s.fund_id = f.fund_id
""")


# COMMAND ----------
# MAGIC %md
# MAGIC ## Reçu de mon schéma
# MAGIC Dans Market Data, ouvrez Mes accès puis collez ce reçu pour renseigner le catalogue et le schéma. Ajoutez les liens de votre espace Genie et de Builder.
# COMMAND ----------
if stamp == "20261123":
    print(json.dumps({"format": "harvest-schema-v1", "participant": team, "catalog": catalog, "schema": schema}, ensure_ascii=False))
else:
    print("Pour Market Data, utilisez le reçu du petit lot du 23 novembre.")
