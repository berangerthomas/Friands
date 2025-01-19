import streamlit as st
import base64

st.set_page_config(page_title=" Friands ", page_icon="assets/logo.png", layout="wide")


def add_logo():

    # Lecture du fichier image local
    with open("assets/logo.png", "rb") as f:
        logo_data = base64.b64encode(f.read()).decode()

    st.markdown(
        f"""
        <style>
            [data-testid="stSidebarNav"] {{
                background-image: url("data:image/png;base64,{logo_data}");
                background-repeat: no-repeat;
                padding-top: 275px;
                background-position: center 20px;
                background-size: 70%;
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )


add_logo()
# Définition des onglets
accueil = st.Page("onglet/Accueil.py", title=" 🏠 Accueil")
comparaison = st.Page("onglet/Comparaison.py", title=" 📊 Comparaison")
restaurant = st.Page("onglet/Restaurants.py", title="🔍 Zoom sur un restaurant")
ajout = st.Page("onglet/Ajout.py", title="📥Ajout")
apropos = st.Page("onglet/A_Propos.py", title="📄A propos")

pg = st.navigation([accueil, comparaison, restaurant, ajout, apropos])
pg.run()
