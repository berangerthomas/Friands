import streamlit as st
from function_app import get_db, transform_to_df, check_url
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from src.utils.scraping import *
from src.nlp.summary_generator import *
from src.nlp.sentiment_analysis import *

# Chargement de la base de données
db = get_db()

# Récupérer les URLs des restaurants existants
query = transform_to_df("restaurants",db,"SELECT url FROM restaurants;")
existing_urls = query['url'].tolist()

st.markdown("""
    <h1 style="font-size: 36px; color: #3C6E47; text-align: center; font-family: 'Arial', sans-serif;">
        📥 <span style="font-weight: bold;">Ajouter un nouveau restaurant</span> 📥
    </h1>
  
""", unsafe_allow_html=True)

st.write("""Vous pouvez ajouter un nouveau restaurant à la base de données en remplissant en entrant le lien de votre restaurant préféré TripAdvisor. <br>
            Pour cela, rendez-vous sur la page du restaurant [TripAdvisor](https://www.tripadvisor.fr/), copiez l'URL et collez-la dans le champ ci-dessous. <br>
            L'opération prends plusieurs minutes. <br>
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
                
                # Préparation des messages de chargement
                placeholder_success = st.empty()
                placeholder_info = st.empty()
                placeholder_info.write("Récupération des informations du restaurant en cours...")
                
                # Exécuter le pipeline de scraping
                process_pipeline(url, db)
                
                # Vérifer si le restaurant est bien été ajouté dans la base
                if check_url(url, db) :
                    placeholder_success.success("Restaurant ajouté avec succès !")
                    placeholder_info.write("Génération du résumé en cours...")

                    # Itérer sur les id_restaurant et appeler generate_summary pour chacun
                    cle_api_mistral = "wOB1K35GugrbguMCVZxQvs6imjLn99Gr"
                    
                    # Récupérer l'identifiant du restaurant
                    success, id_resto = db.select("SELECT id_restaurant FROM restaurants")

                    # Fermuture de la base pour éviter d'être bloqué par une autre requête
                    db.__del__()
                    try : 
                        for row in id_resto :

                            id_restaurant = row[0]
                            success, message = generate_summary(id_restaurant, cle_api_mistral, nb_mois=18)
                            
                            if success:
                                print(f"Résumé généré pour le restaurant {id_restaurant} : {message}")
                            else:
                                print(f"Erreur pour le restaurant {id_restaurant} : {message}")
                    except Exception as e:
                        placeholder_success.write(f"Erreur lors de la génération des résumés : {e}")
                        placeholder_info.empty()  

                    try :
                        placeholder_success.success("Génération des résumés effectué avec succès !")
                        placeholder_info.write("Calcul de la note de sentiment en cours...")

                        for ligne in id_resto :

                            id_restaurant = ligne[0]
                            success, message = generate_label(id_restaurant)
                            
                            if success:
                                print(f"Label pour {id_restaurant} : {message}")
                            else:
                                print(f"Erreur pour le restaurant {id_restaurant} : {message}")
                        placeholder_info.empty()
                        placeholder_success.success("""Calcul de note de sentiment effectué avec succès !
                                                            Retournez sur la page de votre choix pour en apprendre plus sur ce nouveau restaurant.""")
                    
                    except Exception as e:
                            placeholder_success.write(f"Erreur lors de la génération des labels : {e}")
                            placeholder_info.empty()
                                
                else : 
                    placeholder_success.error("Erreur lors de l'ajout du restaurant. \n Rappuyez sur le bouton pour recommencer")
                    placeholder_info.empty()    
                    
        else:
            st.error("L'URL doit commencer par 'https://www.tripadvisor.fr/Restaurant_Review' et se terminer par '.html'.")
    else:
        st.error("Veuillez remplir tous les champs du formulaire.")
            
        
