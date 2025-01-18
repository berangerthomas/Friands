import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from function_app import get_db, transform_to_df_join, retrieve_year, selected_tags_any, retrieve_filter_list
from inter_restaurants import plot_restaurant_similarities
import pandas as pd


# Chargement de la base de données
db = get_db()

# Requêtes nécessaires pour les graphiques
restaurants = transform_to_df_join(db, """SELECT * 
                                   FROM restaurants, geographie
                                   WHERE restaurants.id_restaurant = geographie.id_restaurant;""")

clients = transform_to_df_join(db, """SELECT avis.nom_utilisateur, 
                               restaurants.nom, 
                               avis.date_avis,
                               avis.note_restaurant,
                               avis.label, 
                               restaurants.tags,
                               restaurants.price
                               FROM restaurants, avis 
                               WHERE restaurants.id_restaurant = avis.id_restaurant ;""")


st.markdown("""
    <h1 style="text-align: center; font-size: 40px; font-family: 'Arial', sans-serif; color: #3C6E47; 
              font-weight: bold;"> 📊 Comparaison des restaurants sur différents aspects 📊</h1>
""", unsafe_allow_html=True)

# Afficher les aspects des restaurants
cols1, cols2, cols3, cols4, cols5 = st.columns([1, 1, 1, 1, 1])

with cols1:
    st.markdown("""
        <div style="background:linear-gradient(to right, #ffd166, #f0f9b2);; padding: 20px; border-radius: 15px; text-align: center; width: 100%; margin: auto;">
            <h3 style="color: #fff; font-family: 'Arial', sans-serif; font-weight: 500; font-size: 18px;">
                ⭐ La note du restaurant
            </h3>
        </div>
    """, unsafe_allow_html=True)

with cols2:
    st.markdown("""
        <div style="background: linear-gradient(to right, #ffd166, #ffb74d); padding: 20px; border-radius: 15px; text-align: center; width: 100%; margin: auto;">
            <h3 style="color: #fff; font-family: 'Arial', sans-serif; font-weight: 500; font-size: 18px;">
                🔢 Le nombre d'utilisateurs
            </h3>
        </div>
    """, unsafe_allow_html=True)

with cols3:
    st.markdown("""
        <div style="background: linear-gradient(to right, #b5e48c, #f0f9b2); padding: 20px; border-radius: 15px; text-align: center; width: 100%; margin: auto;">
            <h3 style="color: #fff; font-family: 'Arial', sans-serif; font-weight: 500; font-size: 18px;">
                🏆 Le classement
            </h3>
        </div>
    """, unsafe_allow_html=True)
with cols4:
    st.markdown("""
        <div style="background:linear-gradient(to right, #ffd166, #f0f9b2);; padding: 20px; border-radius: 15px; text-align: center; width: 100%; margin: auto;">
            <h3 style="color: #fff; font-family: 'Arial', sans-serif; font-weight: 500; font-size: 18px;">
                 📈 L'analyse des sentiments
            </h3>
        </div>
    """, unsafe_allow_html=True)

with cols5 :
    st.markdown("""
        <div style="background: linear-gradient(to right, #ffd166, #ffb74d); padding: 20px; border-radius: 15px; text-align: center; width: 100%; margin: auto;">
            <h3 style="color: #fff; font-family: 'Arial', sans-serif; font-weight: 500; font-size: 18px;">
                🔍 Recommendation
            </h3>
        </div>
    """, unsafe_allow_html=True)

# Petit texte introductif sous les blocs
st.markdown("""
    <div style=" padding: 20px; border-radius: 15px; text-align: center; width: 100%; margin: auto;">
        <p style="font-size: 16px; line-height: 1.6; color: #000;">
            Vous pouvez filtrer les résultats pour adapter les graphiques à vos goûts et à votre portefeuille.
        </p>
    </div>
""", unsafe_allow_html=True)

# Récupérer les tags et les prix des restaurants
resto_tags = retrieve_filter_list(restaurants['restaurants.tags'])
resto_prices=retrieve_filter_list(restaurants['restaurants.price'])

# Affichage des filtres
st.sidebar.markdown("### 🎛️ Filtres")
clients_tags = st.sidebar.multiselect("Sélectionnez les types de cuisines", resto_tags)
clients_prices = st.sidebar.multiselect("Choisissez vos fourchettes de prix", resto_prices) 

#################################### Gestion des filtres ###################################
# Filtre en fonction des sélections
if clients_tags and clients_prices:
    filtered_restaurants = restaurants[
        (restaurants["restaurants.price"].isin(clients_prices)) & 
        (restaurants["restaurants.tags"].apply(lambda x: selected_tags_any(x, clients_tags)))
    ]

    filtered_clients = clients[
        (clients["restaurants.price"].isin(clients_prices)) & 
        (clients["restaurants.tags"].apply(lambda x: selected_tags_any(x, clients_tags)))
    ]
# Si seulement des tags ont été sélectionnés
elif clients_tags:  
    filtered_restaurants = restaurants[restaurants["restaurants.tags"].apply(lambda x: selected_tags_any(x, clients_tags))]
    filtered_clients = clients[clients["restaurants.tags"].apply(lambda x: selected_tags_any(x, clients_tags))]

# Si seulement des prix ont été sélectionnés
elif clients_prices:  
    filtered_restaurants = restaurants[restaurants["restaurants.price"].isin(clients_prices)]
    filtered_clients = clients[clients["restaurants.price"].isin(clients_prices)]

# Si aucun filtre n'est sélectionné, afficher toutes les données
else:  
    filtered_restaurants = restaurants
    filtered_clients = clients

# Afficher un message si aucun résultat n'est trouvé
if filtered_restaurants.empty or filtered_clients.empty:
    st.warning("Aucun restaurant ne correspond aux filtres sélectionnés.")

#################################### Note Globale ###################################

st.subheader("⭐Note globale⭐")

# Calculer le prix moyen de la ville
note_moyenne = filtered_restaurants["restaurants.note_globale"].mean()

tab1, tab2 = st.tabs(["Note globale", "Distribution de la Note Gloable"])
with tab1:
    fig3 = px.bar(
        filtered_restaurants,
        x="restaurants.nom",
        y="restaurants.note_globale",
        title="Comparaison des notes globales",
        color="restaurants.nom",
        labels={"restaurants.note_globale": "⭐Note Globale", 
        "restaurants.nom": "Nom du restaurant"},
    )

    # Ajouter une ligne pour le prix moyen de la ville
    fig3.add_hline(y=note_moyenne, line_dash="dot", line_color="red", 
                annotation_text=f"Note globale de tous les restaurants : {round(note_moyenne,1)}", 
                annotation_position="top left")

    fig3.update_xaxes(tickangle=315)

    st.plotly_chart(fig3)

with tab2:
    fig5 = px.box(
        filtered_clients,
        y="avis.note_restaurant",
        x="restaurants.nom",
        title="Variabilité des notes",
        color="restaurants.nom",
        labels={"avis.note_restaurant": "Distribution de la note", 
                        "restaurants.nom": "Nom du restaurant"})
    fig5.update_xaxes(tickangle=315)

    st.plotly_chart(fig5)
#################################### Nombre d'utilisateurs ###################################

st.subheader("🔢 Nombre d'utilisateurs 🔢")

# Appel de la fonction retrieve pour obtenir le nombre de clients par an
col_to_group = ['année', 'restaurants.nom']
nombre_clients_an = retrieve_year(filtered_clients, "avis.date_avis", col_to_group, "avis.nom_utilisateur", 'nunique')

fig4 = px.line(nombre_clients_an, x='année',
            y='avis.nom_utilisateur',
            color='restaurants.nom',
            title=f"Nombre d'utilisateurs au fil des ans",
            markers=True,
            labels={"avis.nom_utilisateur" : "Nombre d'utilisateurs", 
                    "restaurants.nom" : "Nom du restaurant"})
st.plotly_chart(fig4)

#################################### Sentiment Analysis ###################################
st.subheader("📈 Analyse des sentiments 📉")
# Recoder les sentiments
filtered_clients.loc[: ,'avis.label_sentiment'] = filtered_clients['avis.label'].replace({5: "Positif", 4: "Positif", 3: "Neutre", 2: "Négatif", 1: "Négatif"})

# Calculer les proportions de chaque sentiment pour chaque restaurant
sentiment_counts = filtered_clients.groupby(['restaurants.nom', 'avis.label_sentiment']).size().reset_index(name='counts')
sentiment_totals = filtered_clients.groupby('restaurants.nom').size().reset_index(name='total_counts')
sentiment_counts = sentiment_counts.merge(sentiment_totals, on='restaurants.nom')
sentiment_counts['proportion'] = sentiment_counts['counts'] / sentiment_counts['total_counts'] * 100

# Assurer l'ordre des sentiments : Positif, Neutre, Négatif
sentiment_counts['avis.label_sentiment'] = pd.Categorical(
    sentiment_counts['avis.label_sentiment'], 
    categories=["Positif", "Neutre", "Négatif"], 
    ordered=True
)
sentiment_counts = sentiment_counts.sort_values(by=['restaurants.nom', 'avis.label_sentiment'])

# Créer le graphique en barres
fig_sentiments = px.bar(
    sentiment_counts,
    x='restaurants.nom',
    y='proportion',
    color='avis.label_sentiment',
    labels={
        'restaurants.nom': 'Nom du restaurant', 
        'proportion': 'Proportion', 
        'avis.label_sentiment': 'Sentiment'
    },
    title='Proportion des sentiments pour chaque restaurant',
    color_discrete_map={
        'Positif': 'rgba(0, 128, 0, 0.6)',  
        'Neutre': 'rgba(255, 165, 0, 0.6)', 
        'Négatif': 'rgba(255, 0, 0, 0.6)' 
    }
)

# Afficher le graphique
st.plotly_chart(fig_sentiments)

#################################### Classement ###################################

st.subheader("🏆Classement des restaurants🏆")

# Sélectionner les notes à afficher
selected_notes = st.multiselect("Choisissez vos notes pour classer les restaurants", sorted([int(note) for note in filtered_clients["avis.note_restaurant"].unique()], reverse=True))
if selected_notes:
    filtered_clients = filtered_clients[filtered_clients["avis.note_restaurant"].isin(selected_notes)]

# Calculer le nombre de notes par restaurant
restaurant_counts = filtered_clients.groupby("restaurants.nom")["avis.note_restaurant"].count().reset_index()
restaurant_counts.columns = ["Nom", "Nombre de notes"]
restaurant_counts["Rang"] = restaurant_counts["Nombre de notes"].rank(ascending=False)
restaurant_counts = restaurant_counts.sort_values(by="Rang").reset_index(drop=True)

# Afficher le top 3 des restaurants
col1, col2, col3 = st.columns([2, 1, 2])

with col1:
    # Sélection du Top 3
    top_3_restaurants = restaurant_counts.head(3).reindex([1, 0, 2]).reset_index(drop=True)
    colors = ['silver', 'gold', '#cd7f32']

    fig6 = go.Figure(data=[
        go.Bar(
            x=top_3_restaurants["Nom"],
            y=top_3_restaurants["Nombre de notes"],
            marker=dict(color=colors[:len(top_3_restaurants)]),
            hovertemplate='<b>Restaurant :</b> %{x}<br><b>Nombre de notes :</b> %{y}<extra></extra>'

        )
    ])

    fig6.update_xaxes(tickangle=315)

    fig6.update_layout(
        title="Top 3 des restaurants",
        xaxis_title="Nom du restaurant",
        yaxis_title="Nombre de notes", 
    )

    st.plotly_chart(fig6)
    
    with col2:
        st.write('')
        st.write('')
        st.write('') 
        st.write('') 
        st.write('') 
        st.write('') 
        st.write('') 
        st.write('') 
        st.write('') 
        st.write('') 
        st.write('') 
        st.write('') 
        st.write('') 
        st.write('') 
        st.write('')    
        if st.button("Voir le classement complet"):

            with col3:
                st.write('')
                st.write('')
                st.write('')
                st.dataframe(restaurant_counts[["Nom", "Rang", "Nombre de notes"]])

############################################## Recommendation ############################################
st.subheader("🔍 Recommandation de restaurants 🔍")
st.write("""Vous pouvez visualiser les restaurants en se basant sur leur similarité.<br>
        Plus les restaurants sont proches, plus ils sont similaires.<br>
         """, unsafe_allow_html=True)
placeholder = st.empty()

if st.button("Voir les restaurants similaires"):
    placeholder.write("Le chargement de la similiraté des restaurants peut prendre quelques instants.", unsafe_allow_html=True)
    plot_restaurant_similarities()

