-- Hypothèse volontairement insuffisante : « normalisé » veut dire « conservé ».
-- Ce SQL décrit une lecture possible, pas un échec mesuré de Genie.
SELECT COUNT(*) AS population,
       COUNT(normalized_cents) AS treated_as_preserved,
       SUM(normalized_cents) / 100.0 AS normalized_eur
FROM {{ns}}contract_observations;
