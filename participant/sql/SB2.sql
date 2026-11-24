-- Grain calcul : plusieurs calculs peuvent concerner le même fonds.
-- Le candidat doit être examiné ; cette requête ne déclenche aucun recalcul.
SELECT COUNT(DISTINCT calculation_id) AS calculations,
       COUNT(DISTINCT CASE WHEN calculation_status = 'RECOMPUTE_CANDIDATE' THEN calculation_id END) AS recompute_candidates,
       COUNT(DISTINCT CASE WHEN calculation_status = 'RECOMPUTE_CANDIDATE' THEN fund_id END) AS affected_funds,
       COUNT(DISTINCT CASE WHEN calculation_status = 'WAIT_SOURCE' THEN calculation_id END) AS waiting_calculations
FROM {{ns}}calculation_review;
