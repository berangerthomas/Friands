import streamlit as st
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
from function_app import transform_to_df_join, retrieve_year
from sqlutils import sqlutils

# Chargement de la base de données
db_path = Path("data/friands2.db")
db = sqlutils(db_path)

# Requête nécessaires pour les graphiques
restaurants = transform_to_df_join(db, """SELECT * 
                                   FROM restaurants, geographie
                                   WHERE restaurants.id_restaurant = geographie.id_restaurant;""")

clients = transform_to_df_join(db, """SELECT avis.nom_utilisateur, 
                               restaurants.nom, 
                               avis.date_avis,
                               avis.note_restaurant, 
                               restaurants.tags,
                               restaurants.price
                               FROM restaurants, avis 
                               WHERE restaurants.id_restaurant = avis.id_restaurant ;""")

st.markdown("""
    <h1 style="text-align: center;">📊 Comparaison des restaurants 📊</h1>
""", unsafe_allow_html=True)

st.markdown("""
Bienvenue sur la page de comparaison des restaurants. 
Ici, vous pouvez confronter les différents restaurants entres eux sur différents aspects : <br>
         - ⭐La note du restaurant <br>
         - 🔢Le nombre d'utilisateurs <br>
         - 🏆 Et même un classement <br>
Vous pouvez filtrer les résultats pour adapter les graphiques à vos goûts et votre portefeuilles.
""", unsafe_allow_html=True)
st.subheader("⭐Note globale⭐")


# Calculer le prix moyen de la ville
note_moyenne = restaurants["restaurants.note_globale"].mean()

tab1, tab2 = st.tabs(["Note globale", "Distribution de la Note Gloable"])
with tab1:
    fig3 = px.bar(
        restaurants,
        x="restaurants.nom",
        y="restaurants.note_globale",
        title="Comparaison des notes globales",
        color="restaurants.nom",
        labels={"restaurants.note_globale": "⭐Note Globale", "restaurants.nom": "Nom du restaurant"},
    )

    # Ajouter une ligne pour le prix moyen de la ville
    fig3.add_hline(y=note_moyenne, line_dash="dot", line_color="red", 
                annotation_text=f"Note globale de tous les restaurants : {(note_moyenne)}", 
                annotation_position="top left")

    fig3.update_xaxes(tickangle=315)

    st.plotly_chart(fig3)
with tab2:
    # Etude de la variabilité de note_globale
    fig5 = px.box(
        clients,
        y="avis.note_restaurant",
        x = "restaurants.nom",
        title="Variabilité des notes",
        color = "restaurants.nom",
        labels={"avis.note_restaurant": "Distribution de la note", 
                        "restaurants.nom": "Nom du restaurant"})
    st.plotly_chart(fig5)


st.subheader("🔢 Nombre d'utilisateurs 🔢")

# Appel de la fonction retrieve pour obtenir le nombre de clients par an
col_to_group = ['année', 'restaurants.nom']
nb_an = retrieve_year(clients, "avis.date_avis",col_to_group,"avis.nom_utilisateur",'nunique')

# Graphique pour étudier l'évolution du nombre de clients par an
fig4 = px.line(nb_an, x='année',
            y='avis.nom_utilisateur',
            color='restaurants.nom',
            title=f"Nombre d'utilisateurs au fil des ans",
            markers=True,
            labels={"avis.nom_utilisateur": "Nombre d'utilisateurs", 
                    "restaurants.nom": "Nom du restaurant"})
st.plotly_chart(fig4)


st.subheader("🏆Classement des restaurants🏆")

# multiselect pour choisir les notes globales
selected_notes = st.multiselect("Choisissez votre classement", sorted(clients["avis.note_restaurant"].unique(), reverse=True))

# Filtrer les restaurants en fonction des notes globales sélectionnées
if selected_notes:
    filtered_clients = clients[clients["avis.note_restaurant"].isin(selected_notes)]
else:
    filtered_clients = clients

# Calculer le nombre de notes pour chaque restaurant
restaurant_counts = filtered_clients.groupby("restaurants.nom")["avis.note_restaurant"].count().reset_index()
restaurant_counts.columns = ["Nom", "Nombre de notes"]

# Ajouter une colonne de rang basée sur le nombre de notes
restaurant_counts["Rang"] = restaurant_counts["Nombre de notes"].rank(ascending=False)

# Trier le DataFrame en fonction du rang
restaurant_counts = restaurant_counts.sort_values(by="Rang").reset_index(drop=True)

col1, col2, col3 = st.columns([2, 1, 2])
with col1:
    # Afficher le top 3 des restaurants sous forme de bar chart
    top_3_restaurants = restaurant_counts.head(3)
    top_3_restaurants = top_3_restaurants.reindex([1, 0, 2]).reset_index(drop=True)  # Réorganiser pour avoir top2, top1, top3
    colors = ['silver', 'gold', '#cd7f32'] 

    fig6 = go.Figure(data=[
        go.Bar(
            x=top_3_restaurants["Nom"],
            y=top_3_restaurants["Nombre de notes"],
            marker=dict(color=colors[:len(top_3_restaurants)])
        )
    ])

    fig6.update_layout(
        title="Top 3 des restaurants",
        xaxis_title="Nom du restaurant",
        yaxis_title="Nombre de notes"
    )

    st.plotly_chart(fig6)
    if st.button("Voir le classement complet") :
        with col2:
            st.write('')
        with col3:
            st.write('')
            st.write('')
            st.write('')
            # Afficher le tableau des restaurants avec le rang
            st.dataframe(restaurant_counts[["Nom", "Rang", "Nombre de notes"]])

