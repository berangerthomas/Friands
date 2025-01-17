import streamlit as st
from function_app import get_db, transform_to_df_join, generate_circle, retrieve_year
import plotly.graph_objects as go
import pandas as pd
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..')))

from src.nlp.generate_wordcloud import *

# Chargement de la base de données
db = get_db()

# Récupérer les données des restaurants et des avis
restaurants = transform_to_df_join(db, "SELECT * FROM restaurants, geographie WHERE restaurants.id_restaurant = geographie.id_restaurant;")

avis_requete = transform_to_df_join(db, f"""SELECT avis.date_avis, avis.titre_avis, avis.contenu_avis, avis.note_restaurant, avis.label, restaurants.nom 
                                        FROM restaurants, avis 
                                        WHERE restaurants.id_restaurant = avis.id_restaurant;""")

# Ajouter un selectbox pour choisir un restaurant
st.markdown("""
    <h1 style="text-align: center;">🔍 Comparaison des restaurants 🔍</h1>
""", unsafe_allow_html=True)
st.markdown("Dans cette page, vous pouvez obtenir plus d'informations sur les restaurants disponibles dans l'application !")

st.subheader("Sélectionnez un restaurant")
selected_restaurant = st.selectbox("Choisissez un restaurant", restaurants["restaurants.nom"].unique(),label_visibility="collapsed" )

# Filtrer les données en fonction du restaurant sélectionné
selected_data = restaurants[restaurants["restaurants.nom"] == selected_restaurant]
avis = avis_requete[avis_requete["restaurants.nom"] == selected_restaurant].copy()

col1, col2 = st.columns([1, 2])

# Afficher les informations du restaurant sélectionné
with col1:
    st.write(f"### {selected_restaurant}")
    st.write(f"**Adresse** : {selected_data['geographie.localisation'].values[0]}")
    st.write(f"**Type de Cuisine** : {selected_data['restaurants.tags'].values[0]}")
    st.write(f"**Prix** : {selected_data['restaurants.price'].values[0]}")
    st.write(f"**Note globale** : {selected_data['restaurants.note_globale'].values[0]}")
    st.write(f"**Nombre d'avis** : {avis['avis.contenu_avis'].count()}")
    st.write(f"**Nombre de transports ans un rayon de 500 mètres** : {selected_data['geographie.transport_count'].values[0]}")
    st.write(f"**Nombre de restaurants dans un rayon de 500 mètres** : {selected_data['geographie.restaurant_density'].values[0]}")
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
        fill="toself",
        fillcolor="rgba(0, 0, 255, 0.2)",
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
        mapbox_style="open-street-map",  
        mapbox_center={"lat": latitude, "lon": longitude},  
        mapbox_zoom=14,  
        margin={"r":0, "t":0, "l":0, "b":0},
        legend=dict(
            x=0,  
            y=1,  
            xanchor="left",  
            yanchor="top"  
        )
    )

    # Afficher avec Streamlit
    st.plotly_chart(fig)
st.write("")
st.write("")
st.write("")
col6, col7, col8 = st.columns([3,1,3])
with col6:
    st.subheader("Résumé des avis clients du restaurant")
    st.markdown(
        f"""
        <div style='border: 2px solid #ccc; padding: 10px; border-radius: 10px; background-color: #fff; color: #000; font-weight: normal;'>
            {selected_data['restaurants.summary'].values[0]}
        </div>
        """,
        unsafe_allow_html=True
    )

with col7:
    st.write("")
    
with col8:
    selected_id = selected_data['restaurants.id_restaurant'].values[0]

    file_path = f"app/assets/wordcloud_{selected_id}.png"
    if not os.path.exists(file_path):
        generate_wordcloud(selected_id)
    st.image(file_path, width=600)



st.write("")
st.write("")
st.write("")

st.subheader("Analyse temporelle des notes globales")

# Calculer la note globale moyenne par an
tab1, tab2 = st.tabs(["Analyse par année", "Focus par mois"])

with tab1:
    
    avis.drop(columns="restaurants.nom", axis=1, inplace=True)
    # Récupérer les données par année
    moyenne_par_an = retrieve_year(avis, "avis.date_avis", "année" ,"avis.note_restaurant", "mean")

    fig = go.Figure()

    # Ajouter une trace de ligne
    fig.add_trace(go.Scatter(
        x=moyenne_par_an['année'],
        y=moyenne_par_an['avis.note_restaurant'],
        mode='lines+markers',
        name=f'Note globale moyenne par an pour {selected_restaurant}',
        line=dict(color='green')
    ))

    # Mettre à jour les labels et le titre
    fig.update_layout(
        title=f'Note globale moyenne par an pour {selected_restaurant}',
        xaxis_title='Année',
        yaxis_title='Note globale moyenne par année'
    )

    st.plotly_chart(fig)
with tab2:
    # Sélectionner une année pour visualiser les données par mois
    selected_year = st.selectbox("Sélectionnez une année pour voir les données par mois", moyenne_par_an['année'])

    # Filtrer les données pour l'année sélectionnée
    avis_par_an = avis[avis['année'] == selected_year].copy()
    avis_par_an.loc[:, 'mois_nom'] = avis_par_an['avis.date_avis'].dt.strftime('%B')
    moyenne_par_mois = avis_par_an.groupby('mois_nom')['avis.note_restaurant'].mean().reset_index()

    # Définir l'ordre des mois
    mois_ordre = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    moyenne_par_mois['mois_nom'] = pd.Categorical(moyenne_par_mois['mois_nom'], categories=mois_ordre, ordered=True)
    moyenne_par_mois = moyenne_par_mois.sort_values('mois_nom')

    # Créer un graphique en courbe pour les données par mois
    fig_mois = go.Figure()

    # Ajouter une trace de ligne
    fig_mois.add_trace(go.Scatter(
        x=moyenne_par_mois['mois_nom'],
        y=moyenne_par_mois['avis.note_restaurant'],
        mode='lines+markers',
        name=f'Note globale moyenne par mois pour {selected_year}',
        line=dict(color='green')
    ))

    # Mettre à jour les labels et le titre
    fig_mois.update_layout(
        title=f'Note globale moyenne par mois pour {selected_year}',
        xaxis_title='Mois',
        yaxis_title=f'Note globale moyenne pour l\'année {selected_year}'
    )
    st.plotly_chart(fig_mois)
tab1, tab2, tab3 = st.tabs(["Distributions", "Matrice de Confusion", "Analyse des Écarts"])
with tab1:
    fig = go.Figure()

# Histogramme pour les prédictions
fig.add_trace(go.Histogram(
    x=avis['avis.label'],
    name="Prédictions",
    xbins=dict(start=1, end=5, size=0.5),
    marker_color='blue',
    opacity=0.7
))

# Histogramme pour les notes utilisateurs
fig.add_trace(go.Histogram(
    x=avis['avis.note_restaurant'],
    name="Notes Utilisateurs",
    xbins=dict(start=1, end=5, size=0.5),
    marker_color='orange',
    opacity=0.7
))

# Mise en forme
fig.update_layout(
    barmode='group',
    xaxis_title="Notes (1 à 5)",
    yaxis_title="Nombre d'Avis",
    title="Distribution des Prédictions et des Notes Utilisateurs",
    legend_title="Source",
    template="plotly_white"
)

st.plotly_chart(fig)


with tab2:

    avis['ecart'] = avis['avis.label'] - avis['avis.note_restaurant']


    fig = go.Figure()

    # Histogramme des écarts
    fig.add_trace(go.Histogram(
        x=avis['ecart'],
        xbins=dict(start=-4, end=4, size=1),
        marker_color='purple',
        opacity=0.75
    ))

    # Mise en forme
    fig.update_layout(
        title="Distribution des Écarts (Prédictions - Notes Utilisateurs)",
        xaxis_title="Écart",
        yaxis_title="Nombre d'Avis",
        template="plotly_white"
    )

    st.plotly_chart(fig)

    grouped = avis.groupby("avis.note_restaurant")["avis.label"].mean().reset_index()

    st.write("### Moyenne des Prédictions par Note Utilisateur")

    fig = go.Figure()

    # Barres représentant les moyennes
    fig.add_trace(go.Bar(
        x=grouped['avis.note_restaurant'],
        y=grouped['avis.label'],
        marker_color='teal',
        name="Moyenne des Prédictions"
    ))

    # Mise en forme
    fig.update_layout(
        title="Prédiction Moyenne par Note Utilisateur",
        xaxis_title="Notes Utilisateurs",
        yaxis_title="Prédiction Moyenne",
        template="plotly_white"
    )

    st.plotly_chart(fig)






# Afficher les avis du restaurant
st.write("### Avis des clients")

# Cache le bouton pour faire disparaitre les avis
if "show_avis" not in st.session_state:
    st.session_state["show_avis"] = False

button_avis = st.button("Découvrir tous les avis")

if button_avis:
    st.session_state["show_avis"] = not st.session_state["show_avis"]

if st.session_state["show_avis"]:
    avis.drop(columns="année", axis=1, inplace=True)
    avis = avis.sort_values(by="avis.date_avis", ascending=False)
    avis.columns = ["Date de l'avis", "Titre de l'avis", "Contenu de l'avis", "Note du restaurant", "Note Label"]
    st.session_state["avis"] = avis

    avis = st.session_state["avis"]
    min_date = avis["Date de l'avis"].min().date()
    max_date = avis["Date de l'avis"].max().date()
    
    col3, col4, col5 = st.columns([1, 1, 1])
    with col3:
        debut_date = st.date_input("Choissiez votre date de début", min_date,label_visibility="visible")
    
    with col4:
        fin_date = st.date_input("Choissiez votre date de fin", max_date,label_visibility="visible")

    with col5:
        unique_notes = avis["Note du restaurant"].unique()
        selected_notes = st.multiselect("Sélectionnez la ou les notes qui vous intéressent", unique_notes)

    debut_date = pd.to_datetime(debut_date)
    fin_date = pd.to_datetime(fin_date)

    # Filtrage des avis
    if selected_notes:
        # Appliquer le filtre de notes uniquement si des notes sont sélectionnées
        filtered_avis = avis[
            (avis["Date de l'avis"] >= debut_date)
            & (avis["Date de l'avis"] <= fin_date)
            & (avis["Note du restaurant"].isin(selected_notes))
        ].copy()
    else:
        # Ne pas appliquer de filtre sur les notes si aucune note n'est sélectionnée
        filtered_avis = avis[
            (avis["Date de l'avis"] >= debut_date) & (avis["Date de l'avis"] <= fin_date)
        ].copy()
    # Formater les dates pour l'affichage
    filtered_avis["Date de l'avis"] = filtered_avis["Date de l'avis"].astype(str)
    filtered_avis["Date de l'avis"] = pd.to_datetime(filtered_avis["Date de l'avis"]).dt.strftime('%Y/%m/%d')
    filtered_avis.reset_index(drop=True, inplace=True)

    # Sauvegarder dans la session
    st.session_state["filtered_avis"] = filtered_avis

    # Afficher les datas filtrées
    st.dataframe(filtered_avis, use_container_width=True)
