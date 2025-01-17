# Friands
Finding Restaurants, Insights And Notably Delectable Spots


## Architecture projet temp


```r
FRIANDS/
├── app/
│   ├── __init__.py
│   ├── main.py               # Fichier principal Streamlit 
│   ├── pages/                # Pages multiples pour app
│   │   ├── __init__.py
│   │   ├── restaurant_analysis.py  # Page pourintra-restaurant
│   │   └── comparison.py          # Page pour l'analyse inter-restaurants
│   ├── components/           # Composants réutilisables
│   │   ├── __init__.py
│   │   └── map_component.py      # Carte interactive
│   └── assets/               # Images et fichiers statiques
│       └── logo.png
│
├── data/
│   ├── raw/                  # Données brutes récupérées (via )
│   │   └── raw_data.json
│   ├── processed/            # Données structurées pour le traitement
│   │   └── processed_data.db
│   ├── open_data/            # Données publiques complémentaires
│   │   └── socio_economic_data.csv
│   └── samples/              # Données d'exemple pour tests
│       └── sample_reviews.csv
│
├── docker/
│   ├── Dockerfile            # Dockerfile pour déploiement
│   └── docker-compose.yml    # Configuration de services 
├── notebooks/
│   ├── exploration.ipynb     # Analyse exploratoire des données
│   └── models_training.ipynb # Entraînement des modèles NLP
│
├── src/
│   ├── scraping/
│   │   ├── __init__.py
│   │   ├── tripadvisor_scraper.py   # Scraping des avis
│   │   └── api_data_fetcher.py      # Appels aux APIs open data
│   ├── processing/
│   │   ├── __init__.py
│   │   ├── data_cleaning.py         # Nettoyage des données
│   │   └── database_handler.py      # Gestion de la base de données
│   ├── nlp/
│   │   ├── __init__.py
│   │   ├── sentiment_analysis.py    # Analyse des sentiments
│   │   └── summary_generator.py     # Génération de résumés
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── sqlutils.py              # Classe de manipulation de la base Sqlite
│   │   └── schemaDB.py              # Dictionnaire de définition des tables
├── requirements.txt           # Dépendances Python
├── README.md                  # Documentation du projet
└── report/
    ├── rapport.tex            # Rapport LaTeX
    ├── figures/               # Graphiques pour le rapport
    └── references.bib         # Bibliographie

```
