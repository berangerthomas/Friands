import streamlit as st
import pandas as pd
import plotly.express as px
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

# Titre de l'application
st.title("Comparaison des Restaurants")
st.markdown("Sous-titre")

# Exemple de data 
data = {
    "Restaurant": ["Brasserie Georges", "Les terrasses de Lyon", "Frazarin Bistrot Franco Italien", "Agastache Restaurant", "Burger & Wine"],
    "Cuisine": ["Française", "Italienne", "Japonaise", "Américaine", "Indienne"],
    "adresse": ["30 Cours de Verdun Perrache, 69002 Lyon France", 
                "25 Montee Saint Barthelemy, 69005 Lyon France", 
                "23 Rue De Condé, 69002 Lyon France",
                "134 Rue Duguesclin, 69006 Lyon France", 
                "14 quai Antoine Riboud, 69002 Lyon France"],
    "Note": [4.5, 4.2, 4.8, 4.0, 4.3],
    "Prix moyen": [40, 20, 35, 15, 25],
    "Nombre d'avis": [120, 200, 150, 80, 100]
}

# Charger les données dans un DataFrame
restaurants = pd.DataFrame(data)

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

# Calculer le prix moyen de la ville
prix_moyen_ville = restaurants["Prix moyen"].mean()

# filtrer par type de cuisine
cuisine_filter = st.sidebar.multiselect(
    "Sélectionnez le ou les types de cuisine : ",
    options=restaurants["Cuisine"].unique(),
    default=restaurants["Cuisine"].unique(),
    key="cuisine_filter"
)

# Filtrer les données
filtered_data = restaurants[restaurants["Cuisine"].isin(cuisine_filter)]

# Calculer la note moyenne par arrondissement
arrondissement_avg_note = filtered_data.groupby("Arrondissement", as_index=False).agg({"Note": "mean", "latitude": "first", "longitude": "first"})

# Ajouter un graphique interactif pour la note des restaurants
st.subheader("Notes des Restaurants")
fig1 = px.bar(
    filtered_data, 
    x="Restaurant", 
    y="Note", 
    #color="Cuisine", 
    title="Notes moyennes des restaurants",
    labels={"Note": "Note moyenne"}
)
st.plotly_chart(fig1, key="plotly_chart_1")

# Ajouter un graphique interactif pour comparer les prix moyens
st.subheader("Prix moyens par restaurant -- Pas de prix moyen dans tripadvisor")
fig2 = px.scatter(
    filtered_data, 
    x="Restaurant", 
    y="Prix moyen", 
    size="Nombre d'avis", 
    color="Cuisine", 
    title="Prix moyen des restaurants",
    labels={"Prix moyen": "Prix moyen (€)"},
    hover_data=["Note"]
)

# Ajouter une ligne pour le prix moyen de la ville
fig2.add_hline(y=prix_moyen_ville, line_dash="dot", line_color="red", 
               annotation_text=f"Prix moyen de la ville: {prix_moyen_ville:.2f} €", 
               annotation_position="top left")

st.plotly_chart(fig2, key="plotly_chart_2")

# Ajouter une carte interactive des notes moyennes par arrondissement
# st.subheader("Carte interactive des arrondissements")
# fig3 = px.scatter_mapbox(
#     arrondissement_avg_note,
#     lat="latitude",
#     lon="longitude",
#     color="Note",
#     size="Note",
#     hover_name="Arrondissement",
#     title="Notes moyennes par arrondissement",
#     mapbox_style="open-street-map",
#     zoom=12
# )
# fig3.update_traces(marker=dict(sizemin=8))  # Ajuster la taille minimale des marqueurs
# st.plotly_chart(fig3, key="plotly_chart_3")

# Ajouter une table des données filtrées
st.subheader("Données filtrées")
st.dataframe(filtered_data)

# # Ajouter une possibilité de télécharger les données filtrées
# st.download_button(
#     label="Télécharger les données filtrées",
#     data=filtered_data.to_csv(index=False).encode("utf-8"),
#     file_name="restaurants_filtrés.csv",
#     mime="text/csv"
# )
