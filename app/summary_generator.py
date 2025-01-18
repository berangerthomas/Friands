from mistralai import Mistral
import os
import pandas as pd
from pathlib import Path
from sqlutils import sqlutils
import time


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


def split_text(text, max_length):
    """
    Splits the text into chunks of maximum length.
    """
    words = text.split()
    for i in range(0, len(words), max_length):
        yield " ".join(words[i : i + max_length])


def generate_summary(id_resto, cle_api_mistral, nb_mois=18):
    # on passe la clé en environnement
    os.environ["MISTRAL_API_KEY"] = cle_api_mistral

    # Récupération des avis depuis la base de données
    db_path = Path("data/friands.db")
    bdd = sqlutils(db_path)

    # Déterminer la date du jour puis la date du jour moins 18 mois
    date_min = pd.Timestamp.now() - pd.DateOffset(months=nb_mois)

    # Convertir la date en YYYY-MM-DD
    date_min = date_min.strftime("%Y-%m-%d")

    # Extraire tous les avis dont la date est supérieure à date_min
    success, t_avis = bdd.select(
        f"""
        SELECT r.id_restaurant,
               r.nom AS nom_restaurant,
               a.id_avis,
               a.nom_utilisateur,
               a.note_restaurant,
               a.date_avis,
               a.titre_avis,
               a.contenu_avis,
               a.label
        FROM restaurants r
        JOIN avis a ON r.id_restaurant = a.id_restaurant
        WHERE a.date_avis >= '{date_min}'
        AND r.id_restaurant = {id_resto}
    """
    )

    if not success:
        return (
            False,
            f"Erreur lors de l'extraction des avis depuis la base de données : {t_avis}",
        )

    # Insérer les champs extraits de la base de données dans un dataframe
    df = pd.DataFrame(
        t_avis,
        columns=[
            "id_restaurant",
            "nom_restaurant",
            "id_avis",
            "nom_utilisateur",
            "note_restaurant",
            "date_avis",
            "titre_avis",
            "contenu_avis",
            "label",
        ],
    )

    # joindre tous les avis pour le restaurant
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

    # Application du modèle mistral pour générer le résumé
    model = "pixtral-large-latest"
    model_max_length = 131072
    # Instanciation de la classe MistralAPI
    model_mistral = MistralAPI(model=model)

    query = "Analyser ces avis de clients concernant un restaurant, puis produire un unique résumé de ces avis, court mais riche d'informations. Ne pas produire de liste de points positifs ou négatifs."
    temperature = 0.1

    for index, row in df_grouped.iterrows():
        reviews = row["contenu_avis"]
        chunks = list(
            split_text(reviews, model_max_length)
        )  # Adjust the chunk size as needed
        summaries = []
        for chunk in chunks:
            summary = model_mistral.query(
                f"{query} : '{chunk}'", temperature=temperature
            )
            summaries.append(summary)
        full_summary = " ".join(summaries)

        # Si le résumé est None, on le remplace par un message
        if not full_summary or full_summary == "None":
            full_summary = (
                "Trop peu d'avis ces 18 derniers mois pour générer un résumé fiable."
            )

        # Ajouter le résumé à df_grouped
        df_grouped.loc[index, "resume"] = full_summary

    # Updater les résumés dans la base de données
    for index, row in df_grouped.iterrows():
        success, t_insert = bdd.update(
            table_name="restaurants",
            data={"summary": row["resume"]},
            where=[f"id_restaurant = '{row['id_restaurant']}'"],
        )

        if not success:
            bdd.rollback()
            return (
                False,
                f"Erreur lors de l'insertion du résumé pour le restaurant {row['id_restaurant']} : {t_insert}",
            )
        else:
            bdd.commit()
            return (
                True,
                f"Résumé inséré pour le restaurant {row['id_restaurant']} ({t_insert})",
            )
