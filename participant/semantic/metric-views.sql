-- EXTENSION FACULTATIVE : revue, droits et compatibilité requis avant exécution.
-- Définitions préparées, pas de déploiement implicite. Aucun CREATE OR REPLACE.

CREATE VIEW {{ns}}contract_metrics
WITH METRICS
LANGUAGE YAML
AS $$
version: 1.1
source: "{{ns}}contract_review"
comment: "Conservation numérique des contrats au snapshot pédagogique. Ne vaut pas autorisation de livraison."
dimensions:
  - name: "provider_id"
    expr: "provider_id"
    display_name: "Fournisseur"
    comment: "Identifiant du fournisseur fictif."
  - name: "business_date"
    expr: "business_date"
    display_name: "Date métier"
    comment: "Date du contrat observé ; snapshot immuable."
  - name: "review_status"
    expr: "review_status"
    display_name: "Statut de conservation"
    comment: "Définition commune de contract_review ; aucune cause inférée."
measures:
  - name: "population"
    expr: "COUNT(*)"
    display_name: "Contrats observés"
    comment: "Nombre de contrats dans le périmètre filtré."
  - name: "preserved_contracts"
    expr: "COUNT(CASE WHEN review_status = 'PRESERVED' THEN 1 END)"
    display_name: "Contrats conservés"
    comment: "Contrats dont la valeur fournisseur est préservée ; estimation indépendante."
  - name: "preservation_pct"
    expr: "100.0 * COUNT(CASE WHEN review_status = 'PRESERVED' THEN 1 END) / NULLIF(COUNT(*), 0)"
    display_name: "Taux de conservation"
    comment: "Pourcentage sur tous les contrats filtrés. Réagréger le ratio ; NULL si population vide."
  - name: "preserved_supplier_eur"
    expr: "SUM(CASE WHEN review_status = 'PRESERVED' THEN supplier_cents END) / 100.0"
    display_name: "Montant fournisseur conservé"
    comment: "EUR ; somme des montants fournisseur conservés, NULL si aucun montant connu."
  - name: "known_supplier_amounts"
    expr: "COUNT(supplier_cents)"
    display_name: "Montants fournisseur connus"
    comment: "Couverture des montants ; toujours accompagner une somme."
  - name: "supplier_coverage_pct"
    expr: "100.0 * COUNT(supplier_cents) / NULLIF(COUNT(*), 0)"
    display_name: "Complétude fournisseur"
    comment: "Pourcentage de montants fournisseur connus sur tous les contrats filtrés, tous statuts inclus ; distinct de la conservation."
  - name: "known_supplier_eur"
    expr: "SUM(supplier_cents) / 100.0"
    display_name: "Montant fournisseur connu"
    comment: "EUR ; total partiel si couverture incomplète. Ne remplace pas le montant conservé."
$$;

CREATE VIEW {{ns}}fund_arrival_metrics
WITH METRICS
LANGUAGE YAML
AS $$
version: 1.1
source: "{{ns}}fund_freshness"
comment: "Fraîcheur des VL au 20 octobre 2026 à 10:00 UTC. Une ligne par fonds/date ; calendrier et absences conservés."
dimensions:
  - name: "nav_date"
    expr: "nav_date"
    display_name: "Date de VL"
    comment: "Date attendue dans le calendrier."
  - name: "arrival_status"
    expr: "arrival_status"
    display_name: "État de réception"
    comment: "MISSING, WAITING, NOT_EXPECTED, LATE_RECEIVED ou ON_TIME ; non interchangeables."
measures:
  - name: "population"
    expr: "COUNT(*)"
    display_name: "Fonds et dates observés"
    comment: "Nombre de couples fonds/date ; pas un nombre de calculs."
  - name: "expected_funds"
    expr: "COUNT(CASE WHEN expected = 1 THEN 1 END)"
    display_name: "VL attendues"
    comment: "Dénominateur défini par le calendrier."
  - name: "overdue_missing"
    expr: "COUNT(CASE WHEN arrival_status = 'MISSING' THEN 1 END)"
    display_name: "Absences en retard"
    comment: "Nombre de fonds/date attendus, échus et sans réception à 10:00 UTC."
  - name: "overdue_pct"
    expr: "100.0 * COUNT(CASE WHEN arrival_status = 'MISSING' THEN 1 END) / NULLIF(COUNT(CASE WHEN expected = 1 THEN 1 END), 0)"
    display_name: "Taux d’absences en retard"
    comment: "Pourcentage des VL attendues ; NULL si aucune attente. Ne pas moyenner les taux."
$$;

CREATE VIEW {{ns}}calculation_metrics
WITH METRICS
LANGUAGE YAML
AS $$
version: 1.1
source: "{{ns}}calculation_review"
comment: "Impact direct d’une version fournisseur sur des calculs, au snapshot à date unique. Aucun recalcul déclenché."
dimensions:
  - name: "fund_id"
    expr: "fund_id"
    display_name: "Fonds"
    comment: "Fonds consommé ; plusieurs calculs peuvent le partager."
  - name: "calculation_status"
    expr: "calculation_status"
    display_name: "État du calcul"
    comment: "État issu de la comparaison de version ; candidat ne signifie pas recalculé."
measures:
  - name: "calculations"
    expr: "COUNT(DISTINCT calculation_id)"
    display_name: "Calculs distincts"
    comment: "Grain calculation_id, non fund_id."
  - name: "recompute_candidates"
    expr: "COUNT(DISTINCT CASE WHEN calculation_status = 'RECOMPUTE_CANDIDATE' THEN calculation_id END)"
    display_name: "Calculs candidats"
    comment: "Calculs ayant consommé une version antérieure ; à examiner."
  - name: "affected_funds"
    expr: "COUNT(DISTINCT CASE WHEN calculation_status = 'RECOMPUTE_CANDIDATE' THEN fund_id END)"
    display_name: "Fonds concernés"
    comment: "Fonds distincts associés aux candidats. Mesure non additive entre groupes de calculs."
  - name: "waiting_calculations"
    expr: "COUNT(DISTINCT CASE WHEN calculation_status = 'WAIT_SOURCE' THEN calculation_id END)"
    display_name: "Calculs en attente"
    comment: "Calculs dont la source manque ; ce n’est pas une exécution en échec."
$$;
