import sys
import re
import csv
from pathlib import Path
from collections import OrderedDict
import pandas as pd

from parsers import type1

FILENAME_FORMAT = r"^T(?P<type>\w)_(?P<insee>\w{5})_(?P<commune>[\w '-]+)(?:_\d{2})?\.csv"


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


class IncorrectFilenameException(Exception):
    pass


class UnknownFormatException(Exception):
    pass



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
        raise IncorrectFilenameException()

    if match.group('type') != '1':
        raise UnknownFormatException()

    format, insee, commune = match.groups()

    df = pd.read_csv(input_file)

    res, err = type1.parse(df)

    format_output(res, insee, commune).to_csv(output_file, index=False, sep=';', )

    if len(err):
        err.to_csv(error_file, index=False, quoting=csv.QUOTE_NONNUMERIC)

    return len(err), len(res)


if __name__ == '__main__':
    main_dir = Path(sys.argv[1])

    input_dir = main_dir / 'pretreated'
    output_dir = main_dir / 'out'
    error_dir = main_dir / 'err'
    output_dir.mkdir(exist_ok=True)
    error_dir.mkdir(exist_ok=True)

    total_successes = 0
    total_errors = 0

    for f in input_dir.glob('*.csv'):
        try:
            nb_errs, nb_successes = handle_file(f, output_dir / f.name, error_dir / f.name)
            total_errors += nb_errs
            total_successes += nb_successes
            sys.stdout.write(
                '{: <35} {:5d} errors {: >8.2f} % success\n'.format(
                    f.stem, nb_errs, nb_successes / (nb_successes + nb_errs)
                ))
            sys.stdout.flush()
        except IncorrectFilenameException:
            sys.stderr.write('{: <35} [nom de fichier incorrect]\n'.format(f.stem))
        except UnknownFormatException:
            sys.stderr.write('{: <35} [format du fichier inconnu]\n'.format(f.stem))

    sys.stderr.write('{: <35} {:5d} errors {: >8.2f} % success\n'.format(
        'TOTAL', total_errors, total_successes / (total_successes + total_errors) * 100)
    )
