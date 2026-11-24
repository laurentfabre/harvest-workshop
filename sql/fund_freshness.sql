SELECT e.fund_id, e.nav_date, e.expected, e.deadline_utc, e.calendar_note,
       o.nav_eur, o.previous_nav_eur, o.received_at_utc, o.source_version, o.source_file,
       CASE WHEN e.expected = 0 THEN 'NOT_EXPECTED'
            WHEN o.fund_id IS NULL OR o.received_at_utc > '2026-10-20 10:00:00'
              THEN CASE WHEN e.deadline_utc <= '2026-10-20 10:00:00' THEN 'MISSING' ELSE 'WAITING' END
            WHEN o.received_at_utc > e.deadline_utc THEN 'LATE_RECEIVED'
            ELSE 'ON_TIME' END AS arrival_status,
       CASE WHEN o.received_at_utc <= '2026-10-20 10:00:00' AND o.previous_nav_eur > 0
            THEN 100.0 * (o.nav_eur / (1.0 * o.previous_nav_eur) - 1.0)
            ELSE NULL END AS daily_return_pct
FROM {{ns}}fund_expectations e
LEFT JOIN {{ns}}fund_observations o
  ON e.fund_id = o.fund_id AND e.nav_date = o.nav_date
