import pandas as pd

C_NOM = r"\w'().-"
C_PRENOMS = r"\w',.-"
C_USAGE = C_NOM
C_LIEU = r"\w'/()[\]°.,:/-"
C_DEP = r"\w'-"
C_ADRESSE = C_LIEU
C_VILLE =  C_LIEU

R_NOM = fr"[{C_NOM}]+(?:(?: |\r)+[{C_NOM}]+)*"
R_PRENOMS = fr"[{C_PRENOMS}]+(?:(?: |\r)+[{C_PRENOMS}]+)*"
R_USAGE = fr"[{C_USAGE}]+(?:(?: |\r)+[{C_USAGE}]+)*"
R_DATE = r"\d{2}/\d{2}/\d{4}"

# capturer en mode non gourmand, car un lieu peut se finir par un mot entre parenthèses, mais cela peut aussi être le
# nom du département
R_LIEU_NAISSANCE = fr"[{C_LIEU}]+(?:(?: |\r)+[{C_LIEU}]+)*?"

R_DEP = fr"[{C_DEP}]+(?:(?: |\r)+[{C_DEP}]+)*"

REGEX_1 = fr"""^
(?P<nom_famille>{R_NOM})(?: |\r)+-(?: |\r)+(?P<prenoms>{R_PRENOMS})\r
(?:- +(?:\.|(?:[Ee][Pp]\. +)?(?P<nom_usage>{R_USAGE}))\r)?
Né\(e\) le (?P<date_naissance>{R_DATE}) (?:à )?(?P<lieu_naissance>{R_LIEU_NAISSANCE})?(?:(?: |\r)*?\((?P<departement_naissance>{R_DEP})\))?
$""".replace('\n', '')

REGEX_2 = r"""^
(?P<adresse>[\w().°',:/-]+(?:(?: |\r)+[\w().°',:/-]+)*)(?: |\r)+(?P<code_postal>\d{4,5})(?P<ville>[\w'-]+(?:(?: |\r)[\w'-]+)*)
(?:\r(?P<complement>[^\r]+))?
$""".replace('\n', '')


def parse(df):
    # éliminer les lignes de headers répétées
    df = df[df.iloc[:, 0] != df.columns[0]]

    # on identifie les lignes qui fonctionnent
    keep = df.iloc[:, 0].str.match(REGEX_1) & df.iloc[:, 1].str.match(REGEX_2)

    # On extrait les informations de noms
    informations = df.iloc[:, 0].str.extract(REGEX_1, expand=True)

    for c in informations:
        informations[c] = informations[c].str.replace('\r', ' ').str.replace('  +', ' ')

    # les informations d'adresse
    adresse = df.iloc[:, 1].str.extract(REGEX_2, expand=True)

    for c in adresse:
        adresse[c] = adresse[c].str.replace('\r', ' ').str.replace('  +', ' ')

    # on combine tout dans un nouveau tableau
    res = pd.concat(
        [informations, adresse, df.iloc[:, 2]],
        axis=1,
    )

    total = pd.concat([df, informations, adresse], axis=1)

    return (
        res[keep],
        total[~keep]
    )
