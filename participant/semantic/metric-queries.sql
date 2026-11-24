-- À exécuter uniquement après déploiement et vérification des metric views.
SELECT MEASURE(population) AS population,
       MEASURE(preserved_contracts) AS preserved_contracts,
       MEASURE(preservation_pct) AS preservation_pct,
       MEASURE(preserved_supplier_eur) AS preserved_supplier_eur
FROM {{ns}}contract_metrics;

SELECT provider_id, MEASURE(population) AS population,
       MEASURE(preserved_contracts) AS preserved_contracts,
       MEASURE(preservation_pct) AS preservation_pct,
       MEASURE(preserved_supplier_eur) AS preserved_supplier_eur
FROM {{ns}}contract_metrics GROUP BY ALL ORDER BY provider_id;

SELECT MEASURE(population) AS population, MEASURE(expected_funds) AS expected_funds,
       MEASURE(overdue_missing) AS overdue_missing, MEASURE(overdue_pct) AS overdue_pct
FROM {{ns}}fund_arrival_metrics;

SELECT MEASURE(calculations) AS calculations,
       MEASURE(recompute_candidates) AS recompute_candidates,
       MEASURE(affected_funds) AS affected_funds,
       MEASURE(waiting_calculations) AS waiting_calculations
FROM {{ns}}calculation_metrics;
