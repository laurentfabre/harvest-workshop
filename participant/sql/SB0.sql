-- Deux raccourcis volontairement insuffisants : absence = incident ; ligne jointe = fonds.
SELECT
  (SELECT COUNT(*) FROM {{ns}}fund_expectations e
   LEFT JOIN {{ns}}fund_observations o ON e.fund_id = o.fund_id AND e.nav_date = o.nav_date
   WHERE o.fund_id IS NULL) AS absent_observations,
  (SELECT COUNT(*) FROM {{ns}}fund_expectations e
   LEFT JOIN {{ns}}calculation_state c ON e.fund_id = c.fund_id) AS joined_rows;
