SELECT fund_id, nav_date, arrival_status, received_at_utc, deadline_utc, daily_return_pct
FROM {{ns}}fund_freshness
ORDER BY fund_id;
