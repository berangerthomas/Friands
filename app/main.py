import streamlit as st

# Définition des onglets
accueil = st.Page("onglet/Accueil.py", title=" 🏠 Accueil")
comparaison = st.Page("onglet/comparaison.py", title=" 📊 Comparaison")
restaurant = st.Page("onglet/Restaurants.py", title="🔍 Zoom sur un restaurant")
ajout = st.Page("onglet/Ajout.py", title="📥Ajout")
apropos = st.Page("onglet/A_propos.py", title="📄A propos")


pg = st.navigation([accueil,comparaison, restaurant,ajout,apropos])
st.set_page_config(page_title=" Friands ",
                   page_icon="app/assets/logo.png",
                   layout="wide")
pg.run()