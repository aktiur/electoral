import pandas as pd

REGEX_1 = r"""^
(?P<nom_famille>[\w'-]+(?: [\w'-]+)*) - (?P<prenoms>[\w',-]+(?: [\w',-]+)*)\r
(?:- (?P<nom_usage>[\w'-]+(?: [\w'-]+)*)\r)?
Né\(e\) le (?P<date_naissance>\d{2}/\d{2}/\d{4})
 à (?P<lieu_naissance>[\w'-]+(?: [\w'()-]+)*?)(?: \((?P<departement_naissance>[\w'-]+(?: [\w'-]+)*)\))?
$""".replace('\n', '')

REGEX_2 = r"""^
(?P<adresse>[\w().°'-]+(?:(?: |\r)+[\w().°'-]+)*)(?: |\r)(?P<code_postal>\d{4,5})(?P<ville>[\w'-]+(?:(?: |\r)[\w'-]+)*)
(?:\r(?P<complement>[^\r]+))?
$""".replace('\n', '')


def parse(df):
    # éliminer les lignes de headers répétées
    df = df[df.iloc[:, 0] != df.columns[0]]

    # on identifie les lignes qui fonctionnent
    keep = df.iloc[:, 0].str.match(REGEX_1) & df.iloc[:, 1].str.match(REGEX_2)

    # On extrait les informations de noms
    informations = df.iloc[:, 0].str.extract(REGEX_1, expand=True)

    # les informations d'adresse
    adresse = df.iloc[:, 1].str.extract(REGEX_2, expand=True)

    # on combine tout dans un nouveau tableau
    res = pd.concat(
        [informations, adresse, df.iloc[:, 2]],
        axis=1,
    )

    return (
        res[keep],
        df[~keep]
    )
