# B · Données de fonds

## Votre décision

Quelles VL attendues manquent réellement, et quels résultats calculés doivent être revus après une nouvelle version fournisseur ?

Prioriser les relances fournisseur et les candidats au recalcul, tout en distinguant un retard résolu, une attente normale et une vraie absence.

Vérifiez le calendrier du fonds, puis suivez la version de la VL jusqu’au calcul qui l’a consommée.

## Sources et règles

Version harvest-lab-2026-11-16-v1 ; snapshot pédagogique immuable au 2026-10-20 10:00:00 UTC. Aucun rafraîchissement automatique. Tous les montants contractuels sont des entiers en centimes EUR ; afficher /100 en euros sans mélanger les estimations. Dates ISO et heures UTC ; aucune date courante implicite. Clés uniques vérifiées localement ; pas de données personnelles. Une valeur NULL signifie preuve absente et ne vaut jamais zéro. Les vues fournies définissent les indicateurs de référence ; réutiliser leur logique. Le modèle pédagogique harvest-semantics-v1 décrit les objets, clés et relations. Les statuts des vues SQL et les métriques SA1/SA2/SB1/SB2 sont les définitions communes de l’exercice. Une ontologie ou couche sémantique client exige son propre mapping, propriétaire et attendus. Accès pédagogique au niveau des objets, sans promesse de RLS ni de masque. Le mode d’identité réel doit être constaté avant la génération et lors de la publication.

Sources : {{ns}}fund_expectations (une ligne par fund_id/nav_date), {{ns}}fund_observations (zéro ou une ligne par même clé), {{ns}}calculation_state (une ligne par calculation_id) ; vues {{ns}}fund_freshness et {{ns}}calculation_review. Six fonds fictifs ; trois observations et six calculs. Jointure attentes LEFT JOIN observations sur fund_id ET nav_date pour conserver les absences. Snapshot à date unique : fund_id est unique dans fund_freshness, nécessaire à la jointure des calculs. Heure figée : 2026-10-20 10:00:00 UTC. expected=0 → NOT_EXPECTED ; observation absente à échéance passée → MISSING ; avant échéance → WAITING ; reçue après échéance → LATE_RECEIVED, sinon ON_TIME. Une VL inchangée ne suffit pas à prouver une erreur. nav_eur/previous_nav_eur sont des EUR/part ; daily_return_pct = 100 × (VL/VL précédente − 1), seulement avec preuve reçue et dénominateur positif. Aucune performance agrégée de portefeuille. Calcul : version fournisseur supérieure à la version consommée → RECOMPUTE_CANDIDATE ; version égale → CURRENT ; source absente → WAIT_SOURCE ; version inférieure → VERSION_CONFLICT. Dépendances directes préparées, sans graphe transitif ni exécution de recalcul. output_value reste le résultat antérieur avec son unité ; ne pas mélanger score et pourcentage.

## 1. Enquêter avec Genie

1. Au 20 octobre 2026 à 10:00 UTC, quelles VL attendues sont réellement manquantes ? Compare le calendrier aux observations avec une jointure qui conserve les absences. Montre le SQL et explique les statuts.
2. Quels calculs ont consommé une version antérieure à la dernière version reçue, lesquels restent à jour et lesquels attendent une source ? Donne les calculation_id et les versions.
3. Une VL constante ou une absence avant midi signifie-t-elle un incident ? Explique F002, F004, F005 et F006 ; distingue retard historique et absence encore ouverte.

Conserver la conversation, le SQL, l’heure de référence, les clés de jointure, la liste des absences, les versions de chaque calcul et les incertitudes. Valider le calendrier avec le métier. Ajouter ces éléments au prompt Builder, sans ajouter de réponse attendue cachée à Genie. Joindre le modèle fonds → échéance → observation → calcul, SB1/SB2 et le SQL Genie. Builder doit lire les statuts des vues communes, séparer les compteurs fonds/calculs et montrer la preuve de version. Réutiliser les définitions ; ne pas créer une nouvelle règle « NULL = incident ».

## 2. Construire

```text
J’examine les données de fonds pour Harvest. Dans l’App Space {{app_space_url}}, construis en français « Fraîcheur et impact des VL », une app en lecture seule. Inspecte {{ns}}fund_expectations (fund_id, nav_date, expected, deadline_utc, calendar_note), {{ns}}fund_observations (fund_id, nav_date, nav_eur, previous_nav_eur, received_at_utc, source_version, source_file), {{ns}}calculation_state (fund_id, calculation_id, consumed_source_version, output_value, output_unit), et les vues {{ns}}fund_freshness / {{ns}}calculation_review. Si un objet manque ou est interdit, signale-le sans inventer de colonnes ni fournir de fixture. Jeu harvest-lab-2026-11-16-v1, date unique 20/10/2026, observation figée à 10:00 UTC. Attentes LEFT JOIN observations sur fund_id et nav_date ; ne pas perdre les lignes absentes. Réutilise arrival_status, daily_return_pct et calculation_status des vues. Une VL constante n’est pas automatiquement une erreur ; une absence avant échéance n’est pas un incident ; un retard reçu est résolu du point de vue arrivée. EUR/part pour les VL ; rendement quotidien en %, NULL si preuve ou dénominateur manque. Ne pas moyenner ces rendements pour prétendre calculer une performance portefeuille. Inclure trois vues : calendrier attendu/reçu, détail fonds avec source et versions, liste des calculs à revoir avec sortie antérieure et unité. Compter DISTINCT calculation_id après toute jointure ; conserver les dénominateurs. Répondre : qui relancer, quels calculs examiner, quelle preuve manque ? Aucun recalcul réel, interpolation de VL ou modification fournisseur. Tout contrôle hypothétique porte « Simulation — non enregistrée ». Identité de lecture constatée : non-verifie ; demander confirmation si non vérifiée. Afficher l’identité effective fournie par la plateforme, avec contrôles serveur réels et filtres paramétrés. Prévoir chargement, vide, échec SQL, accès refusé, et unités/as-of visibles. Utiliser les logos officiels fournis. Comparer les mêmes filtres à B1/B2/B3 sans coder les résultats en dur. Livrer aperçu, requêtes, hypothèses et procédure de preuve. Utiliser notre enquête Genie validée jointe comme contrat. Modèle métier pédagogique harvest-semantics-v1 : joindre le modèle du parcours et les SQL SB1/SB2 validés. Ajouter un panneau « Pourquoi ce chiffre ? » avec définition, unité, grain, dénominateur, source et filtre. Réutiliser les statuts des vues SQL citées ; aucune classification métier recodée dans le navigateur. Inspecter la correspondance entre les objets du modèle et les colonnes réelles. Ne pas supposer que des metric views natives ou un moteur de graphe sont déployés.
```

## 3. Améliorer

```text
Conserve notre app Harvest Fraîcheur et impact des VL. Lis nos observations réellement consignées (B1/B2/B3, SQL Genie, captures, identité et version de l’app). S’il manque une preuve, demande-la ; n’invente pas d’écart. Corrige les différences observées sur harvest-lab-2026-11-16-v1 à 10:00 UTC. Vérifie que la jointure conserve F003 sans observation, que F004 sans VL attendue et F005 avant midi ne deviennent pas de faux incidents, que F002 constant reste ON_TIME et que F006 reçu tard reste LATE_RECEIVED. Présente les candidats au recalcul par calculation_id avec version consommée et source, sans annoncer qu’ils ont été recalculés. Affiche la sortie antérieure et son unité ; ne confonds pas score de risque et rendement. Ajoute F999 sans résultat, erreur SQL visible et refus d’accès testé avec le compte prévu par l’animateur, sans remplacement silencieux. Les rendements vérifiables viennent de B1 et restent séparés des sorties historiques ; aucune estimation fournisseur. Améliore les libellés avec le métier. Fournis la nouvelle version et le registre de comparaison SQL/Genie/app avec échecs et limites. Une app publiée doit être contrôlée séparément de l’aperçu. Comparer les indicateurs aux définitions SB1/SB2 du mini-lab, sans copier les constantes du résultat. Tester une ambiguïté de vocabulaire et une limite de grain ou de NULL. Montrer la définition partagée et la trace jusqu’à la source. Si les deux lectures sont déjà correctes, consigner cette convergence ; ne pas inventer une amélioration ni un gain de précision.
```

## 4. Vérifier

- Versions et rendements : F001 : 2 % de rendement quotidien observé ; F006 : 1 %. Trois RECOMPUTE_CANDIDATE (deux F001, un F006), un CURRENT, deux WAIT_SOURCE ; six identifiants uniques.
- Donnée jamais arrivée : F003 : MISSING et rendement NULL ; conservé par LEFT JOIN. Deux calculs WAIT_SOURCE.
- Faux positifs et retard résolu : F002 constant : ON_TIME ; F004 : NOT_EXPECTED ; F005 : WAITING ; F006 : LATE_RECEIVED, distinct d’une absence ouverte.
- Population vide : F999 : 0 fonds et rendement NULL, message explicite ; pas de graphique ni moyenne artificielle.
- Identités autorisée/refusée : Compte participant autorisé : lecture des cinq objets. Compte de contrôle : refus de lecture attendu avec accès au workspace/warehouse. Contrôler séparément SQL, Genie et app publiée, en enregistrant l’identité effective ; les lectures par SP partagé ne démontrent pas l’isolation entre utilisateurs.
- Ontologie et définition réutilisée : SB0 : 3 absences et 8 lignes jointes ; SB1 : 1 MISSING parmi 5 attendus ; SB2 : 3 calculs candidats sur 2 fonds. Expliquer F003/F005 et le grain, sans annoncer un recalcul.

### B1

```sql
SELECT fund_id, nav_date, arrival_status, received_at_utc, deadline_utc, daily_return_pct
FROM {{ns}}fund_freshness
ORDER BY fund_id;
```


### B2

```sql
SELECT calculation_id, consumed_source_version, source_version, calculation_status, output_value, output_unit
FROM {{ns}}calculation_review
ORDER BY calculation_id;
```


### B3

```sql
SELECT COUNT(*) AS funds, AVG(daily_return_pct) AS unweighted_return_pct
FROM {{ns}}fund_freshness
WHERE fund_id = 'F999';
```

## 5. Présenter

Préparez une restitution d’une minute. Montrez une preuve issue de vos deux cas, expliquez une limite et proposez le prochain test. Exportez votre suivi et, si vous l’avez renseigné, votre carnet de mission.

## Si bloqué

Si Genie manque, utiliser B1/B2/B3 dans SQL et noter Genie BLOCKED. Si Builder manque, produire le contrat et observer une app autorisée ; construction BLOCKED. Hors ligne, analyser les attentes et CSV ; ne pas convertir cette observation en réussite de contrôle live.

## Extension

Extension native : examiner semantic/metric-views.sql avec l’animateur, confirmer la disponibilité et les droits, puis déployer après revue. Comparer MEASURE() aux SQL sémantiques. Après l’atelier : arbre transitif de dépendances, correction fournisseur versionnée, exécution sélective et comparaison numérique avec une référence Harvest. Ni parité MATLAB, ni gain de performance, ni SLA n’est démontré par ce jeu.


## Fonds · distinguer l’absence de l’incident

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
