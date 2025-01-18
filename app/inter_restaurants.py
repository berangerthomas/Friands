from pathlib import Path
from sqlutils import sqlutils
import pandas as pd
import string
import matplotlib.pyplot as plt
import requests
import spacy
import nltk
import numpy as np
from sklearn.decomposition import PCA
import plotly.express as px
import gensim 
import streamlit as st
from gensim.models import Word2Vec

def clean_text(text, stopwords=set()) -> str:
    """
    Clean the given text by converting to lowercase, removing ponctuation and numbers, and removing specified stopwords.

    Args:
        text (str): The input text to be cleaned.

    Returns:
        str: The cleaned text.
    """
    # Table de transcription de la ponctuation et des chiffres
    translation_table = str.maketrans(
        {char: " " for char in string.punctuation + string.digits}
    )
    text = text.lower().translate(translation_table)
    return " ".join(mot for mot in text.split() if mot not in stopwords)


# Fonction de lemmatisation
def lemmatize_text(text, nlp):
    # Lemmatisation
    doc = nlp(text)
    lemmatized = [token.lemma_ for token in doc]

    return " ".join(lemmatized)


# Fonction pour retirer les stop words
def remove_stopwords(text, stop_words):
    return " ".join(mot for mot in text.split() if mot not in stop_words)


def plot_restaurant_similarities():
    # Accès à la base de données
    db_path = Path("data/friands.db")
    bdd = sqlutils(db_path)

    # Récupération des avis de tous les restaurants
    query = f"SELECT avis.id_restaurant, avis.contenu_avis, restaurants.nom FROM avis JOIN restaurants ON avis.id_restaurant = restaurants.id_restaurant"
    success, t_avis = bdd.select(query)

    if not success:
        print("Erreur lors de l'extraction des avis depuis la base de données")
        print(t_avis)
    else:
        print(
            f"Extraction de {len(t_avis)} enregistrements depuis la base de données réussie"
        )
    
    # Insérer les champs extraits de la base de données dans un dataframe
    df = pd.DataFrame(
        t_avis,
        columns=[
            "id_restaurant",
            "contenu_avis",
            "nom",
        ],
    )

    # Récupération d'une liste de mots vides
    url = "https://raw.githubusercontent.com/stopwords-iso/stopwords-fr/master/stopwords-fr.txt"
    response = requests.get(url)
    if response.status_code == 200:
        mots_vides_github = response.text.splitlines()
    else:
        st.write("Erreur lors de la récupération des mots vides depuis l'URL")

    # Nettoyage des mots vides :
    #     - suppression des caractères diacritiques
    #     - conversion en minuscules
    #     - suppression des chiffres
    mots_vides_github = [clean_text(mot) for mot in mots_vides_github]

    # Application de la fonction de nettoyage sur le contenu des avis
    df["avis_clean"] = df["contenu_avis"].apply(
        lambda x: clean_text(x, mots_vides_github)
    )

    # Chargement du modèle français
    nlp = spacy.load("fr_core_news_sm")
    # Application de la fonction de lemmatisation sur le contenu des avis
    df[f"avis_lemmatized"] = df["avis_clean"].apply(
        lambda avis: lemmatize_text(avis, nlp)
    )

    # retirer les stop words avec nltk
    nltk.download("stopwords")
    from nltk.corpus import stopwords

    stop_words = stopwords.words("french")

    # Application de la fonction de suppression des stop words sur le contenu des avis
    df["avis_no_stopwords"] = df["avis_lemmatized"].apply(
        lambda avis: remove_stopwords(avis, stop_words)
    )



    # Convert text data to list of words for each review
    corpus_liste = [review.split() for review in df["avis_no_stopwords"]]
    model = Word2Vec(
        corpus_liste, vector_size=3, window=3, min_count=1, epochs=10, seed=1
    )

    # Train Word2Vec model on the corpus
    model.build_vocab(corpus_liste)
    model.train(corpus_liste, total_examples=model.corpus_count, epochs=model.epochs)

    # Get average vector for each restaurant
    restaurant_vectors = {}
    # Précalculer tous les vecteurs de mots
    word_to_vec = {word: model.wv[word] for word in model.wv.index_to_key}

    for restaurant, group in df.groupby("nom"):
        all_words = " ".join(group["avis_no_stopwords"]).split()
        vectors = [word_to_vec[word] for word in all_words if word in word_to_vec]
        if vectors:
            restaurant_vectors[restaurant] = np.mean(vectors, axis=0)

    # Reduce vectors to 3D
    names = list(restaurant_vectors.keys())
    vecs = list(restaurant_vectors.values())
    pca = PCA(n_components=3)
    reduced = pca.fit_transform(vecs)

    df_plot = pd.DataFrame(
        {
            "Restaurant": names,
            "Dim1": reduced[:, 0],
            "Dim2": reduced[:, 1],
            "Dim3": reduced[:, 2],
        }
    )

    # Assign colors to each restaurant
    unique_restaurants = df_plot["Restaurant"].unique()
    colors = plt.cm.rainbow(np.linspace(0, 1, len(unique_restaurants)))
    color_map = {
        restaurant: color for restaurant, color in zip(unique_restaurants, colors)
    }
    df_plot["Color"] = df_plot["Restaurant"].map(color_map)

    fig = px.scatter_3d(
        df_plot,
        x="Dim1",
        y="Dim2",
        z="Dim3",
        text="Restaurant",
        color="Restaurant",
        title="Restaurant Similarity (3D)",
    )

    # Update layout for larger size
    fig.update_layout(
        width=1000,  # Width in pixels
        height=800,  # Height in pixels
        scene=dict(aspectmode="cube", aspectratio=dict(x=1, y=1, z=1)),
        margin=dict(l=0, r=0, b=0, t=30),  # Reduce margins
    )

    fig.update_traces(textposition="top center")
    st.plotly_chart(fig, use_container_width=True)

