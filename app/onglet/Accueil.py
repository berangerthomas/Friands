import streamlit as st
import plotly.graph_objects as go
from function_app import (
    get_db,
    transform_to_df_join,
    selected_tags_any,
    retrieve_filter_list,
)

# Chargement de la base de données
db = get_db()

# Utiliser des colonnes pour aligner l'image et le texte
col1, col2, col3 = st.columns([4, 2, 1])

# Titre principal
with col1:
    st.markdown(
        "<h1 style='font-size: 60px; color: #3C6E47;'>Bienvenue sur <span style='font-weight: bold;'>Friands</span> !</h1>",
        unsafe_allow_html=True,
    )

with col2:
    st.write("")  # Laisser vide ou st.empty() pour occuper l'espace au milieu

with col3:
    st.write("")
    # st.image("assets/logo.png", width=150)

st.markdown(
    "<p style='font-size: 28px; color: #6A9A7D;'><em>Finding Restaurants, Insights And Notably Delectable Spots</em></p>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='font-size: 22px; color: #6A9A7D;'>Avec <u><strong>Friands</strong></u>, explorez et comparez les meilleurs restaurants Lyonnais</p>",
    unsafe_allow_html=True,
)


# Charger les données de la table restaurants et la table géographie
restaurants = transform_to_df_join(
    db,
    f"""SELECT avis.id_avis, restaurants.tags, restaurants.price, restaurants.nom, restaurants.note_globale, geographie.localisation, geographie.latitude, geographie.longitude 
                                   FROM restaurants, geographie, avis 
                                   WHERE restaurants.id_restaurant = geographie.id_restaurant
                                   AND restaurants.id_restaurant = avis.id_restaurant;""",
)

# Afficher le nombre de restaurants et de commentaires
cols1, cols2 = st.columns([1, 1])

with cols1:
    st.markdown(
        f"""
        <div style="background: linear-gradient(to right, #b5e48c, #f0f9b2); padding: 20px; border-radius: 15px; text-align: center; width: 100%; margin: auto;">
            <h2 style="color: #333; font-family: 'Arial', sans-serif; font-weight: 500; font-size: 22px;">
                <em>Friands</em> compare <span style="color: #f09e3f;">{restaurants['restaurants.nom'].nunique()}</span> restaurants 🍴
            </h2>
        </div>
    """,
        unsafe_allow_html=True,
    )

with cols2:
    st.markdown(
        f"""
        <div style="background: linear-gradient(to right, #ffd166, #f0f9b2); padding: 20px; border-radius: 15px; text-align: center; width: 100%; margin: auto;">
            <h2 style="color: #333; font-family: 'Arial', sans-serif; font-weight: 500; font-size: 22px;">
                Et analyse <span style="color: #f09e3f;">{len(restaurants)}</span> commentaires
            </h2>
        </div>
    """,
        unsafe_allow_html=True,
    )

st.write("")
st.write("")
st.markdown(
    """
    <h2 style="color: #3C6E47; font-size: 25px;">Carte interactive des restaurants de Lyon</h2>
""",
    unsafe_allow_html=True,
)

# Récupérer les tags des restaurants
tags = retrieve_filter_list(restaurants["restaurants.tags"])


cols3, cols4 = st.columns([1, 1])
with cols3:
    selected_tags = st.multiselect(
        "Sélectionnez les cuisines qui vous intéressent", tags
    )

    # Filtrer les restaurants en fonction des tags sélectionnés
    if selected_tags:

        # Filtrer les restaurants qui contiennent un tag sélectionné
        filtered_restaurants = restaurants[
            restaurants["restaurants.tags"].apply(
                lambda x: selected_tags_any(x, selected_tags)
            )
        ]
    else:
        filtered_restaurants = restaurants

with cols4:
    # Récupérer les prix des restaurants
    price = retrieve_filter_list(restaurants["restaurants.price"])

    selected_price = st.multiselect("Choissisez votre fourchette de prix", price)

    # Filtrer les restaurants en fonction des tags sélectionnés
    if selected_price:

        # Filtrer les restaurants qui contiennent un tag sélectionné
        filtered_restaurants = filtered_restaurants[
            filtered_restaurants["restaurants.price"].isin(selected_price)
        ]
    else:
        filtered_restaurants = filtered_restaurants

if filtered_restaurants.shape[0] == 0:
    st.warning("Aucun restaurant ne correspond à votre recherche.")
else:
    # Initialisation de la carte
    fig = go.Figure()

    # Ajouter les restaurants sur la carte
    fig.add_trace(
        go.Scattermapbox(
            mode="markers",
            lat=filtered_restaurants["geographie.latitude"],
            lon=filtered_restaurants["geographie.longitude"],
            marker=dict(size=15, color="red"),
            text=filtered_restaurants.apply(
                lambda row: f"""
                                            🍴 Nom : {row['restaurants.nom']}<br> 
                                            📌 Adresse : {row['geographie.localisation']}<br>
                                            💶 Prix : {row['restaurants.price']}<br> 
                                            ⭐ Note globale : {row['restaurants.note_globale']}<br> 
                                            🍽️ Cuisine : {row['restaurants.tags']}""",
                axis=1,
            ),
            name="Restaurants",
        )
    )

    fig.update_layout(
        mapbox_style="open-street-map",
        mapbox_center={
            "lat": filtered_restaurants["geographie.latitude"].mean(),
            "lon": filtered_restaurants["geographie.longitude"].mean(),
        },
        mapbox_zoom=12,
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        hoverlabel=dict(align="left"),
    )
    st.plotly_chart(fig)

#  design avec des couleurs gris-vert
st.markdown(
    """
    <style>
        body {
            background-color: #F0F4F1;  /* Fond gris clair */
        }
        .stButton>button {
            background-color: #6A9A7D;  /* Boutons gris-vert */
            color: white;
        }
        h1 {
            font-family: 'Arial', sans-serif;
            font-weight: bold;
            color: #3C6E47;  /* Texte de titre gris-vert */
        }
        p {
            font-family: 'Arial', sans-serif;
            color: #333;  /* Texte descriptif gris-vert */
        }
        
    </style>
""",
    unsafe_allow_html=True,
)
