"""Stage Pages from the verified participant ZIP, including its offline download."""
import argparse
import shutil
from pathlib import Path
from zipfile import ZipFile


def stage(archive, directory):
    directory.mkdir(parents=True, exist_ok=True)
    if any(directory.iterdir()):
        raise ValueError('Choose an empty Pages output directory.')
    with ZipFile(archive) as kit:
        for entry in kit.infolist():
            name = Path(entry.filename)
            if name.parts[:1] != ('harvest-participant',) or '..' in name.parts:
                raise ValueError(f'Unexpected kit path: {name}')
            dest = directory.joinpath(*name.parts[1:])
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(kit.read(entry))
    shutil.copyfile(archive, directory / 'harvest-participant.zip')
    home = directory / 'index.html'
    link = '<a href="harvest-participant.zip" download>Télécharger le kit hors ligne</a>'
    home.write_text(home.read_text().replace('</footer>', link + '</footer>'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', type=Path)
    parser.add_argument('directory', type=Path)
    args = parser.parse_args()
    stage(args.archive, args.directory)
