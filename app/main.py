import sys 
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'utils')))

import streamlit as st
import plotly.express as px
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from pathlib import Path
import pandas as pd
from sqlutils import sqlutils

# Chargement de la base de données
db_path = Path("data/friands.db")
db = sqlutils(db_path)

st.title("Bienvenue sur Friand !")
st.markdown("A travers cette application, vous pourrez naviguer entre les différents restaurants Lyonnais et les comparer !")

# Colonnes à récupérer de la base de données
cols = ["prix_moyen", "restaurant", "cuisine", "adresse", "note", "nombre_avis", "avis"]

# Charger les données dans un DataFrame
restaurants_data = db.select("users", columns=cols)
restaurants = pd.DataFrame(restaurants_data, columns=cols)

# Extraire l'arrondissement à partir de l'adresse
restaurants["Arrondissement"] = restaurants["adresse"].str.extract(r"(\d{5})")[0].str[-2:]

# Ajouter des colonnes de latitude et longitude
geolocator = Nominatim(user_agent="restaurant_locator")
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
restaurants["location"] = restaurants["adresse"].apply(geocode)
restaurants["latitude"] = restaurants["location"].apply(lambda loc: loc.latitude if loc else None)
restaurants["longitude"] = restaurants["location"].apply(lambda loc: loc.longitude if loc else None)

# Supprimer la colonne location
restaurants.drop(columns="location", inplace=True)

# Création des onglets
tabs = st.tabs(["Comparaison inter-Restaurants", "Analyse des notes", "Analyse des commentaires","Zoom sur un restaurant","Table de données", "Ajout d'un restaurant"])
selected_tab = st.selectbox("Sélectionnez un onglet", tabs)

# Onglet 1 : Carte et Prix moyens
if tabs == "Comparaison inter-Restaurants":

    # Calculer le prix moyen de la ville
    prix_moyen_ville = restaurants["prix_moyen"].mean()

    # Ajouter un graphique interactif pour comparer les prix moyens
    st.subheader("Prix moyens par restaurant")
    fig2 = px.scatter(
        restaurants, 
        x="restaurant", 
        y="prix_moyen", 
        size="nombre_avis", 
        color="cuisine", 
        title="Prix moyen des restaurants",
        labels={"prix_moyen": "Prix moyen (€)"},
        hover_data=["note"]
    )

    # Ajouter une ligne pour le prix moyen de la ville
    fig2.add_hline(y=prix_moyen_ville, line_dash="dot", line_color="red", 
                    annotation_text=f"Prix moyen de la ville: {prix_moyen_ville:.2f} €", 
                    annotation_position="top left")

    st.plotly_chart(fig2)

    # Ajouter une carte interactive des notes moyennes par arrondissement
    # st.subheader("Carte interactive des arrondissements")
    # # Calculer la note moyenne par arrondissement
    # arrondissement_avg_note = restaurants.groupby("Arrondissement", as_index=False).agg({"note": "mean", "latitude": "first", "longitude": "first"})

    # fig3 = px.scatter_mapbox(
    #     arrondissement_avg_note,
    #     lat="latitude",
    #     lon="longitude",
    #     color="note",
    #     size="note",
    #     hover_name="Arrondissement",
    #     title="Notes moyennes par arrondissement",
    #     mapbox_style="open-street-map",
    #     zoom=12
    # )
    # fig3.update_traces(marker=dict(sizemin=8))  # la taille minimale des marqueurs
    # st.plotly_chart(fig3)

# Onglet 2 : Analyse des commentaires
with tabs[1]:
    st.subheader("Analyse des commentaires")
    st.markdown("Insérer nos résultats obtenus grâce au NLP/LLM why not.")

    st.subheader("Analyse des sentiments")

    st.subheader("Analyse du résumer global de tous les avis")

    st.subheader("Corrélation de la note à l'avis")

    st.subheader("Ce dont les clients parlent le plus et en quelle terme")

# Onglet 3 : Analyse des notes
with tabs[2]:
    # Ajouter un graphique interactif pour la note des restaurants
    st.subheader("Notes des restaurants")
    fig1 = px.bar(
        restaurants, 
        x="restaurant", 
        y="note", 
        title="Notes moyennes des restaurants",
        labels={"note": "Note moyenne"}
    )
    st.plotly_chart(fig1)

# Onglet 4   : Zoom sur un restaurant
with tabs[3]:
    # Ajouter un selectbox pour choisir un restaurant
    st.subheader("Sélectionnez un restaurant")
    selected_restaurant = st.selectbox("Choisissez un restaurant", restaurants["restaurant"].unique())

    # Filtrer les données en fonction du restaurant sélectionné
    selected_data = restaurants[restaurants["restaurant"] == selected_restaurant]
    
    # Afficher les informations du restaurant sélectionné
    st.write(f"### {selected_restaurant}")
    st.write(f"**Cuisine**: {selected_data['cuisine'].values[0]}")
    st.write(f"**Adresse**: {selected_data['adresse'].values[0]}")
    st.write(f"**Prix moyen**: {selected_data['prix_moyen'].values[0]} €")
    st.write(f"**Note moyenne**: {selected_data['note'].values[0]}")
    st.write(f"**Nombre d'avis**: {selected_data['nombre_avis'].values[0]}")

    # Afficher les avis du restaurant
    st.write("### Avis des clients")
    st.write(selected_data["avis"])

    st.write("### Affichez résumé des commentaires")

# Onglet 5 : Table de données
with tabs[4]:
    # Ajouter une table des données
    st.subheader("Données")
    st.dataframe(restaurants)
with tabs[5]:

# Ajouter un champ de texte pour que l'utilisateur entre un message
    st.subheader("Entrez l'adresse de du restaurant que vous souhaitez")
    user_input = st.text_input("L'adresse se saisit sous cette forme : 30 Cours de Verdun Perrache, 69002 Lyon France","")
    
    # Ajouter un bouton pour récupérer le texte
    if st.button("Ajoutez le restaurant") :
        print(user_input)
