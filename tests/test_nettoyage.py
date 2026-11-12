import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from nettoyage import (
    convertir_booleens,
    nettoyer_former_names,
    nettoyer_goalscorers,
    nettoyer_results,
    nettoyer_shootouts,
    nettoyer_texte,
    normaliser_entetes,
)


def match(**modifs):
    ligne = {"date": "2022-12-18", "home_team": "Argentina", "away_team": "France",
             "home_score": 3, "away_score": 3, "tournament": "FIFA World Cup",
             "city": "Lusail", "country": "Qatar", "neutral": True}
    ligne.update(modifs)
    return ligne


def test_normaliser_entetes_met_en_snake_case():
    df = pd.DataFrame(columns=[" Home Team ", "AWAY-SCORE", "date"])
    assert list(normaliser_entetes(df).columns) == ["home_team", "away_score", "date"]


def test_nettoyer_texte_enleve_espaces_et_vides():
    df = pd.DataFrame({"pays": ["  France  ", "", "Côte  d'Ivoire"]})
    propre = nettoyer_texte(df)
    assert propre["pays"].iloc[0] == "France"
    assert pd.isna(propre["pays"].iloc[1])
    assert propre["pays"].iloc[2] == "Côte d'Ivoire"


def test_convertir_booleens_accepte_plusieurs_formats():
    df = pd.DataFrame({"neutral": ["TRUE", "false", "1", "0"]})
    assert convertir_booleens(df, ["neutral"])["neutral"].tolist() == [True, False, True, False]


def test_nettoyer_results_retire_les_lignes_impossibles_et_doublons():
    df = pd.DataFrame([
        match(),
        match(),                                  # doublon exact
        match(home_team="France"),                # une équipe contre elle-même
        match(home_score=-1),                     # score négatif
        match(date="pas une date"),               # date illisible
        match(away_score=None),                   # score manquant
    ])
    propre = nettoyer_results(df)
    assert len(propre) == 1
    assert propre["date"].dtype.kind == "M"
    assert str(propre["home_score"].dtype) == "Int64"


def test_nettoyer_results_ne_modifie_pas_l_original():
    df = pd.DataFrame([match(), match()])
    nettoyer_results(df)
    assert len(df) == 2


def test_nettoyer_goalscorers_garde_les_vrais_doublons_et_corrige_minute():
    but = {"date": "1963-11-26", "home_team": "Ghana", "away_team": "Ethiopia",
           "team": "Ghana", "scorer": "Edward Acquah", "minute": None,
           "own_goal": False, "penalty": False, "assist": None}
    df = pd.DataFrame([but, but, {**but, "minute": 300}, {**but, "team": "Brazil"}])
    propre = nettoyer_goalscorers(df)
    assert len(propre) == 3                      # les 2 doublons restent, Brazil part
    assert propre["minute"].isna().all()         # 300 devient inconnue


def test_nettoyer_shootouts_verifie_le_vainqueur():
    df = pd.DataFrame([
        {"date": "2022-12-18", "home_team": "Argentina", "away_team": "France",
         "winner": "Argentina", "first_shooter": "France"},
        {"date": "2022-12-18", "home_team": "Argentina", "away_team": "France",
         "winner": "Brazil", "first_shooter": None},
    ])
    assert len(nettoyer_shootouts(df)) == 1


def test_nettoyer_former_names_refuse_dates_inversees():
    df = pd.DataFrame([
        {"current": "Benin", "former": "Dahomey", "start_date": "1959-11-08", "end_date": "1975-11-30"},
        {"current": "X", "former": "Y", "start_date": "2000-01-01", "end_date": "1990-01-01"},
    ])
    assert nettoyer_former_names(df)["current"].tolist() == ["Benin"]


def test_colonne_manquante_donne_une_erreur_claire():
    with pytest.raises(ValueError, match="colonnes manquantes"):
        nettoyer_shootouts(pd.DataFrame({"date": ["2022-12-18"]}))
