# Yboost-Foot – Qui va gagner la Coupe du monde 2030 ?

Projet Yboost B2 IA & Data (Ynov Toulouse). L'objectif est de prédire si une équipe nationale gagne un match, puis de simuler la Coupe du monde 2030 à partir de ces prédictions pour estimer les chances de chaque pays.

## Prérequis

- Python 3.10 ou plus récent

## Installation

```bash
git clone https://github.com/HaxTwoWater/Yboost-Foot.git
cd Yboost-Foot
python -m venv .venv
```

Activer l'environnement virtuel :

- Windows : `.venv\Scripts\activate`
- macOS / Linux : `source .venv/bin/activate`

Puis installer les dépendances :

```bash
pip install -r requirements.txt
```

## Récupérer les données

```bash
python src/download.py
```

Les fichiers sont téléchargés dans `data/raw/`. Les données ne sont pas versionnées (`data/` est dans le `.gitignore`) : chaque membre les récupère avec ce script.

## Les données

| | |
|---|---|
| Source | [international_results](https://github.com/martj42/international_results), par Mart Jürisoo |
| Contenu | Matchs internationaux masculins (hors JO et équipes B) |
| Période | 1872 à aujourd'hui, mis à jour régulièrement |

## Structure du projet

```
Yboost-Foot/
├── app.py               # dashboard Streamlit (à venir)
├── requirements.txt     # dépendances Python
├── data/
│   ├── raw/             # fichiers téléchargés, non modifiés
│   └── processed/       # tableaux préparés
├── notebooks/           # exploration
└── src/
    └── download.py      # téléchargement des données
```
