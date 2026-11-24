CREATE VIEW silver_contrats AS
SELECT c.code_contrat, c.code_client, c.code_type_contrat, c.code_conseiller,
       r.code_parent AS cabinet_id, c.code_ent, e.raison_sociale, c.statut,
       try_cast(concat(substr(c.date_signature,7,4),'-',substr(c.date_signature,4,2),'-',substr(c.date_signature,1,2)) AS DATE) AS ouverture
FROM bronze_ctr c JOIN bronze_cli p ON c.code_client = p.code_client
JOIN bronze_ref r ON c.code_conseiller = r.code AND r.type = 'conseiller'
LEFT JOIN bronze_ent e ON c.code_ent = e.code_ent;

CREATE VIEW silver_positions AS
WITH typed AS (
  SELECT p.date_lot, p.fichier, p.ligne_csv, c.code_client, c.code_contrat, c.statut, c.cabinet_id,
         p.code_sous_contrat, p.code_instrument, t.code AS support_reconnu,
         try_cast(concat(substr(p.date_valeur,7,4),'-',substr(p.date_valeur,4,2),'-',substr(p.date_valeur,1,2)) AS DATE) AS date_valorisation,
         try_cast(concat(substr(p.date_vl,7,4),'-',substr(p.date_vl,4,2),'-',substr(p.date_vl,1,2)) AS DATE) AS date_cotation,
         try_cast(p.quantite AS DECIMAL(18,4)) AS quantite,
         try_cast(p.prix AS DECIMAL(18,4)) AS cours,
         try_cast(p.montant_brut AS DECIMAL(18,2)) AS valeur_euro,
         try_cast(p.montant_disponible AS DECIMAL(18,2)) AS disponible,
         try_cast(p.montant_indisponible AS DECIMAL(18,2)) AS indisponible
  FROM bronze_pos p LEFT JOIN bronze_sub_ctr s ON p.code_sous_contrat = s.code_sous_contrat
  LEFT JOIN silver_contrats c ON s.code_contrat = c.code_contrat
  LEFT JOIN bronze_typ t ON t.groupe = 'CODE_INSTRUMENT' AND p.code_instrument = t.code
)
SELECT typed.*, CASE
  WHEN code_contrat IS NULL OR support_reconnu IS NULL THEN 'REFERENCE_ABSENTE'
  WHEN date_valorisation IS NULL OR date_valorisation > date_lot THEN 'DATE_INVALIDE'
  WHEN statut = 'O' AND date_valorisation < date_lot - INTERVAL '3' YEAR THEN 'DATE_TROP_ANCIENNE'
  WHEN quantite IS NULL OR cours IS NULL OR valeur_euro IS NULL OR disponible IS NULL OR indisponible IS NULL THEN 'MONTANT_INCOMPLET'
  WHEN disponible + indisponible <> valeur_euro OR disponible > valeur_euro THEN 'VENTILATION'
  WHEN abs(valeur_euro - quantite * cours) > 1 AND abs(valeur_euro - quantite * cours) > 0.005 * abs(valeur_euro) THEN 'COURS_QUANTITE'
  ELSE 'VALIDE' END AS regle
FROM typed;

CREATE VIEW gold_client AS
SELECT code_client AS client_id, 'PP' AS type_atelier, nom AS libelle FROM bronze_cli
UNION ALL SELECT code_ent, 'PM', raison_sociale FROM bronze_ent;

CREATE VIEW gold_produit AS
SELECT DISTINCT code_type_contrat AS produit_id, 'ERES' AS fournisseur_id FROM silver_contrats;

CREATE VIEW gold_compte AS
SELECT code_contrat AS compte_id, code_client AS client_id, code_type_contrat AS produit_id,
       ouverture, code_conseiller AS apporteur_id, cabinet_id FROM silver_contrats;

CREATE VIEW revue_positions AS
WITH dates AS (
  SELECT p.*, max(CASE WHEN regle = 'VALIDE' THEN date_valorisation END)
              OVER (PARTITION BY date_lot, code_contrat) AS derniere_date_valide
  FROM silver_positions p
)
SELECT dates.*, CASE WHEN regle <> 'VALIDE' THEN 'REJETEE'
                     WHEN date_valorisation < derniere_date_valide THEN 'HISTORIQUE'
                     ELSE 'PUBLIEE' END AS decision
FROM dates;

CREATE VIEW gold_situation AS
SELECT date_lot, code_client AS client_id, code_contrat AS compte_id, code_sous_contrat AS groupe_id,
       code_instrument AS support_id, date_valorisation, date_cotation, quantite, cours, valeur_euro
FROM revue_positions WHERE decision = 'PUBLIEE';

CREATE VIEW bilan_lot AS
SELECT date_lot, count(*) AS lues,
       sum(CASE WHEN decision='PUBLIEE' THEN 1 ELSE 0 END) AS publiees,
       sum(CASE WHEN decision='HISTORIQUE' THEN 1 ELSE 0 END) AS historiques,
       sum(CASE WHEN decision='REJETEE' THEN 1 ELSE 0 END) AS rejetees
FROM revue_positions GROUP BY date_lot;

CREATE VIEW mouvements_groupes AS
SELECT code_operation, code_instruction, type_operation, code_sous_contrat,
       count(*) AS lignes, count(nullif(code_instrument,'')) AS details,
       sum(cast(montant_brut AS DECIMAL(18,2))) AS brut_source_non_signe
FROM bronze_mvt GROUP BY code_operation, code_instruction, type_operation, code_sous_contrat;
