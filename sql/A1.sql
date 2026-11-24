SELECT review_status, COUNT(*) AS contracts,
       COUNT(supplier_cents) AS known_amounts,
       SUM(supplier_cents) / 100.0 AS supplier_eur
FROM {{ns}}contract_review
WHERE business_date = '2026-10-20'
GROUP BY review_status
ORDER BY review_status;
