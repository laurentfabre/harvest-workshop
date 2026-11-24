SELECT COUNT(*) AS contracts, SUM(supplier_cents) / 100.0 AS supplier_eur
FROM {{ns}}contract_review
WHERE business_date = '2026-10-20' AND provider_id = 'P99';
