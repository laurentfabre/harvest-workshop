# Harvest × Databricks · Des positions aux valeurs de fonds

**24 novembre 2026 · Paris · 14 h – 17 h · Français**

[**Ouvrir le studio de l’atelier**](https://laurentfabre.github.io/harvest-workshop/) · [Télécharger le kit participant](https://laurentfabre.github.io/harvest-workshop/harvest-participant.zip) · [Notebook de démarrage](participant/notebooks/00_DEMARRER.ipynb) · [Petit lot ERES](eres/20261123_HARVEST.zip)

Extrayez le kit, ouvrez `index.html` et choisissez votre prénom. Le premier cas suit les positions ERES du fichier fournisseur à la situation publiée. Le second examine les échéances des fonds et les calculs qui dépendent d’une valeur liquidative.

## Démarrer dans son essai

1. Depuis le studio, ouvrez **Préparer mon essai**. Utilisez votre compte dans le workspace Harvest ou Avanade.
2. Déposez le petit ZIP dans un volume accessible, puis importez `notebooks/00_DEMARRER.ipynb` dans votre workspace. Le widget `archive` reçoit le chemin du ZIP et `equipe` votre code personnel.
3. Dans **Mes accès** du second cas, collez le reçu du notebook pour préremplir votre catalogue et votre schéma. Complétez les liens de votre essai et appliquez les paramètres.
4. Suivez les étapes dans votre navigateur. **Consigner ma preuve** vous ramène au point de reprise. **Ma restitution** affiche vos observations et statuts pour les deux cas.
5. Exportez votre suivi pour le restaurer en changeant de navigateur ou en passant du site au kit extrait. Le carnet détaillé de Market Data dispose de son propre export.

Le kit fournit les huit profils nommés de la séance, leurs rôles, deux lots adaptés et leurs résultats de référence. Les questions Genie, l’exécution SQL et la construction des apps s’effectuent dans votre essai. Le portail garde localement les statuts que vous déclarez.

## Reproduire les supports

Avec Python 3.11 ou ultérieur, depuis la racine du projet :

```sh
python3 scripts/build.py
python3 scripts/verify_semantics.py
python3 -m pip install duckdb==1.5.3
python3 scripts/verify_eres.py
python3 scripts/check_distribution.py
```

Ouvrez `participant/index.html` ou servez le dossier avec `python3 -m http.server 8000 --directory participant`. Le guide imprimable est dans `participant/guide.html`.

Les fichiers sources sont dans `content/`, `assets/`, `eres/` et `sql/`. Les deux lots adaptés permettent de reconstruire le kit sans les archives d’origine. Les tests ERES vérifient les fichiers à l’intérieur du ZIP participant et les requêtes du notebook distribué.

## Distribution sur GitHub

Les pushes et pull requests reconstruisent le kit et vérifient le modèle, les lots, le notebook et les fichiers distribués. Dans l’onglet Actions, le résultat **harvest-atelier** contient le ZIP et le notebook importable.

Pour publier le studio, activez **Settings → Pages → Source → GitHub Actions**, puis lancez manuellement **Publier le studio** depuis la branche principale. Le site contient le kit et le lien de téléchargement. Les données saisies dans le navigateur restent sur l’appareil du participant.
