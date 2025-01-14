import streamlit as st

st.markdown("""
    <h1 style="text-align: center;">📄 A propos de l'application 📄</h1>
""", unsafe_allow_html=True)
st.write("")
st.write("")
st.write("")
st.write("")
col1, col2 = st.columns(2)
col3, col4 = st.columns(2)

with col1:
    st.markdown("""
        <h1 style="text-align: center;"> 🖥️Utilisation de l'application 🖥️</h1>
    """, unsafe_allow_html=True)
    st.markdown("""
        <div style="text-align: center;">
            <div style="text-align: left; display: inline-block;">
                <p>Cette application a pour but de comparer et d'analyser les commentaires TripAdvisor.</p>
                <p>Vous trouvez quatre onglets :</p>
                <p>🏠 <em>Accueil</em> : Pour obtenir des informations générales sur l'application</p>
                <p>📊 <em>Comparaison</em> : Pour comparer les restaurants entre eux</p>
                <p>🔍 <em>Zoom sur un restaurant</em> : Pour se faire une idée d'un restaurant en particulier</p>
                <p>📥 <em>Ajout</em> : Pour ajouter un restaurant à la base de données</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
        <h1 style="text-align: center;">🤖Technologies Utilisées🤖</h1>
    """, unsafe_allow_html=True)
    st.markdown("""
        <div style="text-align: center;">
            <div style="text-align: left; display: inline-block;">
                <p>Cette application a été développée en utilisant les technologies suivantes :</p>
                <ul>
                    <li>Python</li>
                    <li>Streamlit pour l'interface utilisateur</li>
                    <li>Pandas pour la manipulation des données</li>
                    <li>Plotly pour les visualisations graphiques</li>
                    <li>SQLite pour la base de données</li>
                    <li>Beautiful Soup pour le scrapping</li>
                </ul>
            </div>
        </div>
    """, unsafe_allow_html=True)    

with col3:
    st.markdown("""
        <h1 style="text-align: center;">⚙️Fonctionnalités⚙️</h1>
    """, unsafe_allow_html=True)
    st.markdown("""
        <div style="text-align: center;">
            <div style="text-align: left; display: inline-block;">
                <p>Notre application offre les fonctionnalités suivantes :</p>
                <ul>
                    <li>Analyse des avis des utilisateurs pour chaque restaurant</li>
                    <li>Comparaison des restaurants sur la base de plusieurs critères</li>
                    <li>Visualisation des tendances et des classements des restaurants</li>
                    <li>Ajout de nouveaux restaurants à la base de données pour une analyse future</li>
                </ul>
            </div>
        </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
        <h1 style="text-align: center;">Créateurs</h1>
    """, unsafe_allow_html=True)
    st.markdown("""
        <div style="text-align: center;">
            Cette application a été développée par Béranger THOMAS, Souraya AHMED ABDEREMANE et Lucile PERBET dans le cadre du cours de NLP du master SISE de l'Université Lumière Lyon 2.
        </div>
    """, unsafe_allow_html=True)
