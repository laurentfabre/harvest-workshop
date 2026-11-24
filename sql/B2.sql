SELECT calculation_id, consumed_source_version, source_version, calculation_status, output_value, output_unit
FROM {{ns}}calculation_review
ORDER BY calculation_id;
