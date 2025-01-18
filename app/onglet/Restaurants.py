import streamlit as st
from function_app import get_db, transform_to_df_join, generate_circle, retrieve_year
import plotly.graph_objects as go
import pandas as pd



# Chargement de la base de données
db = get_db()

# Récupérer les données des restaurants et des avis
restaurants = transform_to_df_join(db, "SELECT * FROM restaurants, geographie WHERE restaurants.id_restaurant = geographie.id_restaurant;")

avis_requete = transform_to_df_join(db, f"""SELECT avis.date_avis, avis.titre_avis, avis.contenu_avis, avis.note_restaurant, avis.label, restaurants.nom 
                                        FROM restaurants, avis 
                                        WHERE restaurants.id_restaurant = avis.id_restaurant;""")

# Ajouter un selectbox pour choisir un restaurant
# Titre principal stylisé
st.markdown("""
    <h1 style="font-size: 40px; color: #3C6E47; text-align: center;">
        🔍 <span style="font-weight: bold;">Comparaison des restaurants</span> 🔍
    </h1>
""", unsafe_allow_html=True)

# Texte d'introduction stylisé
st.markdown("""
    <p style="font-size: 18px; color: #333; text-align: center; line-height: 1.6;">
        Avec <u><strong>Friands</strong></u>, découvrez plus d'informations sur les restaurants de notre application.<br>
        Explorez les détails pour mieux choisir où savourer vos plats préférés ! 🍽️
    </p>
""", unsafe_allow_html=True)

################################################## Informations Restaurants ##################################################
st.subheader("Sélectionnez un restaurant")
selected_restaurant = st.selectbox("Choisissez un restaurant", restaurants["restaurants.nom"].unique(),label_visibility="collapsed" )

# Filtrer les données en fonction du restaurant sélectionné
selected_data = restaurants[restaurants["restaurants.nom"] == selected_restaurant]
avis = avis_requete[avis_requete["restaurants.nom"] == selected_restaurant].copy()

col1, col2 = st.columns([1, 2])

# Afficher les informations du restaurant sélectionné avec style
with col1:
    st.markdown(f"""
        <div style="background: #f9f9f9; padding: 20px; border-radius: 10px; 
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); margin-top: 20px;">
            <h2 style="color: #3C6E47; font-family: Arial, sans-serif; text-align: center; font-size: 24px;">
                {selected_restaurant}
            </h2>
            <p style="color: #333; font-size: 16px; font-family: Arial, sans-serif; line-height: 1.6;">
                <strong style="color: #f09e3f; font-size: 14px;">Adresse :</strong> {selected_data['geographie.localisation'].values[0]}<br>
                <strong style="color: #f09e3f; font-size: 14px;">Type de Cuisine :</strong> {selected_data['restaurants.tags'].values[0]}<br>
                <strong style="color: #f09e3f; font-size: 14px;">Prix :</strong> {selected_data['restaurants.price'].values[0]}<br>
                <strong style="color: #f09e3f; font-size: 14px;">Note globale :</strong> {selected_data['restaurants.note_globale'].values[0]} ⭐<br>
                <strong style="color: #f09e3f; font-size: 14px;">Nombre d'avis :</strong> {avis['avis.contenu_avis'].count()}<br>
                <strong style="color: #f09e3f; font-size: 14px;">Transports dans un rayon de 500 mètres :</strong> {selected_data['geographie.transport_count'].values[0]} 🚇<br>
                <strong style="color: #f09e3f; font-size: 14px;">Restaurants dans un rayon de 500 mètres :</strong> {selected_data['geographie.restaurant_density'].values[0]} 🍴
            </p>
            <div style="text-align: center; margin-top: 10px;">
                <a href="{selected_data['restaurants.url'].values[0]}" target="_blank" 
                   style="background: #3C6E47; color: #fff; padding: 10px 20px; 
                          text-decoration: none; border-radius: 5px; font-size: 14px;">
                    🌐 Plus d'informations
                </a>
            </div>
        </div>
    """, unsafe_allow_html=True)

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

    st.plotly_chart(fig)
################################################## Résumé et WordCloud ##################################################

# st.write("")
# st.write("")
# st.write("")
# col6, col7, col8 = st.columns([3,1,3])
# with col6:
#     st.subheader("Résumé des avis clients du restaurant")
#     st.markdown(
#         f"""
#         <div style='border: 2px solid #ccc; padding: 10px; border-radius: 10px; background-color: #fff; color: #000; font-weight: normal;'>
#             {selected_data['restaurants.summary'].values[0]}
#         </div>
#         """,
#         unsafe_allow_html=True
#     )

# with col7:
#     st.write("")
    
# with col8:
#     selected_id = selected_data['restaurants.id_restaurant'].values[0]
#     st.image(f"assets/wordcloud_{selected_id}.png", width=600, caption="Nuage de mots pour le restaurant sélectionné")
st.subheader(f"Résumé des avis clients de {selected_restaurant}")
st.markdown(
    f"""
    <div style='border: 2px solid #ccc; padding: 10px; border-radius: 10px; background-color: #fff; color: #000; font-weight: normal;'>
        {selected_data['restaurants.summary'].values[0]}
    </div>
    """,
    unsafe_allow_html=True
)

st.write("")
st.write("")
st.write("")

selected_id = selected_data['restaurants.id_restaurant'].values[0]
st.image(f"assets/wordcloud_{selected_id}.png", width=600, caption="Nuage de mots pour le restaurant sélectionné")

st.write("")
st.write("")
st.write("")

################################################## Temporalité des notes ##################################################

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
        name=f'Note moyenne par an pour {selected_restaurant}',
        line=dict(color='green'),
        hovertemplate="<b>Année : </b> %{x}<br><b>Note moyenne : </b> %{y:.2f}<extra></extra>"

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
        name=f'Note moyenne par mois pour {selected_year}',
        line=dict(color='green'),
        hovertemplate="<b>Mois : </b> %{x}<br><b>Note moyenne : </b> %{y:.2f}<extra></extra>"

    ))

    # Mettre à jour les labels et le titre
    fig_mois.update_layout(
        title=f'Note globale moyenne par mois pour {selected_year}',
        xaxis_title='Mois',
        yaxis_title=f'Note globale moyenne pour l\'année {selected_year}'
    )
    st.plotly_chart(fig_mois)

################################################## Analyse de sentiment ##################################################
st.subheader("Analyse de sentiment des avis clients")
tab1, tab2 = st.tabs(["Analyse de sentiment", "Distribution des notes de sentiment"])

with tab1:
    # Recodage variable avis.label 5 et 4 => positif, 3 => neutre, 2 et 1 => négatif
    avis['avis.label_sentiment'] = avis['avis.label'].replace({5 : "Positif", 4: "Positif", 3: "Neutre", 2: "Négatif", 1: "Négatif"})
    
    # Calcul des proportions de chaque sentiment
    total_avis = len(avis)
    positif = avis['avis.label_sentiment'].value_counts().get('Positif', 0) / total_avis * 100
    neutre = avis['avis.label_sentiment'].value_counts().get('Neutre', 0) / total_avis * 100
    negatif = avis['avis.label_sentiment'].value_counts().get('Négatif', 0) / total_avis * 100


    # Afficher les proportions de chaque sentiment
    col9, col10, col11 = st.columns(3)
    
    markdown_style = """
        <div style='
            border: 2px solid grey;
            border-radius: 10px;
            background-color: white;
            padding: 10px;
            text-align: center;
            color: {};
        '>
            <h3 style='margin: 0;'>{}</h3>
        </div>
    """
    
    with col9:
        st.markdown(markdown_style.format("green", f"Proportion de positif : {positif:.2f}%"), unsafe_allow_html=True)
    with col10:
        st.markdown(markdown_style.format("orange", f"Proportion de neutre : {neutre:.2f}%"), unsafe_allow_html=True)
    with col11:
        st.markdown(markdown_style.format("red", f"Proportion de négatif : {negatif:.2f}%"), unsafe_allow_html=True)

    # Calculer les proportions de chaque sentiment par année
    sentiment_counts = avis.groupby(['année', 'avis.label_sentiment']).size().unstack(fill_value=0)
    sentiment_proportions = sentiment_counts.div(sentiment_counts.sum(axis=1), axis=0) * 100

    # Créer le graphique en ligne
    fig_sa = go.Figure()

    fig_sa.add_trace(go.Scatter(
        x=sentiment_proportions.index, 
        y=sentiment_proportions['Positif'], 
        mode='lines+markers', 
        name='Positif', 
        line=dict(color='green'),
        hovertemplate="<b>Année : </b> %{x}<br><b>Proportion Positif : </b> %{y:.2f}%<extra></extra>"
))
    
    fig_sa.add_trace(go.Scatter(
        x=sentiment_proportions.index, 
        y=sentiment_proportions['Neutre'], 
        mode='lines+markers', 
        name='Neutre', 
        line=dict(color='orange'),    
        hovertemplate="<b>Année : </b> %{x}<br><b>Proportion Neutre : </b> %{y:.2f}%<extra></extra>"
))
    
    fig_sa.add_trace(go.Scatter(
        x=sentiment_proportions.index, 
        y=sentiment_proportions['Négatif'], 
        mode='lines+markers', 
        name='Négatif', 
        line=dict(color='red'),
        hovertemplate="<b>Année : </b> %{x}<br><b>Proportion Négatif : </b> %{y:.2f}%<extra></extra>"
))

    # Ajouter des titres et des labels
    fig_sa.update_layout(
        title='Évolution de la proportion de sentiments au fil des années',
        xaxis_title='Année',
        yaxis_title='Proportion (%)',
        legend_title='Sentiment'
    )

    st.plotly_chart(fig_sa)
    
with tab2:
    st.markdown("""La note de sentiment est une note attribuée par un modèle à chaque avis. Elle est comprise entre 1 et 5, 1 étant très négatif et 5 très positif. <br>
                Sur ce graphique, la note calculée par le modèle et la note réelle du client sont comparées
                """, unsafe_allow_html=True)
    fig_distribution = go.Figure()

    # Histogramme pour les prédictions
    fig_distribution.add_trace(go.Histogram(
        x=avis['avis.label'],
        name="Prédictions",
        marker_color='blue',
        opacity=0.7
    ))

    #Histogramme pour les notes utilisateurs
    fig_distribution.add_trace(go.Histogram(
        x=avis['avis.note_restaurant'],
        name="Notes Utilisateurs",
        marker_color='orange',
        opacity=0.7
    ))

    # Mise en forme
    fig_distribution.update_layout(
        barmode='group',
        xaxis_title="Notes (1 à 5)",
        yaxis_title="Nombre d'Avis",
        title="Distribution des Prédictions et des Notes Utilisateurs",
        legend_title="Source",
        template="plotly_white"
    )
    fig_distribution.data[1].update(
    hovertemplate="<b>Source : </b> Prédiction<br><b>Note : </b> %{x}<br><b>Nombre d'Avis:</b> %{y}<extra></extra>"
    )

    # Supposons que vous avez deux traces, une pour les utilisateurs et une pour les prédictions
    fig_distribution.data[0].update(
        hovertemplate="<b>Source : </b> Utilisateur<br><b>Note : </b> %{x}<br><b>Nombre d'Avis:</b> %{y}<extra></extra>"
    )


    st.plotly_chart(fig_distribution)

################################################## AVIS ##################################################
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
    avis.columns = ["Date de l'avis", "Titre de l'avis", "Contenu de l'avis", "Note du restaurant", "Note Label", "Sentiment"]
    st.session_state["avis"] = avis

    avis = st.session_state["avis"]
    min_date = avis["Date de l'avis"].min().date()
    max_date = avis["Date de l'avis"].max().date()
    
    col3, col4, col5, col12 = st.columns([1, 1, 1, 1])
    with col3:
        debut_date = st.date_input("Choissiez votre date de début", min_date,label_visibility="visible")
    
    with col4:
        fin_date = st.date_input("Choissiez votre date de fin", max_date,label_visibility="visible")

    with col5:
        unique_notes = avis["Note du restaurant"].unique()
        unique_notes = sorted([int(note) for note in unique_notes])
        selected_notes = st.multiselect("Sélectionnez les notes qui vous intéressent ⭐", unique_notes)
    
    with col12:
        unique_sentiments = avis["Sentiment"].unique()
        selected_sentiments = st.multiselect("Sélectionnez les sentiments qui vous intéressent", unique_sentiments)

    debut_date = pd.to_datetime(debut_date)
    fin_date = pd.to_datetime(fin_date)

    search_text = st.text_input("Recherchez un mot clé parmis tous les avis")


    # # Filtrage des avis
    # if selected_notes and selected_sentiments:
    #     # Appliquer le filtre de notes et de sentiments uniquement si des notes et des sentiments sont sélectionnés
    #     filtered_avis = avis[
    #         (avis["Date de l'avis"] >= debut_date)
    #         & (avis["Date de l'avis"] <= fin_date)
    #         & (avis["Note du restaurant"].isin(selected_notes))
    #         & (avis["Sentiment"].isin(selected_sentiments))
    #     ].copy()
    # elif selected_notes:
    #     # Appliquer le filtre de notes uniquement si des notes sont sélectionnées
    #     filtered_avis = avis[
    #         (avis["Date de l'avis"] >= debut_date)
    #         & (avis["Date de l'avis"] <= fin_date)
    #         & (avis["Note du restaurant"].isin(selected_notes))
    #     ].copy()
    # elif selected_sentiments:
    #     # Appliquer le filtre de sentiments uniquement si des sentiments sont sélectionnés
    #     filtered_avis = avis[
    #         (avis["Date de l'avis"] >= debut_date)
    #         & (avis["Date de l'avis"] <= fin_date)
    #         & (avis["Sentiment"].isin(selected_sentiments))
    #     ].copy()
    # else:
    #     # Ne pas appliquer de filtre sur les notes ou les sentiments si aucun n'est sélectionné
    #     filtered_avis = avis[
    #         (avis["Date de l'avis"] >= debut_date) & (avis["Date de l'avis"] <= fin_date)
    #     ].copy()

    # Filtrage des avis
    filtered_avis = avis[
        (avis["Date de l'avis"] >= debut_date) & 
        (avis["Date de l'avis"] <= fin_date)
    ]

    if selected_notes:
        filtered_avis = filtered_avis[filtered_avis["Note du restaurant"].isin(selected_notes)]
    
    if selected_sentiments:
        filtered_avis = filtered_avis[filtered_avis["Sentiment"].isin(selected_sentiments)]
    
    if search_text:
        filtered_avis = filtered_avis[filtered_avis["Contenu de l'avis"].str.contains(search_text, case=False, na=False)]

    # Formater les dates pour l'affichage
    filtered_avis.loc[: ,"Date de l'avis"] = pd.to_datetime(filtered_avis["Date de l'avis"]).dt.strftime('%Y/%m/%d')
    filtered_avis.reset_index(drop=True, inplace=True)

    # Sauvegarder dans la session
    st.session_state["filtered_avis"] = filtered_avis

    # Afficher les avis filtrés de manière améliorée
    for index, row in filtered_avis.iterrows():
        date_avis = row["Date de l'avis"]
        note = int(row["Note du restaurant"])
        avis = row["Contenu de l'avis"]
        sentiment = row["Sentiment"]
        titre = row["Titre de l'avis"]

        stars = '⭐' * note

        with st.expander(f"Avis du {date_avis} - Note : {stars} - Sentiment : {sentiment}", expanded=True):
            st.markdown(f"**Titre:** {titre}")
            st.markdown(f"**Avis:** {avis}")
