# Harvest — carnet de décisions

Préparez une restitution d’une minute. Montrez une preuve issue de vos deux cas, expliquez une limite et proposez le prochain test. Exportez votre suivi et, si vous l’avez renseigné, votre carnet de mission.

## A · Agrégation de contrats

### Mon nom et mon essai

À compléter

### Décision et périmètre retenus

À compléter

### Identité effective SQL / Genie / app et mode de lecture

À compléter

### Conversation Genie : URL, question et résultat

À compléter

### SQL exécuté, filtres, date et résultats inspectés

À compléter

### Contrat validé et incertitudes

À compléter

### App : URL, aperçu ou publication, version

À compléter

### Écarts réellement observés et retour métier pour le second prompt

À compléter

### Comparaison SQL / Genie / app, accès autorisé/refusé, liens de preuve

À compléter

### Décision proposée et principale limite

À compléter

### Responsable et prochain jalon daté

À compléter

### Ontologie : objet, relation, clé et ambiguïté levée

À compléter

### Métrique partagée : définition, avant/après, preuve et propriétaire

À compléter

| Test | Attendu | Statut | Preuve / limite |
|---|---|---|---|
| A-normal | A1/A2 : six contrats ; trois PRESERVED. Somme fournisseur de ces trois = 14 600,25 €. Écart C002 = −43 470,00 € ; ce n’est pas une perte financière prouvée. | NOT RUN | |
| A-missing | C004 : SOURCE_INCOMPLETE et montant inconnu ; C003 : CONVERSION_FAILED. Aucune imputation à zéro, aucune cause inventée. | NOT RUN | |
| A-counter | C005 : PRESERVED malgré une estimation de 8 250 € contre 8 000 € fournisseur. L’estimation ne remplace pas la valeur contractuelle. | NOT RUN | |
| A-empty | P99 : compteur 0, somme NULL, message explicite et filtres conservés. | NOT RUN | |
| A-access | Le compte participant autorisé lit les deux objets. Un compte de contrôle peut accéder au workspace/warehouse mais pas à ces objets. Répéter sur Genie et l’app publiée, avec l’identité effective enregistrée ; un SP partagé ne prouve pas une séparation par utilisateur. | NOT RUN | |
| A-semantics | SA0 compte 4 normalisés ; SA1 compte 3 conservés et 14 600,25 € fournisseur. C005 reste conservé. Même définition dans SQL, Genie et app ; cause et autorisation de livraison non déduites. | NOT RUN | |
## B · Données de fonds

### Mon nom et mon essai

À compléter

### Décision et périmètre retenus

À compléter

### Identité effective SQL / Genie / app et mode de lecture

À compléter

### Conversation Genie : URL, question et résultat

À compléter

### SQL exécuté, filtres, date et résultats inspectés

À compléter

### Contrat validé et incertitudes

À compléter

### App : URL, aperçu ou publication, version

À compléter

### Écarts réellement observés et retour métier pour le second prompt

À compléter

### Comparaison SQL / Genie / app, accès autorisé/refusé, liens de preuve

À compléter

### Décision proposée et principale limite

À compléter

### Responsable et prochain jalon daté

À compléter

### Ontologie : objet, relation, clé et ambiguïté levée

À compléter

### Métrique partagée : définition, avant/après, preuve et propriétaire

À compléter

| Test | Attendu | Statut | Preuve / limite |
|---|---|---|---|
| B-normal | F001 : 2 % de rendement quotidien observé ; F006 : 1 %. Trois RECOMPUTE_CANDIDATE (deux F001, un F006), un CURRENT, deux WAIT_SOURCE ; six identifiants uniques. | NOT RUN | |
| B-missing | F003 : MISSING et rendement NULL ; conservé par LEFT JOIN. Deux calculs WAIT_SOURCE. | NOT RUN | |
| B-counter | F002 constant : ON_TIME ; F004 : NOT_EXPECTED ; F005 : WAITING ; F006 : LATE_RECEIVED, distinct d’une absence ouverte. | NOT RUN | |
| B-empty | F999 : 0 fonds et rendement NULL, message explicite ; pas de graphique ni moyenne artificielle. | NOT RUN | |
| B-access | Compte participant autorisé : lecture des cinq objets. Compte de contrôle : refus de lecture attendu avec accès au workspace/warehouse. Contrôler séparément SQL, Genie et app publiée, en enregistrant l’identité effective ; les lectures par SP partagé ne démontrent pas l’isolation entre utilisateurs. | NOT RUN | |
| B-semantics | SB0 : 3 absences et 8 lignes jointes ; SB1 : 1 MISSING parmi 5 attendus ; SB2 : 3 calculs candidats sur 2 fonds. Expliquer F003/F005 et le grain, sans annoncer un recalcul. | NOT RUN | |
