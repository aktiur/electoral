import pandas as pd
import csv
import re
from itertools import islice

C_NOMS = "A-ZÀÂÄÉÈÊEËÎÏÔÖÙÛÜ'-"

R_MOT_SIMPLE = r"[{0}]+"
R_MOT_COMPLEXE = r"[{0}][{1}]*"

R_MOTS = r"{0}(?:(?: |\r)+{0})*"
R_MOTS_SANS_RC = r"{0}(?: +{0})*"

R_LIEU = R_MOTS.format(R_MOT_SIMPLE.format("\w'/&()[\]°*.,:/-"))

R_NUMERO = r"^\d+(\r\d+)*$"

R_NOM_FAMILLE = R_MOTS.format(R_MOT_SIMPLE.format(C_NOMS))
R_NOM_USAGE = R_MOTS_SANS_RC.format(R_MOT_SIMPLE.format(C_NOMS))
R_PRENOMS = R_MOTS.format(R_MOT_SIMPLE.format(r"\w,'.-")) + '?'

R_NAISSANCE = fr"^(?P<date_naissance>\d{{2}}/\d{{2}}/\d{{4}})[MF]\r(?P<departement_naissance>\d+)\r?(?P<lieu_naissance>{R_LIEU})$"
R_NOMS = fr"^(?P<nom_famille>{R_NOM_FAMILLE}) (?P<prenoms>{R_PRENOMS})(?:\r(?:Ep\. )?(?P<nom_usage>{R_NOM_FAMILLE}))?$"
R_ADRESSE = fr"^(?P<adresse>{R_LIEU})\r+(?P<code_postal>\d{{5}})\r?(?P<ville>{R_LIEU})$"


def select_fields(line):
    return tuple(islice((f for f in line[1:] if len(f) > 4), 3))


def process_file(input_file):
    with open(input_file, 'r', newline='') as f:
        check = re.compile(R_NUMERO)
        r = csv.reader(f)
        for line in r:
            if check.match(line[0]) and len(line) > 2:
                # we keep the three first long enough fields
                yield select_fields(line)


def parse(input_file):
        df = pd.DataFrame.from_records(process_file(input_file), columns=['naissance', 'noms', 'adresse_complete'])

        keep = (
            df.naissance.str.match(R_NAISSANCE) &
            df.noms.str.match(R_NOMS) &
            df.adresse_complete.str.match(R_ADRESSE)
        )

        naissance = df.naissance.str.extract(R_NAISSANCE, expand=True)
        noms = df.noms.str.extract(R_NOMS, expand=True)
        adresse = df.adresse_complete.str.extract(R_ADRESSE, expand=True)

        for df in (naissance, noms, adresse):
            for c in df:
                df[c] = df[c].str.replace('-\r', '-').str.replace('\r', ' ')

        res = pd.concat([naissance, noms, adresse], axis=1)
        total = pd.concat([df, res], axis=1)

        return res[keep], total[~keep]
