"""Portable teaching model. SQL is the executable source of the comparisons.

The ontology describes the existing snapshot; it does not provision a graph engine.
"""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
SEMANTIC_IDS = ['SA0', 'SA1', 'SA2', 'SB0', 'SB1', 'SB2']


def load_lab():
    return json.loads((ROOT / 'content/semantics.json').read_text())


def snapshot(db):
    run = lambda sql: [dict(r) for r in db.execute(sql)]
    queries = {qid: run((ROOT / 'sql' / (qid + '.sql')).read_text().replace('{{ns}}', '')) for qid in SEMANTIC_IDS}
    return {
        'engine': 'SQLite local, jeu synthétique figé ; aucune requête live depuis le portail',
        'queries': queries,
        'contracts': run('SELECT * FROM contract_review ORDER BY contract_id'),
        'funds': run('SELECT * FROM fund_freshness ORDER BY fund_id'),
        'calculations': run('SELECT * FROM calculation_review ORDER BY calculation_id'),
    }


def track_markdown(lab, track, sql, bind=lambda s: s):
    t = lab['tracks'][track]
    out = ['# ' + t['title'], lab['disclosure'], '## 1 · Prédire, puis comparer', t['challenge']]
    out += [f'{i+1}. {step}' for i, step in enumerate(t['exercise'])]
    out += ['## 2 · Ontologie : objets et relations']
    for node in t['entities']:
        out += ['### ' + node['label'], node['meaning'], '**Grain / clé :** ' + node['grain'], '**Source :** ' + bind(node['source'])]
    for edge in t['relations']:
        out += ['- ' + edge['label'] + ' — ' + edge['cardinality'] + '. ' + edge['rule']]
    out += ['## 3 · Couche sémantique : définitions réutilisables']
    for m in t['measures']:
        out += ['### ' + m['label'], m['definition'], '**Unité :** ' + m['unit'] + '. **Grain :** ' + m['grain'], '**Limite :** ' + m['limit']]
    out += ['## 4 · SQL reproductible']
    for qid in t['sql_ids']:
        out += ['### ' + qid, '```sql\n' + bind(sql[qid]).strip() + '\n```']
    out += ['## 5 · Même définition dans Genie et l’app', t['genie_prompt'], t['handoff'], '## 6 · Démontrer le bénéfice et sa limite', t['debrief'], lab['limits']]
    return '\n\n'.join(out) + '\n'


def metric_definitions():
    def field(name, expr, label, comment):
        return dict(name=name, expr=expr, display_name=label, comment=comment)
    return [
        dict(name='contract_metrics', source='contract_review', comment='Conservation numérique des contrats au snapshot pédagogique. Ne vaut pas autorisation de livraison.',
             dimensions=[field('provider_id','provider_id','Fournisseur','Identifiant du fournisseur fictif.'), field('business_date','business_date','Date métier','Date du contrat observé ; snapshot immuable.'), field('review_status','review_status','Statut de conservation','Définition commune de contract_review ; aucune cause inférée.')],
             measures=[field('population','COUNT(*)','Contrats observés','Nombre de contrats dans le périmètre filtré.'),field('preserved_contracts',"COUNT(CASE WHEN review_status = 'PRESERVED' THEN 1 END)",'Contrats conservés','Contrats dont la valeur fournisseur est préservée ; estimation indépendante.'),field('preservation_pct',"100.0 * COUNT(CASE WHEN review_status = 'PRESERVED' THEN 1 END) / NULLIF(COUNT(*), 0)",'Taux de conservation','Pourcentage sur tous les contrats filtrés. Réagréger le ratio ; NULL si population vide.'),field('preserved_supplier_eur',"SUM(CASE WHEN review_status = 'PRESERVED' THEN supplier_cents END) / 100.0",'Montant fournisseur conservé','EUR ; somme des montants fournisseur conservés, NULL si aucun montant connu.'),field('known_supplier_amounts','COUNT(supplier_cents)','Montants fournisseur connus','Couverture des montants ; toujours accompagner une somme.'),field('supplier_coverage_pct','100.0 * COUNT(supplier_cents) / NULLIF(COUNT(*), 0)','Complétude fournisseur','Pourcentage de montants fournisseur connus sur tous les contrats filtrés, tous statuts inclus ; distinct de la conservation.'),field('known_supplier_eur','SUM(supplier_cents) / 100.0','Montant fournisseur connu','EUR ; total partiel si couverture incomplète. Ne remplace pas le montant conservé.')]),
        dict(name='fund_arrival_metrics',source='fund_freshness',comment='Fraîcheur des VL au 20 octobre 2026 à 10:00 UTC. Une ligne par fonds/date ; calendrier et absences conservés.',
             dimensions=[field('nav_date','nav_date','Date de VL','Date attendue dans le calendrier.'),field('arrival_status','arrival_status','État de réception','MISSING, WAITING, NOT_EXPECTED, LATE_RECEIVED ou ON_TIME ; non interchangeables.')],
             measures=[field('population','COUNT(*)','Fonds et dates observés','Nombre de couples fonds/date ; pas un nombre de calculs.'),field('expected_funds','COUNT(CASE WHEN expected = 1 THEN 1 END)','VL attendues','Dénominateur défini par le calendrier.'),field('overdue_missing',"COUNT(CASE WHEN arrival_status = 'MISSING' THEN 1 END)",'Absences en retard','Nombre de fonds/date attendus, échus et sans réception à 10:00 UTC.'),field('overdue_pct',"100.0 * COUNT(CASE WHEN arrival_status = 'MISSING' THEN 1 END) / NULLIF(COUNT(CASE WHEN expected = 1 THEN 1 END), 0)",'Taux d’absences en retard','Pourcentage des VL attendues ; NULL si aucune attente. Ne pas moyenner les taux.')]),
        dict(name='calculation_metrics',source='calculation_review',comment='Impact direct d’une version fournisseur sur des calculs, au snapshot à date unique. Aucun recalcul déclenché.',
             dimensions=[field('fund_id','fund_id','Fonds','Fonds consommé ; plusieurs calculs peuvent le partager.'),field('calculation_status','calculation_status','État du calcul','État issu de la comparaison de version ; candidat ne signifie pas recalculé.')],
             measures=[field('calculations','COUNT(DISTINCT calculation_id)','Calculs distincts','Grain calculation_id, non fund_id.'),field('recompute_candidates',"COUNT(DISTINCT CASE WHEN calculation_status = 'RECOMPUTE_CANDIDATE' THEN calculation_id END)",'Calculs candidats','Calculs ayant consommé une version antérieure ; à examiner.'),field('affected_funds',"COUNT(DISTINCT CASE WHEN calculation_status = 'RECOMPUTE_CANDIDATE' THEN fund_id END)",'Fonds concernés','Fonds distincts associés aux candidats. Mesure non additive entre groupes de calculs.'),field('waiting_calculations',"COUNT(DISTINCT CASE WHEN calculation_status = 'WAIT_SOURCE' THEN calculation_id END)",'Calculs en attente','Calculs dont la source manque ; ce n’est pas une exécution en échec.')])
    ]


def native_metric_sql():
    # JSON-quoted scalars are valid YAML. No materialization or resource replacement.
    quote = lambda s: json.dumps(s, ensure_ascii=False)
    statements=[]
    for m in metric_definitions():
        lines=['version: 1.1', 'source: '+quote('{{ns}}'+m['source']), 'comment: '+quote(m['comment'])]
        for section in ['dimensions','measures']:
            lines.append(section+':')
            for f in m[section]:
                lines.append('  - name: '+quote(f['name']))
                lines += ['    '+key+': '+quote(f[key]) for key in ['expr','display_name','comment']]
        statements.append('CREATE VIEW {{ns}}'+m['name']+'\nWITH METRICS\nLANGUAGE YAML\nAS $$\n'+'\n'.join(lines)+'\n$$;')
    return '-- EXTENSION FACULTATIVE : revue, droits et compatibilité requis avant exécution.\n-- Définitions préparées, pas de déploiement implicite. Aucun CREATE OR REPLACE.\n\n'+'\n\n'.join(statements)+'\n'


def native_queries():
    return '''-- À exécuter uniquement après déploiement et vérification des metric views.
SELECT MEASURE(population) AS population,
       MEASURE(preserved_contracts) AS preserved_contracts,
       MEASURE(preservation_pct) AS preservation_pct,
       MEASURE(preserved_supplier_eur) AS preserved_supplier_eur
FROM {{ns}}contract_metrics;

SELECT provider_id, MEASURE(population) AS population,
       MEASURE(preserved_contracts) AS preserved_contracts,
       MEASURE(preservation_pct) AS preservation_pct,
       MEASURE(preserved_supplier_eur) AS preserved_supplier_eur
FROM {{ns}}contract_metrics GROUP BY ALL ORDER BY provider_id;

SELECT MEASURE(population) AS population, MEASURE(expected_funds) AS expected_funds,
       MEASURE(overdue_missing) AS overdue_missing, MEASURE(overdue_pct) AS overdue_pct
FROM {{ns}}fund_arrival_metrics;

SELECT MEASURE(calculations) AS calculations,
       MEASURE(recompute_candidates) AS recompute_candidates,
       MEASURE(affected_funds) AS affected_funds,
       MEASURE(waiting_calculations) AS waiting_calculations
FROM {{ns}}calculation_metrics;
'''
