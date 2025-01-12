import streamlit as st
import pandas as pd
import time


st.title("Ajouter un nouveau restaurant")

# Formulaire pour ajouter un nouveau restaurant
with st.form(key='add_restaurant_form'):
    url = st.text_input("Veuillez entrez le lien du restaurant TripAdvisor :")
    
    submit_button = st.form_submit_button(label='Ajouter')

# Ajouter le restaurant à la base de données
if submit_button:
    if url:
        if url.startswith("https://www.tripadvisor.fr/Restaurant_Review") and url.endswith(".html"):
            # Afficher une barre de chargement
            progress_bar = st.progress(0)
            
            # Mesurer le temps pris par l'opération d'insertion
            start_time = time.time()
            
            # Créer un DataFrame avec les nouvelles données
            new_restaurant = pd.DataFrame({
                'url': [url]
            })
            
            # Insérer les données dans la base de données
            
            # Calculer le temps écoulé
            elapsed_time = time.time() - start_time
            
            # Mettre à jour la barre de progression en fonction du temps écoulé
            for percent_complete in range(100):
                time.sleep(elapsed_time / 100)
                progress_bar.progress(percent_complete + 1)
            
            st.success(f"Le restaurant a été ajouté avec succès !")
        else:
            st.error("L'URL doit commencer par 'https://www.tripadvisor.fr/Restaurant_Review' et se terminer par '.html'.")
    else:
        st.error("Veuillez remplir tous les champs du formulaire.")
            
        
