import sys 
import os

# Ajouter le chemin du dossier utils au PATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'utils')))

import streamlit as st
from pathlib import Path
import plotly.graph_objects as go
from sqlutils import sqlutils
from function_app import transform_to_df_join

# Redéfinir l'encodage de la sortie standard
sys.stdout.reconfigure(encoding='utf-8')

script_path = Path(__file__).resolve().parent

# Chargement de la base de données
db_path = Path("data/friands2.db")
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
    st.markdown("Avec ***<u>Friands</u>***, naviguer entre les différents restaurants Lyonnais et les comparez-les !", unsafe_allow_html=True)

st.subheader("Utilisation de l'application")
st.markdown("""<p>Cette application a pour but de comparer et d'analyser les commentaires TripAdvisor.
            Vous trouvez quatre onglets : <br>
            - <em>Main</em> : Où vous êtes actuellement ;) pour obtenir des informations générales sur l'application <br>
            - <em>Vue générale : </em>
            - <em>Restaurant</em> : Pour se faire une idée d'un restaurant en particulier <br>
            - <em>Comparaison</em> : Pour comparer plusieurs restaurants entre eux <br>
            - <em>Ajout</em> : Pour ajouter un restaurant à la base de données <br>
            </p>""", unsafe_allow_html=True)

# Charger les données de la table restaurants et la table géograohie
restaurants = transform_to_df_join(db, "SELECT * FROM restaurants, geographie WHERE restaurants.id_restaurant = geographie.id_restaurant;")

# Affciher nombre de restaurants
cols1, cols2 = st.columns([1, 1])
with cols1:
    st.markdown(f"""
        <div style="background-color: #f0f0f0; padding: 10px; border-radius: 5px; text-align: center; width: 100%; margin: auto;">
            <h2 style="color: #333;"><em>Friands</em> compare <span style="color: red;">{len(restaurants)}</span> restaurants 🍴</h2>
        </div>
    """, unsafe_allow_html=True)
with cols2:
    st.markdown(f"""
        <div style="background-color: #f0f0f0; padding: 10px; border-radius: 5px; text-align: center; width: 100%; margin: auto;">
            <h2 style="color: #333;">Et analyse <span style="color: red;">{round(restaurants['restaurants.total_comments'].sum())}</span> commentaires</h2>
        </div>
    """, unsafe_allow_html=True)

st.write("")
st.write("")
st.markdown("""
    <h1 style="font-size: 25px;">Carte interactive des restaurants de Lyon</h1>
""", unsafe_allow_html=True)

# Séparer chaque tag à la virgule et transformer en liste d'éléments distincts
tags_list = restaurants['restaurants.tags'].str.split(",").explode().str.strip()
tags = tags_list.unique()

cols3,cols4 = st.columns([1, 1])
with cols3:
    selected_tags = st.multiselect("Sélectionnez les cuisines qui vous intéressent", tags)

    # Filtrer les restaurants en fonction des tags sélectionnés
    if selected_tags:
        # Filtrer les restaurants qui contiennent un tag sélectionné
        filtered_restaurants = restaurants[restaurants['restaurants.tags'].apply(
            lambda x: all(tag in x for tag in selected_tags)
        )]
    else:
        filtered_restaurants = restaurants
with cols4:
    selected_price = st.multiselect("Choissisez votre fourchette de prix", restaurants["restaurants.price"].unique())

    # Filtrer les restaurants en fonction des tags sélectionnés
    if selected_price:
        # Filtrer les restaurants qui contiennent un tag sélectionné
        filtered_restaurants = filtered_restaurants[filtered_restaurants['restaurants.price'].isin(selected_price)]
    else:
        filtered_restaurants = filtered_restaurants

if filtered_restaurants.shape[0] == 0:
    st.warning("Aucun restaurant ne correspond à votre recherche.")
else : 
    # Initialisation de la carte
    fig = go.Figure()

    # Ajouter les restaurants sur la carte
    fig.add_trace(go.Scattermapbox(
        mode="markers",
        lat=filtered_restaurants['geographie.latitude'],
        lon=filtered_restaurants['geographie.longitude'],
        marker=dict(size=15, color="red"),
        text=filtered_restaurants.apply(lambda row: f"""
                                            🍴 Nom : {row['restaurants.nom']}<br> 
                                            📌 Adresse : {row['geographie.localisation']}<br>
                                            💶 Prix : {row['restaurants.price']}<br> 
                                            ⭐ Note globale : {row['restaurants.note_globale']}<br> 
                                            🍽️ Cuisine : {row['restaurants.tags']}""", axis=1),
        name="Restaurants"
    ))

    # Mettre à jour le style de la carte
    fig.update_layout(
        mapbox_style="open-street-map",
        mapbox_center={"lat": filtered_restaurants['geographie.latitude'].mean(), "lon": filtered_restaurants['geographie.longitude'].mean()},
        mapbox_zoom=12,
        margin={"r":0, "t":0, "l":0, "b":0},
        hoverlabel=dict(
        align="left"  # Aligner le texte à gauche
            )
        )

    # Afficher la carte avec Streamlit
    st.plotly_chart(fig)


st.subheader("A propos")
st.markdown("""
    Cette application a été développé par Béranger THOMAS, Souraya AHMED ABDEREMANE et Lucile PERBET dans le cadre du cours de NLP du master SISE de l'Université Lumière Lyon 2.
""", unsafe_allow_html=True)

