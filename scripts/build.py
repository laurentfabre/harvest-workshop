"""Build the Harvest workshop from shared content; standard library only, no network."""
from pathlib import Path
import csv
import hashlib
import html
import io
import json
import sqlite3
import zipfile
from portal_template import portal_markup
from eres_kit import SOURCE as ERES_SOURCE, kit_files, preview_positions
from semantic_model import SEMANTIC_IDS, load_lab, snapshot, track_markdown, native_metric_sql, native_queries

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'participant'
VIEWS = ['contract_review', 'fund_freshness', 'calculation_review']
QUERY_IDS = ['A1', 'A2', 'A3', 'B1', 'B2', 'B3']


def read_json(path):
    return json.loads(path.read_text())


def local_database(dataset):
    db = sqlite3.connect(':memory:')
    db.row_factory = sqlite3.Row
    for name, table in dataset['tables'].items():
        cols = ', '.join(f'"{col}" {typ}' for col, typ in table['columns'])
        db.execute(f'CREATE TABLE {name} ({cols})')
        db.executemany(f'INSERT INTO {name} VALUES ({",".join("?" for _ in table["columns"])})', table['rows'])
    for name in VIEWS:
        db.execute(f'CREATE VIEW {name} AS ' + (ROOT / 'sql' / f'{name}.sql').read_text().replace('{{ns}}', ''))
    return db


def build():
    (ROOT / 'validation').mkdir(exist_ok=True)
    w = read_json(ROOT / 'content/workshop.json')
    parcours = read_json(ROOT / 'content/parcours.json')
    parcours['positions'] = preview_positions()
    data = read_json(ROOT / 'content/dataset.json')
    b = read_json(ROOT / 'content/session.example.json')
    duration_label = f"{w['duration'] // 60} heures" if w['duration'] % 60 == 0 else f"{w['duration']} min"
    sql = {x: (ROOT / 'sql' / f'{x}.sql').read_text() for x in QUERY_IDS + SEMANTIC_IDS}
    db = local_database(data)
    w['semantic_lab'] = load_lab()
    w['semantic_results'] = snapshot(db)
    results = {x: [dict(row) for row in db.execute(q.replace('{{ns}}', ''))] for x, q in sql.items()}
    assets = ['harvest.svg', 'databricks.svg', 'style.css', 'portal.js', 'experience.js', 'semantics.js', 'semantics.css', 'parcours.js', 'eres.js', 'parcours.css', 'profile-links.js', 'provenance.json', 'manrope.ttf', 'manrope-OFL.txt']
    files = {}
    def write(name, value):
        raw = value if isinstance(value, bytes) else value.encode()
        path = OUT / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
        files[name] = raw
    def j(value):
        return json.dumps(value, ensure_ascii=False, indent=2) + '\n'
    def safe_j(value):
        return json.dumps(value, ensure_ascii=False).replace('<', '\\u003c')
    def e(value):
        return html.escape(str(value))
    def bound(value):
        ns = '`' + b['catalog'] + '`.`' + b['schema'] + '`.' if b['catalog'] and b['schema'] else '{{ns}}'
        return value.replace('{{ns}}', ns).replace('{{app_space_url}}', b['app_space_url'] or '{{app_space_url}}').replace('{{identity_mode}}', b['identity_mode'])
    def p(value):
        return '<p>' + e(bound(value)) + '</p>'
    def ol(values):
        return '<ol>' + ''.join('<li>' + e(bound(x)) + '</li>' for x in values) + '</ol>'
    def code(value):
        return '<pre>' + e(bound(value)) + '</pre>'
    brand = '<header><img src="assets/harvest.svg" alt="Harvest"><img class="db" src="assets/databricks.svg" alt="Databricks"></header>'
    head = '<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Harvest — atelier pratique</title><link rel="stylesheet" href="assets/style.css"><link rel="stylesheet" href="assets/semantics.css"></head>'
    profile_context = {'edition': parcours['edition'], 'ids': [p['id'] for p in parcours['people']], 'stages': {s['id']: s['title'] for s in parcours['stages']}, 'names': {p['id']: p['name'] for p in parcours['people']}}
    profile_links = '<script id="profile-context" type="application/json">' + safe_j(profile_context) + '</script><script src="assets/profile-links.js"></script>'
    personal_head = head.replace('</head>', '<link rel="stylesheet" href="assets/parcours.css"></head>')
    return_link = '<a class="pg-return" href="index.html">← Mon parcours</a>'
    for asset in assets:
        write('assets/' + asset, (ROOT / 'assets' / asset).read_bytes())
    for name, value in kit_files(data, ROOT / 'sql').items():
        write(name, value)
    write('eres/carnet.csv', 'participant,workspace,schema,lot,identite,lues,publiees,historiques,rejetees,preuve_sql,conversation_genie,version_app,limite,decision,responsable,jalon\n')
    eres_case = (ERES_SOURCE / 'case.html').read_text()
    write('data/dataset.json', j(data))
    for name, table in data['tables'].items():
        out = io.StringIO()
        writer = csv.writer(out)
        writer.writerow([c[0] for c in table['columns']])
        writer.writerows(table['rows'])
        write('data/' + name + '.csv', out.getvalue())
    write('references.json', j({'dataset': data['version'], 'engine': 'SQLite local; exécution Databricks à vérifier séparément', 'queries': results}))
    write('session.json', j(b))
    write('workshop.json', j(w))
    write('semantic/model.json', j(w['semantic_lab']))
    write('semantic/references.json', j(w['semantic_results']))
    write('semantic/metric-views.sql', bound(native_metric_sql()))
    write('semantic/metric-queries.sql', bound(native_queries()))
    for t in w['tracks']:
        track_md = '# ' + t['label'] + '\n\n## Votre décision\n\n' + t['question'] + '\n\n' + t['decision'] + '\n\n' + t['roles'] + '\n\n## Sources et règles\n\n' + bound(w['shared_contract']) + '\n\n' + bound(t['contract']) + '\n\n## 1. Enquêter avec Genie\n\n'
        track_md += '\n'.join(str(i+1)+'. '+q for i,q in enumerate(t['questions'])) + '\n\n' + t['handoff']
        track_md += '\n\n## 2. Construire\n\n```text\n' + bound(t['prompt1']) + '\n```\n\n## 3. Améliorer\n\n```text\n' + bound(t['prompt2']) + '\n```\n\n## 4. Vérifier\n\n'
        track_md += '\n'.join('- '+c['case']+' : '+c['expected'] for c in t['checks'])
        for qid in t['sql_ids']:
            track_md += '\n\n### '+qid+'\n\n```sql\n'+bound(sql[qid])+'```\n'
        track_md += '\n## 5. Présenter\n\n'+w['presentation']+'\n\n## Si bloqué\n\n'+t['fallback']+'\n\n## Extension\n\n'+t['extension']+'\n'
        track_md += '\n\n' + track_markdown(w['semantic_lab'], t['id'], sql, bound).replace('# ', '## ', 1)
        write('tracks/'+t['id']+'.md',track_md)
        write('semantic/'+t['id']+'.md',track_markdown(w['semantic_lab'], t['id'], sql, bound))
    for qid, query in sql.items():
        write('sql/' + qid + '.sql', bound(query))
    for view in VIEWS:
        write('sql/' + view + '.sql', bound((ROOT / 'sql' / (view + '.sql')).read_text()))
    # A browser-importable notebook: sources must already be prepared by the organizer.
    notebook = '''# Databricks notebook source
# MAGIC %md
# MAGIC # Harvest — preuves SQL
# MAGIC Jeu synthétique harvest-lab-2026-11-16-v1. Lecture seule ; aucune création de table.
# MAGIC Saisir le catalogue et le schéma personnel du petit lot affichés par le notebook ERES. Les cellules suivantes affichent le SQL et son résultat.

# COMMAND ----------
import re
dbutils.widgets.text("catalog", "")
dbutils.widgets.text("schema", "")
catalog = dbutils.widgets.get("catalog")
schema = dbutils.widgets.get("schema")
assert all(re.fullmatch(r"[A-Za-z0-9_-]+", x) for x in (catalog, schema)), "Catalogue et schéma requis ; conserver les noms exacts"
ns = f"`{catalog}`.`{schema}`."
display(spark.sql("SELECT current_user() AS execution_identity"))
'''
    for qid, query in sql.items():
        notebook += '\n# COMMAND ----------\n# MAGIC %md\n# MAGIC ## ' + qid + '\n\n# COMMAND ----------\n'
        notebook += 'query = ' + repr(query) + '.replace("{{ns}}", ns)\nprint(query)\ndisplay(spark.sql(query))\n'
    write('lab.py', notebook)
    wb = '# Harvest — carnet de décisions\n\n' + w['presentation'] + '\n\n'
    for t in w['tracks']:
        wb += '## ' + t['label'] + '\n\n'
        for f in w['workbook_fields']:
            wb += '### ' + f['label'] + '\n\nÀ compléter\n\n'
        wb += '| Test | Attendu | Statut | Preuve / limite |\n|---|---|---|---|\n'
        for c in t['checks']:
            wb += f'| {c["id"]} | {c["expected"]} | NOT RUN | |\n'
    write('decision-workbook.md', wb)
    out = io.StringIO(); writer = csv.writer(out)
    writer.writerow(['participant', 'parcours', 'app_url', 'version', 'identite', 'preuve_sql', 'preuve_genie', 'preuve_app', 'limite', 'decision', 'responsable', 'prochain_jalon', 'date'])
    for t in w['tracks']:
        writer.writerow(['', t['label']] + [''] * 11)
    write('decision-workbook.csv', out.getvalue())
    write('decision-workbook.json', j({'format':'harvest-workbook-v1','version':w['version'],'dataset':data['version'],'bindings':b,'records':{}}))
    guide = head + '<body>' + brand + '<main class="guide"><div class="cover"><p>ATELIER PRATIQUE · ' + e(duration_label.upper()) + ' · FR</p><h1>' + e(w['title']) + '</h1>' + p(w['outcome']) + '</div>'
    guide += '<div class="notice">' + e(w['disclosure']) + '</div><p class="no-print"><button onclick="print()">Imprimer / enregistrer en PDF</button> <a href="index.html">Ouvrir le portail</a></p>'
    guide += '<h2>Préparation</h2>' + p(w['audience']) + ol(w['preflight']) + p(w['surfaces']) + '<h2>Déroulé</h2><table><tr><th>Durée</th><th>Séquence</th></tr>'
    guide += ''.join('<tr><td>' + str(a['minutes']) + ' min</td><td><b>' + e(a['title']) + '</b><br>' + e(a['detail']) + '</td></tr>' for a in w['agenda']) + '</table>'
    guide += eres_case.replace('<h1 id="eres-title">', '<h2 id="eres-title">').replace('</h1>', '</h2>')
    guide += '<h2>Sources des parcours complémentaires</h2>' + p(w['shared_contract']) + '<p>Les tokens {{ns}} et {{app_space_url}} doivent être résolus avec les liens remis par l’animateur ; aucune destination implicite. Les réponses de référence sont visibles pour comparaison après votre première enquête.</p>'
    for t in w['tracks']:
        guide += '<section><h2>' + e(t['label'] + ' — ' + t['title']) + '</h2>' + p(t['question']) + p(t['decision']) + p(t['roles']) + '<h3>Sources et règles</h3>' + p(t['contract'])
        lab = w['semantic_lab']; sem = lab['tracks'][t['id']]
        guide += '<h3>Mini-lab · Ontologie et couche sémantique</h3>' + p(lab['ontology']) + p(lab['semantic_layer']) + p(lab['disclosure']) + p(sem['challenge']) + ol(sem['exercise'])
        guide += '<h3>Objets et relations</h3>' + ol([n['label'] + ' : ' + n['meaning'] + ' Grain : ' + n['grain'] + ' Source : ' + n['source'] for n in sem['entities']]) + ol([r['label'] + ' (' + r['cardinality'] + ') : ' + r['rule'] for r in sem['relations']])
        guide += '<h3>Définitions réutilisables</h3>' + ol([m['label'] + ' : ' + m['definition'] + ' Unité : ' + m['unit'] + '. Limite : ' + m['limit'] for m in sem['measures']])
        for qid in sem['sql_ids']:
            guide += '<h3>' + qid + '</h3>' + code(sql[qid])
        guide += '<h3>Question Genie avec le contrat</h3>' + p(sem['genie_prompt']) + p(sem['debrief']) + p(lab['implementation']) + p(lab['limits'])
        guide += '<h3>1 · Enquêter</h3>' + ol(t['questions']) + p(t['handoff'])
        guide += '<h3>2 · Construire</h3>' + code(t['prompt1']) + '<h3>3 · Améliorer</h3>' + code(t['prompt2'])
        guide += '<h3>4 · Vérifier</h3>' + ol([c['case'] + ' : ' + c['expected'] for c in t['checks']])
        for qid in t['sql_ids']:
            guide += '<h3>' + qid + '</h3>' + code(sql[qid])
        guide += '<h3>5 · Présenter</h3>' + p(w['presentation']) + '<h3>Si bloqué</h3>' + p(t['fallback']) + '<h3>Extension facultative</h3>' + p(t['extension']) + '</section>'
    guide += '<h2>Documentation officielle</h2><ul>'+''.join('<li><a href="'+e(d['url'])+'">'+e(d['label'])+'</a></li>' for d in w['documentation'])+'</ul>'
    guide += '<h2>Après la séance</h2><p>Exporter JSON pour restaurer les notes et Markdown pour partager la décision. Les notes sont locales au navigateur et à son origine ; file:// et HTTP peuvent avoir des stockages différents. Ni collaboration simultanée, ni audit de décision métier. Conserver les preuves avant tout nettoyage de ressources.</p></main></body></html>'
    write('guide.html', guide.replace('</body>', profile_links + '</body>'))
    portal = head + portal_markup(w, data, b, sql)
    write('missions.html', portal.replace('<script src="assets/portal.js">', profile_links + '<script src="assets/portal.js">'))
    trial = (ROOT / 'content/trial.html').read_text()
    write('trial.html', personal_head.replace('Harvest — atelier pratique', 'Préparer mon essai · Harvest') +
          '<body class="pg-home"><a class="skip" href="#installation">Aller à la préparation</a>' + brand +
          '<main class="trial-page" id="installation">' + return_link + trial + return_link + '</main>' + profile_links + '</body></html>')
    write('eres.html', personal_head + '<body><a class="skip" href="#eres-title">Aller au contenu</a>' + brand +
          '<main class="guide eres-home">' + return_link + eres_case + return_link + '<span id="copy-feedback" role="status"></span></main>' + profile_links + '<script src="assets/eres.js"></script></body></html>')
    legacy_route = r"""<script>
function openMissionLink() {
  if (/^#(contracts|funds)\/[0-4]$/.test(location.hash))
    location.replace('missions.html' + location.search + location.hash);
}
window.addEventListener('hashchange', openMissionLink);
openMissionLink();
</script>"""
    write('index.html', personal_head + '<body class="pg-home">' + legacy_route +
          '<a class="skip" href="#personal-guide">Aller au contenu</a>' + brand +
          '<main id="personal-guide" tabindex="-1"><noscript><h1>Mon parcours d’atelier</h1><p>Activez JavaScript pour enregistrer votre suivi personnel, ou consultez le <a href="guide.html">guide imprimable</a>.</p></noscript></main>'
          '<div class="pg-messages"><p id="guide-message" role="status" aria-live="polite"></p>'
          '<p id="guide-storage" hidden>Le navigateur ne peut pas enregistrer votre suivi. Exportez-le avant de fermer cette page.</p></div>'
          '<dialog id="pg-presentation" aria-labelledby="pg-present-title"><form method="dialog"><button autofocus>Fermer</button></form><div id="pg-present-body"></div></dialog>'
          '<footer><span>Harvest × Databricks · 24 novembre 2026</span><a href="guide.html">Guide imprimable</a></footer>'
          '<script type="application/json" id="parcours-data">' + safe_j(parcours) + '</script><script src="assets/parcours.js"></script></body></html>')
    write('README.txt', """HARVEST — ATELIER DU 24 NOVEMBRE 2026, 14 H–17 H
Décompressez tout le ZIP. Ouvrez index.html et choisissez votre prénom. Le guide affiche votre action, la preuve à garder et le code personnel à saisir dans le widget equipe du notebook ERES. Harvest et Avanade / Accenture suivent le même parcours dans leurs essais respectifs.
Commencez par le petit lot ERES, puis passez au cas Market Data. Le lot volume et la conversion des contrats sont des prolongements facultatifs. La préparation de l’essai est dans trial.html et le notebook à importer dans notebooks/00_DEMARRER.ipynb. Le guide imprimable est dans guide.html.
Chaque personne valide ses étapes et consigne ses preuves dans son navigateur. Rouvrez le kit au même emplacement pour reprendre. « Exporter » dans Mon parcours conserve les statuts et notes des sept étapes. Le carnet détaillé des missions a son propre export JSON dans « Mon carnet ». Restaurez chaque fichier dans l’écran correspondant.
Les consignes, les fichiers et les carnets fonctionnent hors ligne. Databricks nécessite une connexion et les accès de votre essai. Pour le second cas, importez lab.py pour les vérifications SQL, puis saisissez le catalogue et votre schéma du petit lot. Dans les fichiers SQL, remplacez {{ns}} par `catalogue`.`schema`. avant exécution.
Le mini-lab sémantique et son modèle se trouvent dans semantic/. SA0/SB0 illustrent des hypothèses à tester. Les metric views natives sont une extension. Les données du kit sont pédagogiques et les apps sont en lecture seule.
""")
    manifest = {name: hashlib.sha256(raw).hexdigest() for name, raw in sorted(files.items())}
    write('manifest.json', j({'version': w['version'], 'files': manifest}))
    archive = ROOT / 'harvest-participant.zip'
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
        for name, raw in sorted(files.items()):
            info = zipfile.ZipInfo('harvest-participant/' + name, (2026, 11, 16, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, raw)
    print(json.dumps({'participant_files': len(files), 'archive': str(archive), 'reference_queries': len(results)}, indent=2))


if __name__ == '__main__':
    build()
