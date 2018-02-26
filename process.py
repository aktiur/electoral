import sys
import re
from pathlib import Path
from collections import OrderedDict
import pandas as pd

from parsers import type1

FILENAME_FORMAT = r"^T(?P<type>\d)_(?P<insee>\w{5})_(?P<commune>[\w '-]+)(?:_\d{2})?\.csv"


COLUMNS = OrderedDict([
    ('TypeListe', False),
    ('CodeDepartement', True),
    ('CodeCommune', True),
    ('Civilite', False),
    ('NomdeNaissance', True),
    ('NomDusage', True),
    ('Prenoms', True),
    ('DateDeNaissance', True),
    ('NomComNaissance', True),
    ('DeptNaissance', True),
    ('PaysNaissance', False),
    ('Nationalite', True),
    ('ComplementDeLocalisation1', True),
    ('ComplementDeLocalisation2', False),
    ('NumeroVoie', False),
    ('TypeVoie', False),
    ('LibelleVoie', True),
    ('LieuDit', False),
    ('CodePostal', True),
    ('VilleLocalite', True),
    ('Pays', True),
    ('NomCommune', True),
])


def format_output(df, insee, commune):
    df['TypeListe'] = 'G'
    df['CodeDepartement'] = insee[:2]
    df['CodeCommune'] = insee
    df['NomCommune'] = commune

    return df.rename(columns={
        'nom_famille': 'NomdeNaissance',
        'prenoms': 'Prenoms',
        'nom_usage': 'NomDusage',
        'date_naissance': 'DateDeNaissance',
        'lieu_naissance': 'NomComNaissance',
        'departement_naissance': 'DeptNaissance',
        'adresse': 'LibelleVoie',
        'code_postal': 'CodePostal',
        'ville': 'VilleLocalite',
        'complement': 'ComplementDeLocalisation1',
    }).reindex(columns=list(COLUMNS))


def handle_file(input_file, output_file, error_file):
    path = Path(input_file)
    match = re.match(FILENAME_FORMAT, path.name)

    if not match:
        sys.stderr.write('Format de nom de fichier incorrect: {}'.format(input_file))
        sys.exit(1)

    if match.group('type') != '1':
        sys.stderr.write('Format T{} non traité : {}'.format(match.group('type'), input_file))
        sys.exit(2)

    format, insee, commune = match.groups()

    df = pd.read_csv(input_file)

    res, err = type1.parse(df)

    format_output(res, insee, commune).to_csv(output_file, index=False)
    err.to_csv(error_file, index=False)


if __name__ == '__main__':
    input_file = Path(sys.argv[1])

    output_dir = Path.cwd() / 'out'
    error_dir = Path.cwd() / 'err'
    output_dir.mkdir(exist_ok=True)
    error_dir.mkdir(exist_ok=True)

    output_file = output_dir / input_file.name
    error_file = error_dir / input_file.name

    handle_file(str(input_file), str(output_file), str(error_file))
