SELECT s.fund_id, s.calculation_id, s.consumed_source_version, s.output_value, s.output_unit,
       f.source_version, f.arrival_status,
       CASE WHEN f.arrival_status IN ('MISSING', 'WAITING', 'NOT_EXPECTED') OR f.source_version IS NULL THEN 'WAIT_SOURCE'
            WHEN f.source_version > s.consumed_source_version THEN 'RECOMPUTE_CANDIDATE'
            WHEN f.source_version = s.consumed_source_version THEN 'CURRENT'
            ELSE 'VERSION_CONFLICT' END AS calculation_status
FROM {{ns}}calculation_state s
LEFT JOIN {{ns}}fund_freshness f ON s.fund_id = f.fund_id
