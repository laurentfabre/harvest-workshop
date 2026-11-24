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
fingerprints = __ARCHIVE_HASHES__
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
# __TRANSFORMATIONS__

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
# __FOLLOW_ON__


# COMMAND ----------
# MAGIC %md
# MAGIC ## Reçu de mon schéma
# MAGIC Dans Market Data, ouvrez Mes accès puis collez ce reçu pour renseigner le catalogue et le schéma. Ajoutez les liens de votre espace Genie et de Builder.
# COMMAND ----------
if stamp == "20261123":
    print(json.dumps({"format": "harvest-schema-v1", "participant": team, "catalog": catalog, "schema": schema}, ensure_ascii=False))
else:
    print("Pour Market Data, utilisez le reçu du petit lot du 23 novembre.")
