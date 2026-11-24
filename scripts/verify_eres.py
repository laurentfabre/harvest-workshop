"""Verify the actual distributed ERES ZIPs and notebook queries. Requires DuckDB."""
import ast
import csv
import hashlib
import io
import json
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from zipfile import ZipFile

import duckdb
from eres_kit import ARCHIVES

ROOT = Path(__file__).resolve().parents[1]
KIT = ROOT / 'harvest-participant.zip'
PREFIX = 'harvest-participant/eres/'
EXPECTED = [
    {'raw':40, 'positions':6, 'bilan':(6,3,1,2), 'clients':7, 'comptes':5, 'mvts':(3,4,3)},
    {'raw':404969, 'positions':160007, 'bilan':(160007,144007,0,16000), 'clients':50500, 'comptes':80133, 'mvts':(32151,32151,32151)},
]


def verify(kit, name, expected, queries):
    stamp = name[:8]
    lot = datetime.strptime(stamp,'%Y%m%d').date()
    con = duckdb.connect()
    source_counts = {}
    with tempfile.TemporaryDirectory() as tmp, ZipFile(io.BytesIO(kit.read(PREFIX+name))) as source:
        assert source.testzip() is None
        kinds = ('REF','CLI','ENT','CTR','SUB_CTR','TYP','POS','MVT')
        assert set(source.namelist()) == {f'{stamp}_HARVEST_{k}.csv' for k in kinds}
        for kind in kinds:
            file = f'{stamp}_HARVEST_{kind}.csv'
            path = Path(tmp)/file
            with source.open(file) as raw, path.open('w', encoding='utf-8', newline='') as out:
                reader = csv.reader(io.TextIOWrapper(raw, encoding='utf-8'), delimiter=';', strict=True)
                writer = csv.writer(out,delimiter=';')
                header = next(reader)
                writer.writerow(header+['ligne_csv'])
                count = 0
                for count, row in enumerate(reader,1):
                    assert len(row)==len(header)
                    writer.writerow(row+[count+1])
            con.execute(f"CREATE TABLE bronze_{kind.lower()} AS SELECT * EXCLUDE(ligne_csv), cast(ligne_csv as integer) AS ligne_csv, ? AS fichier, ? AS date_lot FROM read_csv(?, header=true, all_varchar=true, delim=';')", [file,lot,str(path)])
            source_counts[kind]=count
    assert sum(source_counts.values())==expected['raw']
    # Repeat creation in the same namespace. Every generated SELECT is executed by the checks.
    for _ in range(2):
        for query in queries:
            con.execute(query)
    def row(query):
        return con.execute(query).fetchone()
    assert row('SELECT lues,publiees,historiques,rejetees FROM bilan_lot')==expected['bilan']
    assert row('SELECT count(*) FROM gold_client')==(expected['clients'],)
    assert row('SELECT count(*) FROM gold_produit')==(1,)
    assert row('SELECT count(*) FROM silver_positions p JOIN gold_compte c ON c.compte_id=p.code_contrat WHERE p.date_valorisation<c.ouverture')==(0,)
    assert row('SELECT count(*) FROM gold_compte')==(expected['comptes'],)
    assert row('SELECT count(*) FROM gold_situation')==(expected['bilan'][1],)
    assert row('SELECT count(*),sum(lignes),sum(details) FROM mouvements_groupes')==expected['mvts']
    assert row('SELECT count(*) FROM bronze_cli WHERE nom NOT LIKE \'Personne atelier %\' OR email IS NOT NULL OR tel_mobile IS NOT NULL OR adr1 IS NOT NULL')==(0,)
    assert row('SELECT count(*) FROM bronze_ent WHERE siren IS NOT NULL OR raison_sociale NOT LIKE \'Entreprise atelier %\'')==(0,)
    assert row('SELECT count(*) FROM (SELECT DISTINCT fichier, ligne_csv FROM revue_positions)')==(source_counts['POS'],)
    assert row('SELECT count(*) FROM fund_freshness')==(6,)
    assert row('SELECT count(*) FROM contract_review')==(6,)
    assert row('SELECT count(*) FROM calculation_review')==(6,)
    reasons=dict(con.execute("SELECT regle,count(*) FROM revue_positions WHERE decision='REJETEE' GROUP BY regle").fetchall())
    assert reasons==({'DATE_TROP_ANCIENNE':1,'VENTILATION':1} if expected['raw']==40 else {'VENTILATION':16000})
    if expected['raw']==40:
        assert row('SELECT ligne_csv FROM silver_positions WHERE disponible + indisponible <> valeur_euro')==(5,)
        assert row('SELECT sum(valeur_euro) FROM gold_situation')==(295,)
        assert row('SELECT lignes,details FROM mouvements_groupes WHERE lignes>details')==(2,1)
    con.close()
    return {'lot':str(lot),'sha256':hashlib.sha256(kit.read(PREFIX+name)).hexdigest(),'rows':source_counts,'bilan':expected['bilan'],'rejets':reasons,'status':'PASS'}


def main():
    with ZipFile(KIT) as kit:
        notebook=kit.read(PREFIX+'import_eres.py').decode()
        code=ast.parse(notebook)
        queries=[n.args[0].value for n in ast.walk(code) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='sql' and n.args and isinstance(n.args[0],ast.Constant) and isinstance(n.args[0].value,str) and n.args[0].value.strip().startswith('CREATE VIEW')]
        assert len(queries)==16
        binds=json.loads(kit.read('harvest-participant/session.json'))
        assert all(not v for k,v in binds.items() if k.endswith('_url') or k in ('catalog','schema','warehouse_id'))
        for name in ARCHIVES:
            assert hashlib.sha256(kit.read(PREFIX+name)).hexdigest() in notebook
        report={'timestamp':datetime.now(timezone.utc).isoformat(),'environment':'local DuckDB '+duckdb.__version__,'scope':'Archived CSVs and notebook view SQL, repeated view creation. Databricks upload, permissions, Spark/Delta writes, Genie and Builder require the target trials.','archive_sha256':hashlib.sha256(KIT.read_bytes()).hexdigest(),'lots':[verify(kit,name,expected,queries) for name,expected in zip(ARCHIVES,EXPECTED)]}
    path=ROOT/'validation'/('eres-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'.json')
    path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(path)
    for result in report['lots']:
        print(result['lot'],result['bilan'],result['rejets'])

if __name__=='__main__':
    main()
