import pandas as pd

R_MOT_SIMPLE = r"[{0}]+"
R_MOT_COMPLEXE = r"[{0}][{1}]*"

R_MOTS = r"{0}(?:(?: |\r)+{0})*"

C_NOM_INIT = r"\w'(."
C_NOM = r"\w'(),.-"
C_PRENOMS_INIT = C_NOM_INIT
C_PRENOMS = C_NOM
C_USAGE = C_NOM
C_LIEU = r"\w'/&()[\]°*.,:/-"
C_DEP = r"\w'-"
C_ADRESSE = C_LIEU
C_VILLE =  C_LIEU

R_NOM = R_MOTS.format(R_MOT_COMPLEXE.format(C_NOM_INIT, C_NOM))
R_PRENOMS = R_MOTS.format(R_MOT_COMPLEXE.format(C_PRENOMS_INIT, C_PRENOMS))
R_USAGE = R_MOTS.format(R_MOT_SIMPLE.format(C_USAGE))
R_DATE = r"\d{2}/\d{2}/\d{4}"

# capturer en mode non gourmand, car un lieu peut se finir par un mot entre parenthèses, mais cela peut aussi être le
# nom du département
R_LIEU_NAISSANCE = R_MOTS.format(R_MOT_SIMPLE.format(C_LIEU)) + "?"

R_DEP = R_MOTS.format(R_MOT_SIMPLE.format(C_DEP))

REGEX_1 = fr"""^
(?P<nom_famille>{R_NOM})(?: |\r)+-(?: |\r)+(?P<prenoms>{R_PRENOMS})\r
(?:- +(?:\.|(?:[Ee][Pp]\. +)?(?P<nom_usage>{R_USAGE}))\r)?
Né\(e\) +le +(?P<date_naissance>{R_DATE}) (?:à )?(?P<lieu_naissance>{R_LIEU_NAISSANCE})?(?:(?: |\r)*?\((?P<departement_naissance>{R_DEP})\))?
$""".replace('\n', '')

R_ADRESSE = R_MOTS.format(R_MOT_SIMPLE.format(C_ADRESSE))
R_VILLE = R_MOTS.format(R_MOT_SIMPLE.format(C_VILLE))

REGEX_2 = fr"""^
(?P<adresse>{R_ADRESSE})(?: |\r)+(?P<code_postal>\d{{2,5}})(?P<ville>{R_VILLE})
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
