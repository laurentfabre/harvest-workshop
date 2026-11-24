SELECT c.*,
  CASE WHEN supplier_cents IS NULL THEN 'SOURCE_INCOMPLETE'
       WHEN conversion_error IS NOT NULL OR normalized_cents IS NULL THEN 'CONVERSION_FAILED'
       WHEN supplier_cents <> normalized_cents THEN 'VALUE_CHANGED'
       ELSE 'PRESERVED' END AS review_status,
  normalized_cents - supplier_cents AS normalization_delta_cents
FROM {{ns}}contract_observations c
