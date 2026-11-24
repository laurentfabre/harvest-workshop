-- Réutiliser la même définition au grain fournisseur, sans moyenner les taux.
SELECT provider_id, COUNT(*) AS population,
       COUNT(CASE WHEN review_status = 'PRESERVED' THEN 1 END) AS preserved_contracts,
       100.0 * COUNT(CASE WHEN review_status = 'PRESERVED' THEN 1 END)
         / NULLIF(COUNT(*), 0) AS preservation_pct,
       SUM(CASE WHEN review_status = 'PRESERVED' THEN supplier_cents END) / 100.0 AS preserved_supplier_eur
FROM {{ns}}contract_review
GROUP BY provider_id
ORDER BY provider_id;
