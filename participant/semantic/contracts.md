# Contrats · convertir n’est pas préserver

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
