import sys 
import os

# Ajouter le chemin du dossier utils au PATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'utils')))

import streamlit as st
import plotly.express as px
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from pathlib import Path
import pandas as pd
from sqlutils import sqlutils
from function_app import transform_to_df

# Redéfinir l'encodage de la sortie standard
sys.stdout.reconfigure(encoding='utf-8')

# Chargement de la base de données
db_path = Path("data/friands.db")
db = sqlutils(db_path)


# Utiliser des colonnes pour aligner l'image et le texte
col1, col2 = st.columns([1, 2])
with col1:
    st.image("app/assets/logo.png", width=300)
with col2:
    st.write("")  # Ligne vide pour aligner le titre à l'image
    st.write("")  
    st.write("") 
    st.write("")  
    st.title("Bienvenue sur Friands")
st.markdown("Avec ***<u>Friands</u>***, vous pouvez naviguer entre les différents restaurants Lyonnais et les comparer !", unsafe_allow_html=True)


restaurants = transform_to_df("restaurants", db)
avis = transform_to_df("avis", db)
geographie = transform_to_df("geographie", db)

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

# Onglet 4   : Zoom sur un restaurant

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


# Ajouter un champ de texte pour que l'utilisateur entre un message
st.subheader("Entrez l'adresse de du restaurant que vous souhaitez")
user_input = st.text_input("L'adresse se saisit sous cette forme : 30 Cours de Verdun Perrache, 69002 Lyon France","")

# Ajouter un bouton pour récupérer le texte
if st.button("Ajoutez le restaurant") :
    print(user_input)
