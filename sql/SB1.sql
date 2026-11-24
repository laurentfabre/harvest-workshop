-- Grain fonds/date ; le calendrier et l'heure figée définissent le retard ouvert.
SELECT COUNT(*) AS population,
       COUNT(CASE WHEN expected = 1 THEN 1 END) AS expected_funds,
       COUNT(CASE WHEN arrival_status = 'MISSING' THEN 1 END) AS overdue_missing,
       COUNT(CASE WHEN arrival_status = 'WAITING' THEN 1 END) AS waiting_funds,
       COUNT(CASE WHEN arrival_status = 'NOT_EXPECTED' THEN 1 END) AS not_expected_funds,
       COUNT(CASE WHEN arrival_status = 'LATE_RECEIVED' THEN 1 END) AS late_received_funds,
       100.0 * COUNT(CASE WHEN arrival_status = 'MISSING' THEN 1 END)
         / NULLIF(COUNT(CASE WHEN expected = 1 THEN 1 END), 0) AS overdue_pct
FROM {{ns}}fund_freshness;
