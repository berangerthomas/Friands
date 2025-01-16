from transformers import pipeline
from sqlutils import sqlutils
from pathlib import Path
import pandas as pd
import multiprocessing
from concurrent.futures import ThreadPoolExecutor
import sys
import os


def get_label(review, classifier):
    # Appliquer le classifier sur les 1500 premiers caractères de l'avis
    res = classifier(review[:1500])
    # Retourner le label et le score
    return res[0]["label"]


def generate_label(id_restaurant):
    # Récupération des avis depuis la base de données
    bdd = sqlutils(
        Path(os.path.join(os.path.dirname(__file__), "../../data/friands.db")).resolve()
    )
    query = f"SELECT id_avis, contenu_avis FROM avis WHERE id_restaurant = {id_restaurant} AND label IS NULL"
    success, t_avis = bdd.select(query)

    if not success:
        return (
            False,
            f"Erreur lors de l'extraction des avis depuis la base de données : {t_avis}",
        )
    else:
        if len(t_avis) == 0:
            return True, "Aucun avis à analyser."
        else:
            # Insertion des avis dans un dataframe pour plus de souplesse
            df = pd.DataFrame(t_avis, columns=["id_avis", "contenu_avis"])

    # Création du classifier
    classifier = pipeline(
        "sentiment-analysis",
        model="nlptown/bert-base-multilingual-uncased-sentiment",
        tokenizer="nlptown/bert-base-multilingual-uncased-sentiment",
    )

    ## Avec multi-threading
    n_jobs = multiprocessing.cpu_count()
    # start_time = time.time()
    with ThreadPoolExecutor(max_workers=n_jobs) as executor:
        # Utiliser threadpoolexecutor pour faire appel à la fonction get_label et remplir df["label"]
        results = list(
            executor.map(
                get_label, df["contenu_avis"], [classifier] * len(df["contenu_avis"])
            )
        )

    df["label"] = results

    # Insérer les labels calculés dans la base de données avec update
    reussi = 0

    for index, row in df.iterrows():
        success, t_insert = bdd.update(
            table_name="avis",
            data={"label": row["label"].split()[0]},
            where=[f"id_avis = '{row['id_avis']}'"],
        )

        if success:
            reussi += 1
        else:
            break
    if reussi != len(df):
        bdd.rollback()
        return (
            False,
            f"Erreur lors de la mise à jour du label {row['id_avis']} : {t_insert}. Toutes les modifications ont été annulées.",
        )
    else:
        bdd.commit()
        return True, f"{reussi} avis mis à jour avec succès."
