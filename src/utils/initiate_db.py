import multiprocessing
import os
import pandas as pd
import time
from concurrent.futures import ThreadPoolExecutor
from mistralai import Mistral
from pathlib import Path
from schemaDB import schemaDB
from sqlutils import sqlutils
from transformers import pipeline

"""
Ce script réalise les trois grandes étapes d'initialisation de la base de données :
    1. Création du schéma et importation des données initiales depuis des fichiers csv
    2. Génération de résumés pour les restaurants à partir des avis des clients
    3. Génération de labels pour les avis des clients à partir de leur contenu

Il faut compter 15 minutes pour l'exécution complète de ce script.

Penser à remplir la clé API pour Mistral ci-dessous.
"""

os.environ["MISTRAL_API_KEY"] = "7PdL6AoyIBJDNlZKZPQzEOBpReehekdE"

###################################
#### INITIALISATION DE LA BDD #####
###################################
# 1. Chemin de la base de données et des fichiers csv à importer
# Chemin du script
script_path = Path(__file__).resolve()

# Chemin de la base de données
db_path = Path(script_path).parents[1] / "data" / "friands.db"

# Définir les fichiers csv à importer
csv_sources = [
    Path(script_path).parents[1] / "data" / fic
    for fic in ["avis_cleaned.csv", "restaurants.csv", "Geographie.csv"]
]

# # 2. Création des tables à partir de schemaDB
db = sqlutils(db_path)
for k, v in schemaDB.items():
    success, message = db.create_table(k, v)
    if not success:
        print(f"Erreur lors de la création de la table '{k}': {message}")
    else:
        print(f"Table '{k}' créée avec succès : {message}")

# 3. Insérer les données à partir des fichiers csv
for fic in csv_sources:
    success, message = db.load_from_csv(
        fic.name.split("_")[0].split(".")[0].lower(), fic
    )
    if success:
        db.commit()
        print(message)
    else:
        db.rollback()
        print(f"Erreur lors de l'importation du fichier {fic} : '{message}'")


#################################
#### GÉNÉRATION DES RÉSUMÉS #####
#################################
# 1. Classe pour interagir avec l'API MistralAI
class MistralAPI:
    """
    A client for interacting with the MistralAI API.

    Attributes:
        client (Mistral): The Mistral client instance.
        model (str): The model to use for queries.
    """

    def __init__(self, model: str) -> None:
        """
        Initializes the MistralAPI with the given model.

        Args:
            model (str): The model to use for queries.

        Raises:
            ValueError: If the MISTRAL_API_KEY environment variable is not set.
        """
        api_key = os.getenv("MISTRAL_API_KEY")
        if not api_key:
            raise ValueError(
                "No MISTRAL_API_KEY as environment variable, please set it!"
            )
        self.client = Mistral(api_key=api_key)
        self.model = model

    def query(self, query: str, temperature: float = 0.5) -> str:
        """
        Sends a query to the MistralAI API and returns the response.

        Args:
            query (str): The input query to send to the model.
            temperature (float, optional): The temperature parameter for controlling
                                          the randomness of the output. Defaults to 0.5.

        Returns:
            str: The response from the API.
        """
        chat_response = self.client.chat.complete(
            model=self.model,
            temperature=temperature,
            messages=[
                {
                    "role": "user",
                    "content": query,
                },
            ],
        )
        return chat_response.choices[0].message.content


# 2. Récupération des avis depuis la base de données

# Déterminer le chemin du script
script_path = Path().resolve()

# # Select des avis depuis la base de données et depuis le chemin du script
bdd = sqlutils(script_path / "../../data/friands.db")
# Déterminer la date du jour puis la date du jour moins 18 mois
date_min = pd.Timestamp.now() - pd.DateOffset(months=18)
# Convertir la date en YYYY-MM-DD
date_min = date_min.strftime("%Y-%m-%d")
print(f"Date minimum: {date_min}")
# Extraire tous les avis dont la date est supérieure à date_min
query = f"SELECT * FROM avis WHERE date_avis >= '{date_min}'"
success, t_avis = bdd.select(query)

if not success:
    print("Erreur lors de l'extraction des avis depuis la base de données")
    print(t_avis)
else:
    print(
        f"Extraction de {len(t_avis)} enregistrements depuis la base de données réussie"
    )

# # Insérer les champs extraits de la base de données dans un dataframe
df = pd.DataFrame(
    t_avis,
    columns=[
        "id_avis",
        "id_restaurant",
        "nom_utilisateur",
        "note_restaurant",
        "date_avis",
        "titre_avis",
        "contenu_avis",
        "label",
    ],
)

# Sélectionner les id_restaurant et les noms des restaurants depuis la table restaurant
success, t_resto = bdd.select("SELECT id_restaurant, nom FROM restaurants")

if not success:
    print(
        "Erreur lors de l'extraction des informations des restaurants depuis la base de données"
    )
    print(t_resto)
else:
    # Ajouter les infos au dataframe df
    df_resto = pd.DataFrame(t_resto, columns=["id_restaurant", "nom_restaurant"])
    df = pd.merge(df, df_resto, on="id_restaurant")

# joindre tous les avis pour un restaurant donné
df_grouped = (
    df.groupby("id_restaurant")
    .agg(
        {
            "nom_restaurant": "first",
            "contenu_avis": lambda x: " --- ".join(x),
        }
    )
    .reset_index()
)

# 3. Appel à l'API Mistral pour générer les résumés
# Choix du modèle
model = "pixtral-large-latest"
# Instanciation de la classe MistralAPI
model_mistral = MistralAPI(model=model)
# Définition du nombre de caractère max
model_max_length = [m.max_context_length for m in liste_modeles_tri if m.id == model][0]
# Résumé
print(f"Modèle sélectionné : {model}. Longueur de prompt maximale : {model_max_length}")


def split_text(text, max_length):
    """
    Splits the text into chunks of maximum length.
    """
    words = text.split()
    for i in range(0, len(words), max_length):
        yield " ".join(words[i : i + max_length])


query = "Analyser ces avis de clients concernant un restaurant, puis produire un unique résumé de ces avis, court mais riche d'informations. Ne pas produire de liste de points positifs ou négatifs, ni ."
temperature = 0.1

for index, row in df_grouped.iterrows():
    reviews = row["contenu_avis"]
    chunks = list(
        split_text(reviews, model_max_length)
    )  # Adjust the chunk size as needed
    summaries = []
    for chunk in chunks:
        summary = model_mistral.query(f"{query} : '{chunk}'", temperature=temperature)
        summaries.append(summary)
    full_summary = " ".join(summaries)
    print(f"Restaurant: {row['nom_restaurant']}")
    print(f"Résumé: {full_summary}")
    print("\n")

    # Ajouter le résumé à df_grouped
    df_grouped.loc[index, "resume"] = full_summary

    # Marquer une pause de 10 secondes pour ne pas saturer l'API
    time.sleep(10)

# 4. Updater les résumés dans la base de données
for index, row in df_grouped.iterrows():
    success, t_insert = bdd.update(
        table_name="restaurants",
        data={"summary": row["resume"]},
        where=[f"id_restaurant = '{row['id_restaurant']}'"],
    )

    if not success:
        bdd.rollback()
        print(
            f"Erreur lors de l'insertion du résumé pour le restaurant {row['id_restaurant']} : {t_insert}"
        )
        print(t_insert)
    else:
        bdd.commit()
        print(f"Résumé inséré pour le restaurant {row['id_restaurant']} ({t_insert})")


##################################
##### GÉNÉRATION DES LABELS ######
##################################
# 1. Extraction des informations à traiter
query = f"SELECT avis.*, restaurants.nom FROM avis JOIN restaurants ON avis.id_restaurant = restaurants.id_restaurant"
success, t_avis = bdd.select(query)

if not success:
    print("Erreur lors de l'extraction des avis depuis la base de données")
    print(t_avis)
else:
    print(
        f"Extraction de {len(t_avis)} enregistrements depuis la base de données réussie"
    )

# # Insérer les champs extraits de la base de données dans un dataframe
df = pd.DataFrame(
    t_avis,
    columns=[
        "id_avis",
        "id_restaurant",
        "nom_utilisateur",
        "note_restaurant",
        "date_avis",
        "titre_avis",
        "contenu_avis",
        "label",
        "nom",
    ],
)

# 2. Création du classifier
classifier = pipeline(
    "sentiment-analysis",
    model="nlptown/bert-base-multilingual-uncased-sentiment",
    tokenizer="nlptown/bert-base-multilingual-uncased-sentiment",
)


# 3. Application multi-threadée du classifier sur les avis
# Fonction de traitement des avis
def process_review(review):
    # Appliquer le classifier sur les 1500 premiers caractères de l'avis
    res = classifier(review[:1500])
    # Retourner le label et le score
    return res[0]["label"], res[0]["score"]


n_jobs = multiprocessing.cpu_count()
with ThreadPoolExecutor(max_workers=n_jobs) as executor:
    results = executor.map(process_review, df["contenu_avis"])
df[["label", "score"]] = pd.DataFrame(results)

# 4. Insérer les labels calculés dans la base de données
for index, row in df.iterrows():
    success, t_insert = bdd.update(
        table_name="avis",
        data={"label": row["label"].split()[0]},
        where=[f"id_avis = '{row['id_avis']}'"],
    )

    if not success:
        bdd.rollback()
        print(f"Erreur lors de la mise à jour du label {row['id_avis']} : {t_insert}")
        print(t_insert)
    else:
        bdd.commit()
        print(f"Label inséré pour l'avis {row['id_avis']} ({t_insert})")
