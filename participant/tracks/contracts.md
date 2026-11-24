# A · Agrégation de contrats

## Votre décision

Quels contrats faut-il examiner avant de préparer une livraison, et quelle preuve demander au fournisseur ou au responsable du mapping ?

Produire une liste de contrats à examiner et choisir une prochaine action pour chaque motif, sans altérer les montants ni lancer une livraison.

Comparez vous-même les montants et examinez les écarts de conversion. Relevez la décision de livraison à faire valider par Harvest.

## Sources et règles

Version harvest-lab-2026-11-16-v1 ; snapshot pédagogique immuable au 2026-10-20 10:00:00 UTC. Aucun rafraîchissement automatique. Tous les montants contractuels sont des entiers en centimes EUR ; afficher /100 en euros sans mélanger les estimations. Dates ISO et heures UTC ; aucune date courante implicite. Clés uniques vérifiées localement ; pas de données personnelles. Une valeur NULL signifie preuve absente et ne vaut jamais zéro. Les vues fournies définissent les indicateurs de référence ; réutiliser leur logique. Le modèle pédagogique harvest-semantics-v1 décrit les objets, clés et relations. Les statuts des vues SQL et les métriques SA1/SA2/SB1/SB2 sont les définitions communes de l’exercice. Une ontologie ou couche sémantique client exige son propre mapping, propriétaire et attendus. Accès pédagogique au niveau des objets, sans promesse de RLS ni de masque. Le mode d’identité réel doit être constaté avant la génération et lors de la publication.

Sources : {{ns}}contract_observations et {{ns}}contract_review. Une ligne par contract_id au business_date 2026-10-20 ; six contrats, trois fournisseurs fictifs, trois familles de format. Ce snapshot résume des observations de conversion préparées ; aucun parseur de production n’est exécuté. contract_id est la clé, sans jointure nécessaire. supplier_cents = valeur fournisseur ; normalized_cents = résultat observé du mapping ; analytical_cents = estimation séparée. normalization_delta_cents = normalisé moins fournisseur. review_status : SOURCE_INCOMPLETE si fournisseur absent ; CONVERSION_FAILED si erreur ou normalisé absent ; VALUE_CHANGED si les valeurs diffèrent ; PRESERVED sinon. PRESERVED confirme seulement la conservation numérique : ce n’est pas une autorisation de livraison. Somme par statut avec nombre de montants connus ; un total incomplet reste signalé. Pas de conformité Pénélop revendiquée : custom-xml est un nom pédagogique.

## 1. Enquêter avec Genie

1. Pour le 20 octobre 2026, examine tous les contrats, sans exclure aucun statut : valeur fournisseur conservée, modifiée, source incomplète ou conversion échouée. Donne chaque contract_id, review_status, le motif, la version du mapping et la source. Montre le SQL exécuté et le nombre total de contrats couverts.
2. Quelle somme fournisseur en euros correspond aux contrats conservés, et combien de montants sont connus dans chaque catégorie ? Une estimation analytique différente doit-elle modifier ce classement ?
3. Peux-tu affirmer qu’un écart vient du fournisseur ou du mapping avec ces seules observations ? Quelles preuves manquent ? Examine C002, C004 et C005 sans inventer de correction.

Enregistrer le lien de conversation, le SQL exécuté, les identifiants et les sommes obtenus, les colonnes vérifiées, l’identité de lecture et l’incertitude sur la cause. Validez la distinction fournisseur/normalisé/estimation avant d’ouvrir Builder. Joindre le modèle métier, le contrat de métriques, SA1/SA2 et les preuves Genie. Builder doit réutiliser review_status et la définition fournisseur, afficher la définition des indicateurs et une trace contrat → source → mapping. Les constantes des résultats du mini-lab ne doivent pas entrer dans le prompt.

## 2. Construire

```text
Je vérifie la conversion des contrats chez Harvest. Dans l’App Space {{app_space_url}}, construis une application en français nommée « Revue des conversions », en lecture seule. Sources confirmées : {{ns}}contract_observations (contract_id, business_date, provider_id, format_family, source_file, mapping_version, supplier_cents, normalized_cents, analytical_cents, conversion_error) et {{ns}}contract_review (mêmes colonnes, review_status, normalization_delta_cents). Inspecte d’abord les schémas et les droits ; arrête et explique toute source inaccessible ou colonne manquante. Aucun jeu de remplacement ni réponse AI prédéfinie. Jeu harvest-lab-2026-11-16-v1, arrêté au 20/10/2026 ; une ligne par contrat, EUR en centimes, valeurs manquantes NULL. Réutilise review_status tel que défini dans la vue. Les faits fournisseur restent autoritatifs ; l’estimation analytique est une colonne séparée. Une valeur PRESERVED n’autorise pas la livraison. Affiche : répartition par motif avec dénominateur, somme des montants fournisseur connus par motif et couverture, filtre fournisseur, liste des contrats, détail des valeurs et lien logique au fichier/source/version. Réponds à trois questions : quels contrats examiner, quel montant connu est concerné, quelle preuve demander ensuite ? Inclure chargement, population vide, erreur de requête et refus d’accès ; ne pas remplacer un échec par des données synthétiques locales. Identité de lecture constatée : non-verifie. Si elle n’est pas vérifiée, demander cette information avant de générer les accès. Afficher l’identité effective issue de la plateforme ; aucun sélecteur de rôle ne donne de droits. Paramétrer les filtres, protéger l’accès serveur, ne modifier aucune source. Aucun bouton publier/corriger/approuver. Les hypothèses éventuelles sont « Simulation — non enregistrée ». Utiliser les logos officiels fournis et une mise en page lisible au clavier. Vérifier la même population avec A1, A2 et A3, sans coder leurs résultats en dur. Livrer un aperçu fonctionnel, les hypothèses, les requêtes et la procédure de vérification. Intégrer uniquement les résultats et le contrat effectivement validés dans notre conversation Genie jointe. Modèle métier pédagogique harvest-semantics-v1 : joindre le modèle du parcours et les SQL SA1/SA2 validés. Ajouter un panneau « Pourquoi ce chiffre ? » avec définition, unité, grain, dénominateur, source et filtre. Réutiliser les statuts des vues SQL citées ; aucune classification métier recodée dans le navigateur. Inspecter la correspondance entre les objets du modèle et les colonnes réelles. Ne pas supposer que des metric views natives ou un moteur de graphe sont déployés. Définir la complétude fournisseur comme 100 × COUNT(supplier_cents) / COUNT(*), tous statuts inclus dans les filtres ; afficher les deux comptes. La distinguer du taux de conservation et de la part conservée des montants connus.
```

## 3. Améliorer

```text
Conserve notre application Harvest Revue des conversions et son contrat de données. Lis d’abord les écarts effectivement enregistrés dans notre carnet (SQL A1/A2/A3, conversation Genie, capture ou version de l’app) ; demande les observations manquantes, sans inventer de constat. Sur harvest-lab-2026-11-16-v1, même identité, fournisseur et date, corrige chaque différence mesurée avec le SQL de référence. Ajoute des contrôles : fournisseur P99 sans résultat, C004 sans montant fournisseur, C002 avec normalisé différent, C005 avec estimation différente mais fournisseur conservé. Préserve NULL et affiche la couverture des sommes ; une somme fournisseur absente n’est pas 0 €. Montre la valeur fournisseur, normalisée et analytique séparément, avec écart signé, source et mapping. Si la cause n’est pas démontrée, afficher « cause à confirmer ». Ajoute un message explicite en cas de refus de lecture et vérifie la route avec l’identité prévue par l’animateur ; aucun repli vers une fixture. Intègre les retours de lisibilité du métier. Aucun changement de valeur, publication ni succès de sauvegarde métier. Fournis la nouvelle version, les modifications et un registre des tests observés, échecs compris. Une case cochée dans le carnet n’exécute pas un test de la plateforme. Comparer les indicateurs aux définitions SA1/SA2 du mini-lab, sans copier les constantes du résultat. Tester une ambiguïté de vocabulaire et une limite de grain ou de NULL. Montrer la définition partagée et la trace jusqu’à la source. Si les deux lectures sont déjà correctes, consigner cette convergence ; ne pas inventer une amélioration ni un gain de précision. Vérifier explicitement le numérateur et le dénominateur de la complétude fournisseur ; le mot « couverture » seul ne suffit pas.
```

## 4. Vérifier

- Population et valeurs normales : A1/A2 : six contrats ; trois PRESERVED. Somme fournisseur de ces trois = 14 600,25 €. Écart C002 = −43 470,00 € ; ce n’est pas une perte financière prouvée.
- Preuve manquante : C004 : SOURCE_INCOMPLETE et montant inconnu ; C003 : CONVERSION_FAILED. Aucune imputation à zéro, aucune cause inventée.
- Contre-exemple : C005 : PRESERVED malgré une estimation de 8 250 € contre 8 000 € fournisseur. L’estimation ne remplace pas la valeur contractuelle.
- Filtre sans ligne : P99 : compteur 0, somme NULL, message explicite et filtres conservés.
- Identités autorisée/refusée : Le compte participant autorisé lit les deux objets. Un compte de contrôle peut accéder au workspace/warehouse mais pas à ces objets. Répéter sur Genie et l’app publiée, avec l’identité effective enregistrée ; un SP partagé ne prouve pas une séparation par utilisateur.
- Ontologie et définition réutilisée : SA0 compte 4 normalisés ; SA1 compte 3 conservés et 14 600,25 € fournisseur. C005 reste conservé. Même définition dans SQL, Genie et app ; cause et autorisation de livraison non déduites.

### A1

```sql
SELECT review_status, COUNT(*) AS contracts,
       COUNT(supplier_cents) AS known_amounts,
       SUM(supplier_cents) / 100.0 AS supplier_eur
FROM {{ns}}contract_review
WHERE business_date = '2026-10-20'
GROUP BY review_status
ORDER BY review_status;
```


### A2

```sql
SELECT contract_id, supplier_cents, normalized_cents, analytical_cents,
       normalization_delta_cents, source_file, mapping_version, review_status
FROM {{ns}}contract_review
WHERE business_date = '2026-10-20'
ORDER BY contract_id;
```


### A3

```sql
SELECT COUNT(*) AS contracts, SUM(supplier_cents) / 100.0 AS supplier_eur
FROM {{ns}}contract_review
WHERE business_date = '2026-10-20' AND provider_id = 'P99';
```

## 5. Présenter

Préparez une restitution d’une minute. Montrez une preuve issue de vos deux cas, expliquez une limite et proposez le prochain test. Exportez votre suivi et, si vous l’avez renseigné, votre carnet de mission.

## Si bloqué

Si Genie est indisponible, travailler sur A1/A2/A3 dans SQL et marquer Genie BLOCKED. Si Builder manque, rédiger le contrat et observer une app autorisée ; marquer la construction BLOCKED. L’observation ne valide pas une réalisation pratique. Hors ligne, lire les CSV et le guide ; les contrôles live restent NOT RUN.

## Extension

Extension native : examiner semantic/metric-views.sql avec l’animateur, confirmer la disponibilité et les droits, puis déployer après revue. Comparer MEASURE() aux SQL sémantiques. Après l’atelier seulement : remplacer le snapshot par un vrai mapping anonymisé avec entrée, sortie attendue, version et preuve d’équivalence ; définir le traitement des consommateurs de fichiers entiers. Le rejeu et la livraison idempotente nécessitent un atelier distinct.


## Contrats · convertir n’est pas préserver

Laboratoire local sur le snapshot synthétique au 20/10/2026 à 10:00 UTC. Les comparaisons sont calculées par les SQL fournis lors du build, pas par une requête live du portail. Les raccourcis sont des hypothèses pédagogiques explicites, pas des erreurs attribuées à Genie.

## 1 · Prédire, puis comparer

Avant de révéler les résultats, prédisez : un montant normalisé prouve-t-il que la valeur fournisseur a été conservée ? Quel montant faut-il additionner ?

1. 2 min · Le métier propose le sens de « conservé ». L’IT prédit le résultat de SA0 sans exécuter SA1.

2. 3 min · Explorez C002, C004 et C005. Nommez le contrat, le fournisseur, la version du mapping et les trois valeurs. Choisissez une relation et sa clé.

3. 3 min · Comparez SA0 et SA1, puis SA2. Expliquez le contrat qui change de catégorie et le montant retenu. Consignez une limite.

4. 4 min · Posez la question à Genie avec la définition ci-dessous. Comparez son SQL à SA1, sans lui donner les résultats chiffrés.

5. 8 min · Complétez l’enquête Genie, inspectez la couverture et validez le contrat destiné à Builder.

## 2 · Ontologie : objets et relations

### Fournisseur

L’émetteur de la valeur contractuelle ; il ne définit pas l’estimation analytique.

**Grain / clé :** Une identité provider_id.

**Source :** {{ns}}contract_observations.provider_id ; objet logique, sans table fournisseur dédiée.

### Contrat

L’objet dont on veut préserver la valeur, observé à une date métier.

**Grain / clé :** Un contract_id dans ce snapshot à date unique ; une évolution multi-date exigerait contract_id + business_date.

**Source :** {{ns}}contract_observations → {{ns}}contract_review

### Conversion observée

La valeur normalisée et l’erreur éventuelle, avec une version du mapping. Une observation ne prouve pas la cause.

**Grain / clé :** Une observation par contrat/date dans ce jeu ; pas d’historique d’exécutions.

**Source :** {{ns}}contract_observations.mapping_version, normalized_cents, conversion_error

### Valeur & estimation

Trois rôles différents : fournisseur autoritatif, normalisé à comparer, estimation analytique indépendante.

**Grain / clé :** Trois attributs en centimes EUR ; NULL = preuve absente, jamais zéro.

**Source :** supplier_cents / normalized_cents / analytical_cents

- Un fournisseur émet des contrats — 1 → plusieurs. provider_id identifie le fournisseur de chaque contrat.

- Un contrat possède une observation de conversion — 1 → 1 dans le snapshot. contract_id ; rattacher mapping_version et source_file, sans inventer un historique.

- La conversion compare des valeurs de rôles distincts — 1 → 3 rôles, chacun nullable. PRESERVED compare fournisseur et normalisé ; l’estimation ne participe pas à ce statut.

## 3 · Couche sémantique : définitions réutilisables

### Contrats conservés

Nombre de lignes dont review_status = PRESERVED. Le statut exige un montant fournisseur connu, aucune erreur, un normalisé connu et identique.

**Unité :** contrats. **Grain :** contract_id, même date et filtres

**Limite :** Une conservation numérique n’autorise pas une livraison.

### Montant fournisseur conservé

Somme de supplier_cents pour PRESERVED, divisée par 100. Les valeurs analytiques ne remplacent pas les valeurs fournisseur. La complétude fournisseur est 100 × COUNT(supplier_cents) / COUNT(*) sur tous les statuts, distincte du taux de conservation.

**Unité :** EUR. **Grain :** contrat puis agrégation selon le filtre

**Limite :** Somme d’une population vide = NULL ; montrer le nombre de montants connus.

### Taux de conservation

100 × nombre conservé / nombre total de contrats. Réagréger numérateur et dénominateur ; ne pas moyenner les taux fournisseurs.

**Unité :** %. **Grain :** population filtrée

**Limite :** Dénominateur nul = NULL. Une exclusion de statut change la question.

## 4 · SQL reproductible

### SA0

```sql
-- Hypothèse volontairement insuffisante : « normalisé » veut dire « conservé ».
-- Ce SQL décrit une lecture possible, pas un échec mesuré de Genie.
SELECT COUNT(*) AS population,
       COUNT(normalized_cents) AS treated_as_preserved,
       SUM(normalized_cents) / 100.0 AS normalized_eur
FROM {{ns}}contract_observations;
```

### SA1

```sql
-- Définition commune : statut gouverné par contract_review ; montant fournisseur.
SELECT COUNT(*) AS population,
       COUNT(CASE WHEN review_status = 'PRESERVED' THEN 1 END) AS preserved_contracts,
       100.0 * COUNT(CASE WHEN review_status = 'PRESERVED' THEN 1 END)
         / NULLIF(COUNT(*), 0) AS preservation_pct,
       SUM(CASE WHEN review_status = 'PRESERVED' THEN supplier_cents END) / 100.0 AS preserved_supplier_eur,
       COUNT(supplier_cents) AS known_supplier_amounts,
       100.0 * COUNT(supplier_cents) / NULLIF(COUNT(*), 0) AS supplier_coverage_pct,
       SUM(supplier_cents) / 100.0 AS known_supplier_eur
FROM {{ns}}contract_review;
```

### SA2

```sql
-- Réutiliser la même définition au grain fournisseur, sans moyenner les taux.
SELECT provider_id, COUNT(*) AS population,
       COUNT(CASE WHEN review_status = 'PRESERVED' THEN 1 END) AS preserved_contracts,
       100.0 * COUNT(CASE WHEN review_status = 'PRESERVED' THEN 1 END)
         / NULLIF(COUNT(*), 0) AS preservation_pct,
       SUM(CASE WHEN review_status = 'PRESERVED' THEN supplier_cents END) / 100.0 AS preserved_supplier_eur
FROM {{ns}}contract_review
GROUP BY provider_id
ORDER BY provider_id;
```

## 5 · Même définition dans Genie et l’app

Utilise contract_review pour définir « conservé » comme review_status = PRESERVED, sans utiliser l’estimation analytique. Sur le 20 octobre 2026, donne la population totale, le nombre conservé, le taux sur tous les contrats et la somme fournisseur conservée en euros, avec la complétude des montants fournisseur. Définition de supplier_coverage_pct : 100 × COUNT(supplier_cents) / COUNT(*), sur tous les contrats du périmètre, tous statuts inclus ; donne aussi le numérateur et le dénominateur. Ce taux de complétude est distinct du taux de conservation et de la part des montants connus conservés. Décline ensuite par fournisseur. Montre le SQL, les unités et les sources. Pourquoi un normalisé non NULL ne suffit-il pas ? N’invente pas de cause ni d’autorisation de livraison. Définition exacte de preserved_supplier_eur : SUM(CASE WHEN review_status = 'PRESERVED' THEN supplier_cents END) / 100.0. Si aucun contrat conservé ne possède de montant connu dans le groupe, la somme reste NULL, jamais 0 : aucun ELSE 0 ni COALESCE sur cette somme. Limite la sortie aux métriques définies ci-dessus ; ne crée pas de taux supplémentaire.

Joindre le modèle métier, le contrat de métriques, SA1/SA2 et les preuves Genie. Builder doit réutiliser review_status et la définition fournisseur, afficher la définition des indicateurs et une trace contrat → source → mapping. Les constantes des résultats du mini-lab ne doivent pas entrer dans le prompt.

## 6 · Démontrer le bénéfice et sa limite

Montrer une ambiguïté éliminée, un contre-exemple (C002 ou C005), la même définition dans deux surfaces et un propriétaire pour la règle. Le gain est une décision plus cohérente et explicable, pas une hausse annoncée du taux de réussite du modèle. Faites nommer le numérateur et le dénominateur de « couverture » : la complétude fournisseur et la part conservée des montants connus répondent à deux questions différentes.

Un modèle partagé ne répare pas une source, ne prouve pas une cause, ne garantit pas les réponses de l’IA et ne remplace pas les droits. Il demande un propriétaire métier, des tests de grain/jointure et une version. Les bénéfices mesurés ici concernent les décisions sur ce petit jeu ; aucun gain de performance, de coût ou de précision générale n’est annoncé.
