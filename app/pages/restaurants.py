import streamlit as st
from function_app import transform_to_df
import sys 
import os
from pathlib import Path
from sqlutils import sqlutils


# Ajouter le chemin du dossier utils au PATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'utils')))

# Redéfinir l'encodage de la sortie standard
sys.stdout.reconfigure(encoding='utf-8')

# Chargement de la base de données
db_path = Path("data/friands.db")
db = sqlutils(db_path)
restaurants = transform_to_df("restaurants", db)

# Ajouter un selectbox pour choisir un restaurant
st.subheader("Sélectionnez un restaurant")
selected_restaurant = st.selectbox("Choisissez un restaurant", restaurants["nom"].unique())

# Filtrer les données en fonction du restaurant sélectionné
selected_data = restaurants[restaurants["nom"] == selected_restaurant]

query = (f"""
    SELECT distinct(localisation) 
    FROM restaurants, avis, geographie
    WHERE restaurants.id_localisation = geographie.id_localisation 
    AND restaurants.id_restaurant = avis.id_restaurant 
    AND restaurants.nom = '{selected_restaurant}';
""")

# Afficher les informations du restaurant sélectionné
st.write(f"### {selected_restaurant}")
st.write(f"**Type de Cuisine**: {selected_data['tags'].values[0]}")
st.write(f"**Note Global**: {selected_data['note_globale'].values[0]}")
st.write(f"**Nombre d'avis**: {selected_data['total_comments'].values[0]}")
st.write(f"**Pour plus d'informations suivez le lien**: {selected_data['url'].values[0]}")
st.write(f"**Adresse**:{db.select(query)[1]}")


# Afficher les avis du restaurant
st.write("### Avis des clients")
st.write(selected_data["avis"])

st.write("### Affichez résumé des commentaires")
