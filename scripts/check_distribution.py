"""Compare the extracted distribution with the website and both notebook formats."""
import argparse
import hashlib
import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]


class LocalLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = set()

    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key in ('href', 'src') and value:
                url = urlparse(value)
                if not url.scheme and url.path:
                    self.links.add(url.path)


def check(archive=ROOT / 'harvest-participant.zip'):
    prefix = 'harvest-participant/'
    with ZipFile(archive) as kit:
        assert kit.testzip() is None
        manifest = json.loads(kit.read(prefix + 'manifest.json'))['files']
        assert kit.read(prefix + 'manifest.json') == (ROOT / 'participant/manifest.json').read_bytes()
        assert set(kit.namelist()) == {prefix + n for n in set(manifest) | {'manifest.json'}}
        for name, digest in manifest.items():
            data = kit.read(prefix + name)
            assert hashlib.sha256(data).hexdigest() == digest, name
            assert (ROOT / 'participant' / name).read_bytes() == data, name
            if name.endswith('.html'):
                parser = LocalLinks()
                parser.feed(data.decode())
                assert parser.links <= set(manifest), parser.links - set(manifest)
        notebook = json.loads(kit.read(prefix + 'notebooks/00_DEMARRER.ipynb'))
        source = kit.read(prefix + 'eres/import_eres.py').decode().removeprefix('# Databricks notebook source\n')
        blocks = [part.strip() for part in source.split('# COMMAND ----------\n')]
        assert len(notebook['cells']) == len(blocks)
        for cell, block in zip(notebook['cells'], blocks):
            if block.startswith('# MAGIC %md'):
                assert cell['cell_type'] == 'markdown'
                continue
            assert cell['cell_type'] == 'code' and cell['source'] == block
            assert cell['execution_count'] is None and not cell['outputs']
            compile(cell['source'], '00_DEMARRER.ipynb', 'exec')
    print(f'{len(manifest) + 1} packaged files verified, {len(blocks)} notebook cells checked.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', nargs='?', type=Path, default=ROOT / 'harvest-participant.zip')
    check(parser.parse_args().archive)
