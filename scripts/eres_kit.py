"""Build the ERES notebook and download set from the distributed lots and SQL."""
import csv
import hashlib
import io
import json
from zipfile import ZipFile
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / 'eres'
ARCHIVES = ('20261123_HARVEST.zip', '20261124_HARVEST.zip')


def statements(source):
    return [s.strip() for s in source.split(';') if s.strip()]


def notebook_cells(queries):
    return '\n\n# COMMAND ----------\n'.join('spark.sql("""\n' + q.replace('CREATE VIEW ', 'CREATE VIEW IF NOT EXISTS ', 1) + '\n""")' for q in queries)


def preview_positions():
    """Use actual workshop CSV lines in the studio's interactive preview."""
    with ZipFile(SOURCE / ARCHIVES[0]) as archive:
        name = next(n for n in archive.namelist() if n.endswith('_POS.csv'))
        with archive.open(name) as raw:
            rows = csv.DictReader(io.TextIOWrapper(raw, encoding='utf-8'), delimiter=';')
            return [dict(line=i, account=r['code_sous_contrat'], day=r['date_valeur'],
                         gross=int(r['montant_brut']), available=int(r['montant_disponible']),
                         unavailable=int(r['montant_indisponible'])) for i, r in enumerate(rows, 2)]


def as_ipynb(source):
    cells = []
    for block in source.removeprefix('# Databricks notebook source\n').split('# COMMAND ----------\n'):
        lines = block.strip().splitlines()
        if lines[0] == '# MAGIC %md':
            body = '\n'.join(line.removeprefix('# MAGIC').removeprefix(' ') for line in lines[1:])
            cell = {'cell_type': 'markdown', 'source': body}
        else:
            cell = {'cell_type': 'code', 'source': '\n'.join(lines), 'execution_count': None, 'outputs': []}
        cells.append({**cell, 'metadata': {}})
    return json.dumps({'nbformat': 4, 'nbformat_minor': 4,
                       'metadata': {'kernelspec': {'name': 'python3', 'display_name': 'Python 3', 'language': 'python'}},
                       'cells': cells}, indent=2, ensure_ascii=False) + '\n'


def kit_files(dataset, sql_root):
    files = {f'eres/{name}': (SOURCE / name).read_bytes() for name in ARCHIVES}
    fingerprints = {name: hashlib.sha256(files[f'eres/{name}']).hexdigest() for name in ARCHIVES}
    sql = (SOURCE / 'transformations.sql').read_text()
    files['eres/transformations.sql'] = sql
    follow_on = []
    for name, table in dataset['tables'].items():
        def literal(value):
            if value is None:
                return 'NULL'
            if isinstance(value, str):
                return "'" + value.replace("'", "''") + "'"
            return str(value)
        fields = ', '.join(c[0] for c in table['columns'])
        values = ',\n'.join('(' + ', '.join(literal(v) for v in row) + ')' for row in table['rows'])
        follow_on.append(f'CREATE VIEW {name} AS SELECT * FROM VALUES\n{values} AS seed({fields})')
    for name in ('contract_review', 'fund_freshness', 'calculation_review'):
        query = (sql_root / (name + '.sql')).read_text().replace('{{ns}}', '').strip().rstrip(';')
        follow_on.append(f'CREATE VIEW {name} AS {query}')
    notebook = (SOURCE / 'import_template.py').read_text().replace('__ARCHIVE_HASHES__', repr(fingerprints))
    files['eres/import_eres.py'] = notebook.replace('# __TRANSFORMATIONS__', notebook_cells(statements(sql))).replace('# __FOLLOW_ON__', notebook_cells(follow_on))
    files['notebooks/00_DEMARRER.ipynb'] = as_ipynb(files['eres/import_eres.py'])
    return files
