SELECT COUNT(*) AS funds, AVG(daily_return_pct) AS unweighted_return_pct
FROM {{ns}}fund_freshness
WHERE fund_id = 'F999';
