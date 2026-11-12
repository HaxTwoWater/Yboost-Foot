"""Fonctions de nettoyage des données de matchs internationaux.

Chaque fonction prend un DataFrame et renvoie une NOUVELLE copie nettoyée :
on ne modifie jamais le tableau d'origine.
"""

import re

import pandas as pd

# Une minute de but au-delà de 130 est impossible (90 min + prolongation + arrêts de jeu)
MINUTE_MIN = 1
MINUTE_MAX = 130

COLONNES_ATTENDUES = {
    "results": ["date", "home_team", "away_team", "home_score", "away_score",
                "tournament", "city", "country", "neutral"],
    "goalscorers": ["date", "home_team", "away_team", "team", "scorer",
                    "minute", "own_goal", "penalty", "assist"],
    "shootouts": ["date", "home_team", "away_team", "winner", "first_shooter"],
    "former_names": ["current", "former", "start_date", "end_date"],
}


def normaliser_entetes(df: pd.DataFrame) -> pd.DataFrame:
    """Met les noms de colonnes en snake_case : minuscules, sans espaces ni accents parasites."""
    nouveaux = [re.sub(r"[^0-9a-z]+", "_", str(c).strip().lower()).strip("_") for c in df.columns]
    return df.set_axis(nouveaux, axis=1)


def verifier_colonnes(df: pd.DataFrame, nom: str) -> None:
    """Lève une erreur claire si une colonne attendue manque."""
    manquantes = set(COLONNES_ATTENDUES[nom]) - set(df.columns)
    if manquantes:
        raise ValueError(f"{nom} : colonnes manquantes {sorted(manquantes)}")


def nettoyer_texte(df: pd.DataFrame) -> pd.DataFrame:
    """Enlève les espaces en trop et transforme les textes vides en valeurs manquantes."""
    propre = df.copy()
    for col in propre.select_dtypes(include=["object", "string"]).columns:
        texte = propre[col].astype("string").str.strip().str.replace(r"\s+", " ", regex=True)
        propre[col] = texte.replace("", pd.NA)
    return propre


def convertir_dates(df: pd.DataFrame, colonnes: list[str]) -> pd.DataFrame:
    """Convertit en vraies dates. Une date illisible devient NaT (manquante)."""
    propre = df.copy()
    for col in colonnes:
        propre[col] = pd.to_datetime(propre[col], errors="coerce", format="%Y-%m-%d")
    return propre


def convertir_booleens(df: pd.DataFrame, colonnes: list[str]) -> pd.DataFrame:
    """Accepte True/False, 'TRUE'/'false', 1/0 et renvoie de vrais booléens."""
    correspondance = {"true": True, "false": False, "1": True, "0": False}
    propre = df.copy()
    for col in colonnes:
        propre[col] = propre[col].astype("string").str.strip().str.lower().map(correspondance)
    return propre


def preparer(df: pd.DataFrame, nom: str, colonnes_dates: list[str]) -> pd.DataFrame:
    """Étapes communes : en-têtes, vérification des colonnes, textes, dates."""
    propre = normaliser_entetes(df)
    verifier_colonnes(propre, nom)
    return convertir_dates(nettoyer_texte(propre), colonnes_dates)


def nettoyer_results(df: pd.DataFrame) -> pd.DataFrame:
    """Matchs : types corrects, lignes impossibles retirées, doublons exacts retirés."""
    propre = preparer(df, "results", ["date"])
    propre = convertir_booleens(propre, ["neutral"])
    for col in ["home_score", "away_score"]:
        propre[col] = pd.to_numeric(propre[col], errors="coerce").astype("Int64")

    obligatoires = ["date", "home_team", "away_team", "home_score", "away_score"]
    valide = (
        propre[obligatoires].notna().all(axis=1)
        & (propre["home_team"] != propre["away_team"])
        & (propre["home_score"] >= 0)
        & (propre["away_score"] >= 0)
    )
    return propre[valide].drop_duplicates().reset_index(drop=True)


def nettoyer_goalscorers(df: pd.DataFrame) -> pd.DataFrame:
    """Buteurs. ATTENTION : deux lignes identiques peuvent être deux vrais buts
    (même joueur, minute inconnue), donc on NE supprime PAS les doublons ici."""
    propre = preparer(df, "goalscorers", ["date"])
    propre = convertir_booleens(propre, ["own_goal", "penalty"])
    propre["minute"] = pd.to_numeric(propre["minute"], errors="coerce")
    # Minute hors limites : on la considère comme inconnue plutôt que de perdre le but
    hors_limites = ~propre["minute"].between(MINUTE_MIN, MINUTE_MAX)
    propre["minute"] = propre["minute"].mask(hors_limites).astype("Int64")

    equipe_du_match = (propre["team"] == propre["home_team"]) | (propre["team"] == propre["away_team"])
    valide = propre[["date", "home_team", "away_team", "team"]].notna().all(axis=1) & equipe_du_match
    return propre[valide].reset_index(drop=True)


def nettoyer_shootouts(df: pd.DataFrame) -> pd.DataFrame:
    """Tirs au but : le vainqueur doit être une des deux équipes."""
    propre = preparer(df, "shootouts", ["date"])
    vainqueur_ok = (propre["winner"] == propre["home_team"]) | (propre["winner"] == propre["away_team"])
    valide = propre[["date", "home_team", "away_team", "winner"]].notna().all(axis=1) & vainqueur_ok
    return propre[valide].drop_duplicates().reset_index(drop=True)


def nettoyer_former_names(df: pd.DataFrame) -> pd.DataFrame:
    """Anciens noms de pays : la date de début doit précéder la date de fin."""
    propre = preparer(df, "former_names", ["start_date", "end_date"])
    valide = propre.notna().all(axis=1) & (propre["start_date"] <= propre["end_date"])
    return propre[valide].drop_duplicates().reset_index(drop=True)
