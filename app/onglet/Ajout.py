import streamlit as st
import time
from function_app import get_db, transform_to_df
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.utils.scraping import *

# Chargement de la base de données
db = get_db()

# Récupérer les URLs des restaurants existants
query=transform_to_df("restaurants",db,"SELECT url FROM restaurants;")
existing_urls = query['url'].tolist()

st.title("📥 Ajouter un nouveau restaurant 📥")
st.write("""Vous pouvez ajouter un nouveau restaurant à la base de données en remplissant en entrant le lien de votre restaurant préféré TripAdvisor. <br>
            Pour cela, rendez-vous sur la page du restaurant [TripAdvisor](https://www.tripadvisor.fr/), copiez l'URL et collez-la dans le champ ci-dessous. <br>
         """, unsafe_allow_html=True)
# Formulaire pour ajouter un nouveau restaurant
with st.form(key='add_restaurant_form'):
    url = st.text_input("Veuillez entrez le lien du restaurant TripAdvisor :")
    
    submit_button = st.form_submit_button(label='Ajouter')

# Ajouter le restaurant à la base de données
if submit_button:
    if url:
        if url.startswith("https://www.tripadvisor.fr/Restaurant_Review") and url.endswith(".html"):
            
            if url in existing_urls:
                st.error("Le restaurant existe déjà dans la base de données.")
            else:
            
                # Afficher une barre de chargement
                progress_bar = st.progress(0)
                
                # Mesurer le temps pris par l'opération d'insertion
                start_time = time.time()

                # Calculer le temps écoulé
                elapsed_time = time.time() - start_time
            
                # Mettre à jour la barre de progression en fonction du temps écoulé
                for percent_complete in range(100):
                    time.sleep(elapsed_time / 100)
                    progress_bar.progress(percent_complete + 1)
                process_pipeline(url)
                st.success(f"Le restaurant a été ajouté avec succès !")
        else:
            st.error("L'URL doit commencer par 'https://www.tripadvisor.fr/Restaurant_Review' et se terminer par '.html'.")
    else:
        st.error("Veuillez remplir tous les champs du formulaire.")
            
        
