# Databricks notebook source
# MAGIC %md
# MAGIC # Harvest — preuves SQL
# MAGIC Jeu synthétique harvest-lab-2026-11-16-v1. Lecture seule ; aucune création de table.
# MAGIC Saisir le catalogue et le schéma personnel du petit lot affichés par le notebook ERES. Les cellules suivantes affichent le SQL et son résultat.

# COMMAND ----------
import re
dbutils.widgets.text("catalog", "")
dbutils.widgets.text("schema", "")
catalog = dbutils.widgets.get("catalog")
schema = dbutils.widgets.get("schema")
assert all(re.fullmatch(r"[A-Za-z0-9_-]+", x) for x in (catalog, schema)), "Catalogue et schéma requis ; conserver les noms exacts"
ns = f"`{catalog}`.`{schema}`."
display(spark.sql("SELECT current_user() AS execution_identity"))

# COMMAND ----------
# MAGIC %md
# MAGIC ## A1

# COMMAND ----------
query = "SELECT review_status, COUNT(*) AS contracts,\n       COUNT(supplier_cents) AS known_amounts,\n       SUM(supplier_cents) / 100.0 AS supplier_eur\nFROM {{ns}}contract_review\nWHERE business_date = '2026-10-20'\nGROUP BY review_status\nORDER BY review_status;\n".replace("{{ns}}", ns)
print(query)
display(spark.sql(query))

# COMMAND ----------
# MAGIC %md
# MAGIC ## A2

# COMMAND ----------
query = "SELECT contract_id, supplier_cents, normalized_cents, analytical_cents,\n       normalization_delta_cents, source_file, mapping_version, review_status\nFROM {{ns}}contract_review\nWHERE business_date = '2026-10-20'\nORDER BY contract_id;\n".replace("{{ns}}", ns)
print(query)
display(spark.sql(query))

# COMMAND ----------
# MAGIC %md
# MAGIC ## A3

# COMMAND ----------
query = "SELECT COUNT(*) AS contracts, SUM(supplier_cents) / 100.0 AS supplier_eur\nFROM {{ns}}contract_review\nWHERE business_date = '2026-10-20' AND provider_id = 'P99';\n".replace("{{ns}}", ns)
print(query)
display(spark.sql(query))

# COMMAND ----------
# MAGIC %md
# MAGIC ## B1

# COMMAND ----------
query = 'SELECT fund_id, nav_date, arrival_status, received_at_utc, deadline_utc, daily_return_pct\nFROM {{ns}}fund_freshness\nORDER BY fund_id;\n'.replace("{{ns}}", ns)
print(query)
display(spark.sql(query))

# COMMAND ----------
# MAGIC %md
# MAGIC ## B2

# COMMAND ----------
query = 'SELECT calculation_id, consumed_source_version, source_version, calculation_status, output_value, output_unit\nFROM {{ns}}calculation_review\nORDER BY calculation_id;\n'.replace("{{ns}}", ns)
print(query)
display(spark.sql(query))

# COMMAND ----------
# MAGIC %md
# MAGIC ## B3

# COMMAND ----------
query = "SELECT COUNT(*) AS funds, AVG(daily_return_pct) AS unweighted_return_pct\nFROM {{ns}}fund_freshness\nWHERE fund_id = 'F999';\n".replace("{{ns}}", ns)
print(query)
display(spark.sql(query))

# COMMAND ----------
# MAGIC %md
# MAGIC ## SA0

# COMMAND ----------
query = '-- Hypothèse volontairement insuffisante : « normalisé » veut dire « conservé ».\n-- Ce SQL décrit une lecture possible, pas un échec mesuré de Genie.\nSELECT COUNT(*) AS population,\n       COUNT(normalized_cents) AS treated_as_preserved,\n       SUM(normalized_cents) / 100.0 AS normalized_eur\nFROM {{ns}}contract_observations;\n'.replace("{{ns}}", ns)
print(query)
display(spark.sql(query))

# COMMAND ----------
# MAGIC %md
# MAGIC ## SA1

# COMMAND ----------
query = "-- Définition commune : statut gouverné par contract_review ; montant fournisseur.\nSELECT COUNT(*) AS population,\n       COUNT(CASE WHEN review_status = 'PRESERVED' THEN 1 END) AS preserved_contracts,\n       100.0 * COUNT(CASE WHEN review_status = 'PRESERVED' THEN 1 END)\n         / NULLIF(COUNT(*), 0) AS preservation_pct,\n       SUM(CASE WHEN review_status = 'PRESERVED' THEN supplier_cents END) / 100.0 AS preserved_supplier_eur,\n       COUNT(supplier_cents) AS known_supplier_amounts,\n       100.0 * COUNT(supplier_cents) / NULLIF(COUNT(*), 0) AS supplier_coverage_pct,\n       SUM(supplier_cents) / 100.0 AS known_supplier_eur\nFROM {{ns}}contract_review;\n".replace("{{ns}}", ns)
print(query)
display(spark.sql(query))

# COMMAND ----------
# MAGIC %md
# MAGIC ## SA2

# COMMAND ----------
query = "-- Réutiliser la même définition au grain fournisseur, sans moyenner les taux.\nSELECT provider_id, COUNT(*) AS population,\n       COUNT(CASE WHEN review_status = 'PRESERVED' THEN 1 END) AS preserved_contracts,\n       100.0 * COUNT(CASE WHEN review_status = 'PRESERVED' THEN 1 END)\n         / NULLIF(COUNT(*), 0) AS preservation_pct,\n       SUM(CASE WHEN review_status = 'PRESERVED' THEN supplier_cents END) / 100.0 AS preserved_supplier_eur\nFROM {{ns}}contract_review\nGROUP BY provider_id\nORDER BY provider_id;\n".replace("{{ns}}", ns)
print(query)
display(spark.sql(query))

# COMMAND ----------
# MAGIC %md
# MAGIC ## SB0

# COMMAND ----------
query = '-- Deux raccourcis volontairement insuffisants : absence = incident ; ligne jointe = fonds.\nSELECT\n  (SELECT COUNT(*) FROM {{ns}}fund_expectations e\n   LEFT JOIN {{ns}}fund_observations o ON e.fund_id = o.fund_id AND e.nav_date = o.nav_date\n   WHERE o.fund_id IS NULL) AS absent_observations,\n  (SELECT COUNT(*) FROM {{ns}}fund_expectations e\n   LEFT JOIN {{ns}}calculation_state c ON e.fund_id = c.fund_id) AS joined_rows;\n'.replace("{{ns}}", ns)
print(query)
display(spark.sql(query))

# COMMAND ----------
# MAGIC %md
# MAGIC ## SB1

# COMMAND ----------
query = "-- Grain fonds/date ; le calendrier et l'heure figée définissent le retard ouvert.\nSELECT COUNT(*) AS population,\n       COUNT(CASE WHEN expected = 1 THEN 1 END) AS expected_funds,\n       COUNT(CASE WHEN arrival_status = 'MISSING' THEN 1 END) AS overdue_missing,\n       COUNT(CASE WHEN arrival_status = 'WAITING' THEN 1 END) AS waiting_funds,\n       COUNT(CASE WHEN arrival_status = 'NOT_EXPECTED' THEN 1 END) AS not_expected_funds,\n       COUNT(CASE WHEN arrival_status = 'LATE_RECEIVED' THEN 1 END) AS late_received_funds,\n       100.0 * COUNT(CASE WHEN arrival_status = 'MISSING' THEN 1 END)\n         / NULLIF(COUNT(CASE WHEN expected = 1 THEN 1 END), 0) AS overdue_pct\nFROM {{ns}}fund_freshness;\n".replace("{{ns}}", ns)
print(query)
display(spark.sql(query))

# COMMAND ----------
# MAGIC %md
# MAGIC ## SB2

# COMMAND ----------
query = "-- Grain calcul : plusieurs calculs peuvent concerner le même fonds.\n-- Le candidat doit être examiné ; cette requête ne déclenche aucun recalcul.\nSELECT COUNT(DISTINCT calculation_id) AS calculations,\n       COUNT(DISTINCT CASE WHEN calculation_status = 'RECOMPUTE_CANDIDATE' THEN calculation_id END) AS recompute_candidates,\n       COUNT(DISTINCT CASE WHEN calculation_status = 'RECOMPUTE_CANDIDATE' THEN fund_id END) AS affected_funds,\n       COUNT(DISTINCT CASE WHEN calculation_status = 'WAIT_SOURCE' THEN calculation_id END) AS waiting_calculations\nFROM {{ns}}calculation_review;\n".replace("{{ns}}", ns)
print(query)
display(spark.sql(query))
