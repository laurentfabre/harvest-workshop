-- Définition commune : statut gouverné par contract_review ; montant fournisseur.
SELECT COUNT(*) AS population,
       COUNT(CASE WHEN review_status = 'PRESERVED' THEN 1 END) AS preserved_contracts,
       100.0 * COUNT(CASE WHEN review_status = 'PRESERVED' THEN 1 END)
         / NULLIF(COUNT(*), 0) AS preservation_pct,
       SUM(CASE WHEN review_status = 'PRESERVED' THEN supplier_cents END) / 100.0 AS preserved_supplier_eur,
       COUNT(supplier_cents) AS known_supplier_amounts,
       100.0 * COUNT(supplier_cents) / NULLIF(COUNT(*), 0) AS supplier_coverage_pct,
       SUM(supplier_cents) / 100.0 AS known_supplier_eur
FROM {{ns}}contract_review;
