import streamlit as st
from function_app import transform_to_df, transform_to_df_join, generate_circle
import sys 
import os
from pathlib import Path
import plotly.graph_objects as go
import pandas as pd
from sqlutils import sqlutils


# Ajouter le chemin du dossier utils au PATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'utils')))

# Redéfinir l'encodage de la sortie standard
sys.stdout.reconfigure(encoding='utf-8')

# Chargement de la base de données
db_path = Path("data/friands2.db")
db = sqlutils(db_path)
restaurants = transform_to_df_join(db, "SELECT * FROM restaurants, geographie WHERE restaurants.id_restaurant = geographie.id_restaurant;")

# Ajouter un selectbox pour choisir un restaurant
st.title("🔍 Zoom sur un restaurant 🔍")
st.markdown("Dans cette page, vous pouvez obtenir plus d'informations sur les restaurants disponibles dans l'application !")

st.subheader("Sélectionnez un restaurant")
selected_restaurant = st.selectbox("Choisissez un restaurant", restaurants["restaurants.nom"].unique(),label_visibility="collapsed" )

# Filtrer les données en fonction du restaurant sélectionné
selected_data = restaurants[restaurants["restaurants.nom"] == selected_restaurant]

col1, col2 = st.columns([1, 1])

# Afficher les informations du restaurant sélectionné
with col1:
    st.write(f"### {selected_restaurant}")
    st.write(f"**Adresse**: {selected_data['geographie.localisation'].values[0]}")
    st.write(f"**Type de Cuisine**: {selected_data['restaurants.tags'].values[0]}")
    st.write(f"**Prix**: {selected_data['restaurants.price'].values[0]}")
    st.write(f"**Note globale**: {selected_data['restaurants.note_globale'].values[0]}")
    st.write(f"**Nombre d'avis**: {selected_data['restaurants.total_comments'].values[0]}")
    st.write(f"**Nombre de transports à proximité**: {selected_data['geographie.transport_count'].values[0]}")
    st.write(f"**Nombre de restaurants dans un rayon de 500 mètres**: {selected_data['geographie.restaurant_density'].values[0]}")
    st.markdown(f"**Pour plus d'informations sur {selected_restaurant}** [cliquez ici]({selected_data['restaurants.url'].values[0]})")

with col2: 
    latitude = selected_data['geographie.latitude'].values[0]
    longitude = selected_data['geographie.longitude'].values[0]

    # Générer les coordonnées du cercle autour du point central
    circle_lats, circle_lons = generate_circle(latitude, longitude, 500)

    # Créer la carte avec Plotly
    fig = go.Figure(go.Scattermapbox(
        mode="lines",
        lat=circle_lats,
        lon=circle_lons,
        fill="toself",  # Remplir l'intérieur du cercle
        fillcolor="rgba(0, 0, 255, 0.2)",  # Couleur transparente du cercle
        line=dict(width=2, color="blue"),
        name="Périmètre de 500m"
    ))

    # Ajouter le restaurant sur la carte
    fig.add_trace(go.Scattermapbox(
        mode="markers",
        lat=[latitude],
        lon=[longitude],
        marker=dict(size=13, color="red"),
        text=(f"""{selected_restaurant}
            <br>Adresse: {selected_data['geographie.localisation'].values[0]}
            <br>Nombre de restaurants à proximité : {selected_data['geographie.restaurant_density'].values[0]}
            <br>Nombre de transports à proximité : {selected_data['geographie.transport_count'].values[0]}"""),
        name="Restaurant"    
    ))

    # Mettre à jour le style de la carte
    fig.update_layout(
        mapbox_style="open-street-map",  # Style de la carte
        mapbox_center={"lat": latitude, "lon": longitude},  # Centre de la carte
        mapbox_zoom=14,  # Niveau de zoom
        margin={"r":0, "t":0, "l":0, "b":0},
        legend=dict(
            x=0,  # Position horizontale de la légende
            y=1,  # Position verticale de la légende
            xanchor="left",  # Ancrage horizontal
            yanchor="top"  # Ancrage vertical
        )
    )

    # Afficher avec Streamlit
    st.plotly_chart(fig)

# fig = px.scatter_mapbox(
#     lat=[latitude],
#     lon=[longitude],
#     hover_name=[selected_restaurant],
#     zoom=15,
#     height=300
# )

# # Ajouter l'image comme marqueur personnalisé
# fig.update_layout(
#     mapbox_style="open-street-map",
#     mapbox=dict(
#         style="open-street-map",
#         layers=[
#             {
#                 "sourcetype": "image",
#                 #"source":"data:image/jpeg;base64,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",
#                 "source":"https://github.com/berangerthomas/Friands/blob/Lucile/app/assets/t%C3%A9l%C3%A9chargement_bis.png?raw=true",
#                 "coordinates": [
#                     [longitude - 0.00050, latitude + 0.00050], 
#                     [longitude + 0.00050, latitude + 0.00050],
#                     [longitude + 0.00050, latitude - 0.00050],
#                     [longitude - 0.00050, latitude - 0.00050]
#                 ]
#             }
#         ]
#     ),
#     margin={"r":0,"t":0,"l":0,"b":0}
# )

# # Afficher le graphique avec Streamlit
# st.plotly_chart(fig)


# Afficher les avis du restaurant
st.write("### Avis des clients")
avis = transform_to_df_join(db, f"SELECT avis.date_avis, avis.titre_avis, avis.contenu_avis FROM restaurants, avis WHERE restaurants.id_restaurant = avis.id_restaurant AND restaurants.nom = '{selected_restaurant}';")
# classement des avis par date de la plus récente à la plus ancienne
avis = avis.sort_values(by="avis.date_avis", ascending=False)
avis.columns = ["Date de l'avis", "Titre de l'avis", "Contenu de l'avis"]

# Convertir les dates en objets datetime
avis["Date de l'avis"] = pd.to_datetime(avis["Date de l'avis"])

# Ajout d'un filtre pour sélectionner les dates que l'on veut afficher
min_date = avis["Date de l'avis"].min().date()
max_date = avis["Date de l'avis"].max().date()
start_date, end_date = st.date_input("Sélectionnez la plage de dates", [min_date, max_date], label_visibility="visible")

# Convertir les dates sélectionnées par l'utilisateur en datetime
start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)

# Filtrer les avis en fonction de la plage de dates sélectionnée
filtered_avis = avis[(avis["Date de l'avis"] >= start_date) & (avis["Date de l'avis"] <= end_date)]

filtered_avis["Date de l'avis"] = filtered_avis["Date de l'avis"].dt.strftime('%Y/%m/%d')
filtered_avis.reset_index(drop=True, inplace=True)

st.write(filtered_avis)

