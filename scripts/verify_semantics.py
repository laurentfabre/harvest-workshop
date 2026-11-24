"""Check semantic counterexamples, grain, ratios and portable metric expressions."""
import json
from datetime import datetime, timezone
from build import ROOT, local_database, read_json
from semantic_model import SEMANTIC_IDS, load_lab, snapshot, metric_definitions


def main():
    checks=[]
    data=read_json(ROOT/'content/dataset.json');db=local_database(data)
    def check(name,condition,observed):
        checks.append({'id':name,'status':'PASS' if condition else 'FAIL','observed':observed})
    run=lambda sql:[dict(r) for r in db.execute(sql)]
    sql=lambda q:(ROOT/'sql'/f'{q}.sql').read_text().replace('{{ns}}','')
    actual=snapshot(db);q=actual['queries'];packed=read_json(ROOT/'participant/semantic/references.json')
    for qid in SEMANTIC_IDS:check(qid+'-packaged-results',q[qid]==packed['queries'][qid],q[qid])
    check('conversion-is-not-preservation',q['SA0'][0]['treated_as_preserved']==4 and q['SA1'][0]['preserved_contracts']==3,{'quick':q['SA0'],'shared':q['SA1']})
    check('authoritative-money-and-coverage',q['SA1'][0]['preserved_supplier_eur']==14600.25 and q['SA1'][0]['known_supplier_amounts']==5,q['SA1'])
    check('absence-is-not-incident',q['SB0'][0]['absent_observations']==3 and q['SB1'][0]['overdue_missing']==1 and q['SB1'][0]['overdue_pct']==20,q['SB1'])
    check('fanout-and-impact-grains',q['SB0'][0]['joined_rows']==8 and q['SB1'][0]['population']==6 and q['SB2'][0]['recompute_candidates']==3 and q['SB2'][0]['affected_funds']==2,q['SB2'])
    # Native YAML expressions are checked as ordinary aggregate SQL; this is not a Databricks DDL test.
    for definition in metric_definitions():
        query='SELECT '+', '.join(m['expr']+' AS '+m['name'] for m in definition['measures'])+' FROM '+definition['source']
        rows=run(query);reference=q[{'contract_metrics':'SA1','fund_arrival_metrics':'SB1','calculation_metrics':'SB2'}[definition['name']]][0]
        check('metric-expression-'+definition['name'],all(rows[0][k]==v for k,v in reference.items() if k in rows[0]),rows)
        check('metric-metadata-'+definition['name'],all(f.get('comment') and f.get('display_name') for f in definition['dimensions']+definition['measures']),'Every dimension and measure has a comment and display name')
    empty=run(sql('SA1').replace('FROM contract_review','FROM contract_review WHERE provider_id = \'P99\''))[0]
    check('empty-population-null-ratio',empty['population']==0 and empty['preserved_contracts']==0 and empty['preservation_pct'] is None and empty['preserved_supplier_eur'] is None,empty)
    empty=run(sql('SB1').replace('FROM fund_freshness',"FROM fund_freshness WHERE fund_id = 'F004'"))[0]
    check('no-expectations-null-ratio',empty['expected_funds']==0 and empty['overdue_pct'] is None,empty)
    db.execute("UPDATE contract_observations SET provider_id='P01' WHERE contract_id='C006'")
    groups=run(sql('SA2'));global_rate=run(sql('SA1'))[0]['preservation_pct'];weighted=100*sum(g['preserved_contracts'] for g in groups)/sum(g['population'] for g in groups)
    mean=sum(g['preservation_pct'] for g in groups)/len(groups)
    check('ratio-reaggregation-unequal-groups',global_rate==weighted==50 and abs(mean-global_rate)>10,{'global':global_rate,'reaggregated':weighted,'incorrect_mean_of_rates':mean})
    db.execute("INSERT INTO calculation_state VALUES ('F001','F001:extra',1,7,'score')")
    impact=run(sql('SB2'))[0];arrivals=run(sql('SB1'))[0]
    check('new-child-does-not-duplicate-parent',impact['recompute_candidates']==4 and impact['affected_funds']==2 and arrivals['population']==6,impact)
    db.execute("UPDATE fund_expectations SET deadline_utc='2026-10-20 09:00:00' WHERE fund_id='F005'")
    arrivals=run(sql('SB1'))[0]
    check('calendar-change-propagates-through-view',arrivals['overdue_missing']==2 and arrivals['overdue_pct']==40,arrivals)
    db.execute("INSERT INTO fund_expectations VALUES ('F001','2026-10-21',1,'2026-10-21 08:00:00','Next day')")
    next_day=run("SELECT received_at_utc FROM fund_freshness WHERE fund_id='F001' AND nav_date='2026-10-21'")[0]
    check('composite-key-keeps-other-date-missing',next_day['received_at_utc'] is None,next_day)
    for track,t in load_lab()['tracks'].items():
        ids={n['id'] for n in t['entities']}
        check('ontology-links-'+track,all(e['from'] in ids and e['to'] in ids and e['rule'] and e['cardinality'] for e in t['relations']),[e['label'] for e in t['relations']])
        check('track-time-'+track,sum(int(x.split(' min')[0]) for x in t['exercise'])==20,'20 minutes including the original Genie investigation')
    report={'timestamp':datetime.now(timezone.utc).isoformat(),'artifact':read_json(ROOT/'content/workshop.json')['version'],'dataset':data['version'],'environment':'local SQLite; no native metric-view execution implied','checks':checks}
    path=ROOT/'validation'/('semantics-local-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')+'.json');path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    failed=[c for c in checks if c['status']=='FAIL'];print(json.dumps({'report':str(path),'passed':len(checks)-len(failed),'failed':failed},indent=2));return bool(failed)

if __name__=='__main__':raise SystemExit(main())
