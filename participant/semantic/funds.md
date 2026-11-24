# Fonds · distinguer l’absence de l’incident

Laboratoire local sur le snapshot synthétique au 20/10/2026 à 10:00 UTC. Les comparaisons sont calculées par les SQL fournis lors du build, pas par une requête live du portail. Les raccourcis sont des hypothèses pédagogiques explicites, pas des erreurs attribuées à Genie.

## 1 · Prédire, puis comparer

Avant de révéler les résultats, prédisez : toutes les VL absentes sont-elles en retard ? Une ligne après jointure sur les calculs représente-t-elle toujours un fonds ?

1. 2 min · Prédisez les résultats de SB0 : absences et lignes jointes. Précisez ce que signifie « fonds en incident ». Ne consultez pas SB1.

2. 3 min · Explorez F003, F005 puis F001 : échéance, observation, version et calculs. Identifiez les clés et la relation un-à-plusieurs.

3. 3 min · Comparez SB0/SB1/SB2 : quels faux incidents disparaissent, et combien de fonds distincts correspondent aux calculs candidats ?

4. 4 min · Posez à Genie la question avec heure, calendrier et grain explicites ; inspectez son SQL sans lui donner les résultats chiffrés.

5. 8 min · Complétez l’enquête et vérifiez le contrat pour Builder. Échangez les rôles métier/IT.

## 2 · Ontologie : objets et relations

### Fonds

L’entité métier ; son identifiant ne suffit pas pour joindre des observations couvrant plusieurs dates.

**Grain / clé :** fund_id ; une seule nav_date par fonds dans ce jeu.

**Source :** {{ns}}fund_expectations.fund_id

### Échéance attendue

L’obligation de recevoir une VL à une date et une heure, selon le calendrier. Une non-attente reste visible.

**Grain / clé :** fund_id + nav_date ; expected, deadline_utc.

**Source :** {{ns}}fund_expectations

### VL reçue

Une valeur, son heure de réception et sa version fournisseur. L’absence est une relation vide, pas une valeur à zéro.

**Grain / clé :** Zéro ou une observation pour fund_id + nav_date dans ce snapshot.

**Source :** {{ns}}fund_observations → {{ns}}fund_freshness

### Calcul consommateur

Un résultat antérieur, son unité et la version qu’il a consommée. Plusieurs calculs peuvent dépendre du même fonds.

**Grain / clé :** calculation_id ; fund_id est non unique.

**Source :** {{ns}}calculation_state → {{ns}}calculation_review

- Un fonds suit un calendrier de VL — 1 → 1 échéance dans ce snapshot. Le calendrier définit le dénominateur des VL attendues.

- L’échéance peut être satisfaite par une observation — 1 → 0..1. LEFT JOIN sur fund_id ET nav_date ; garder les lignes absentes et l’heure de référence.

- Une version fournisseur alimente plusieurs calculs — 1 → plusieurs ; source parfois absente. Comparer consumed_source_version à source_version ; compter les calculation_id séparément des fund_id. La jointure actuelle par fund_id est limitée au snapshot à date unique.

## 3 · Couche sémantique : définitions réutilisables

### VL attendues en retard et non reçues

Nombre de lignes de fund_freshness dont arrival_status = MISSING, au 20/10/2026 à 10:00 UTC.

**Unité :** fonds/date. **Grain :** fund_id + nav_date

**Limite :** WAITING, NOT_EXPECTED et LATE_RECEIVED ne sont pas des absences encore en retard.

### Taux d’absences en retard

100 × MISSING / nombre de lignes expected = 1. Le calendrier donne le dénominateur ; ne pas compter les lignes de calcul.

**Unité :** % des VL attendues. **Grain :** population et heure filtrées

**Limite :** Dénominateur nul = NULL ; pas de rafraîchissement live implicite.

### Calculs candidats et fonds concernés

COUNT DISTINCT calculation_id, puis COUNT DISTINCT fund_id, limités à RECOMPUTE_CANDIDATE. Deux mesures de grains différents.

**Unité :** calculs / fonds distincts. **Grain :** calculation_id pour les calculs, fund_id pour les fonds

**Limite :** Ce sont des candidats à examiner ; aucune exécution ni fermeture transitive du graphe.

## 4 · SQL reproductible

### SB0

```sql
-- Deux raccourcis volontairement insuffisants : absence = incident ; ligne jointe = fonds.
SELECT
  (SELECT COUNT(*) FROM {{ns}}fund_expectations e
   LEFT JOIN {{ns}}fund_observations o ON e.fund_id = o.fund_id AND e.nav_date = o.nav_date
   WHERE o.fund_id IS NULL) AS absent_observations,
  (SELECT COUNT(*) FROM {{ns}}fund_expectations e
   LEFT JOIN {{ns}}calculation_state c ON e.fund_id = c.fund_id) AS joined_rows;
```

### SB1

```sql
-- Grain fonds/date ; le calendrier et l'heure figée définissent le retard ouvert.
SELECT COUNT(*) AS population,
       COUNT(CASE WHEN expected = 1 THEN 1 END) AS expected_funds,
       COUNT(CASE WHEN arrival_status = 'MISSING' THEN 1 END) AS overdue_missing,
       COUNT(CASE WHEN arrival_status = 'WAITING' THEN 1 END) AS waiting_funds,
       COUNT(CASE WHEN arrival_status = 'NOT_EXPECTED' THEN 1 END) AS not_expected_funds,
       COUNT(CASE WHEN arrival_status = 'LATE_RECEIVED' THEN 1 END) AS late_received_funds,
       100.0 * COUNT(CASE WHEN arrival_status = 'MISSING' THEN 1 END)
         / NULLIF(COUNT(CASE WHEN expected = 1 THEN 1 END), 0) AS overdue_pct
FROM {{ns}}fund_freshness;
```

### SB2

```sql
-- Grain calcul : plusieurs calculs peuvent concerner le même fonds.
-- Le candidat doit être examiné ; cette requête ne déclenche aucun recalcul.
SELECT COUNT(DISTINCT calculation_id) AS calculations,
       COUNT(DISTINCT CASE WHEN calculation_status = 'RECOMPUTE_CANDIDATE' THEN calculation_id END) AS recompute_candidates,
       COUNT(DISTINCT CASE WHEN calculation_status = 'RECOMPUTE_CANDIDATE' THEN fund_id END) AS affected_funds,
       COUNT(DISTINCT CASE WHEN calculation_status = 'WAIT_SOURCE' THEN calculation_id END) AS waiting_calculations
FROM {{ns}}calculation_review;
```

## 5 · Même définition dans Genie et l’app

À 10:00 UTC le 20 octobre 2026, utilise fund_freshness pour compter les VL MISSING parmi celles expected = 1, avec dénominateur et taux. Explique pourquoi WAITING, NOT_EXPECTED et LATE_RECEIVED ne désignent pas la même situation. Avec calculation_review, donne séparément le nombre de calculation_id distincts RECOMPUTE_CANDIDATE et de fund_id distincts concernés. Montre les SQL, clés, grains et versions. Ne compte pas les lignes d’une jointure un-à-plusieurs comme des fonds.

Joindre le modèle fonds → échéance → observation → calcul, SB1/SB2 et le SQL Genie. Builder doit lire les statuts des vues communes, séparer les compteurs fonds/calculs et montrer la preuve de version. Réutiliser les définitions ; ne pas créer une nouvelle règle « NULL = incident ».

## 6 · Démontrer le bénéfice et sa limite

Montrer un faux incident évité, un chemin d’impact expliqué et deux compteurs de grains différents. Tester aussi la limite : changer le calendrier change la définition attendue ; le modèle ne décide pas du calendrier à la place du métier.

Un modèle partagé ne répare pas une source, ne prouve pas une cause, ne garantit pas les réponses de l’IA et ne remplace pas les droits. Il demande un propriétaire métier, des tests de grain/jointure et une version. Les bénéfices mesurés ici concernent les décisions sur ce petit jeu ; aucun gain de performance, de coût ou de précision générale n’est annoncé.
