SELECT contract_id, supplier_cents, normalized_cents, analytical_cents,
       normalization_delta_cents, source_file, mapping_version, review_status
FROM {{ns}}contract_review
WHERE business_date = '2026-10-20'
ORDER BY contract_id;
