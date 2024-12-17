import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime
import time
import random

# Définir les noms des colonnes pour le CSV
avis_columns = ["id_avis", "id_restaurant", "id_utilisateur", "note_restaurant", "date_avis", "contenu_avis", "ratio_avis"]
restaurant_columns = ["id_restaurant", "nom", "localisation", "categorie", "tags", "note_globale"]
utilisateur_columns = ["id_utilisateur", "nom", "ratio_avis_global"]

# Fichiers CSV
avis_csv = "avis.csv"
restaurant_csv = "restaurant.csv"
utilisateur_csv = "utilisateur.csv"

# Initialiser les fichiers CSV avec les colonnes
def init_csv_file(filename, columns):
    with open(filename, mode="w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=columns)
        writer.writeheader()

# Appeler cette fonction pour chaque fichier
init_csv_file(avis_csv, avis_columns)
init_csv_file(restaurant_csv, restaurant_columns)
init_csv_file(utilisateur_csv, utilisateur_columns)

# Fonction pour gérer les erreurs HTTP et les retries
def request_with_retry(url, headers, max_retries=3):
    retries = 0
    while retries < max_retries:
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response
        except requests.exceptions.HTTPError as e:
            print(f"Erreur HTTP: {e}")
            retries += 1
            time.sleep(random.uniform(2, 5))  # Attendre avant de réessayer
        except requests.exceptions.RequestException as e:
            print(f"Erreur de requête: {e}")
            break
    return None  # Si la requête échoue après plusieurs tentatives

# Ajouter un User-Agent pour simuler un navigateur
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.5993.89 Safari/537.36",
    "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
}

# Scraper les données pour un restaurant donné
def scrape_restaurant(url, restaurant_id):
    try:
        # Effectuer une requête avec gestion des erreurs et retries
        response = request_with_retry(url, HEADERS)
        if response is None:
            print(f"Échec de récupération de la page {url}. Passer à la suivante.")
            return

        soup = BeautifulSoup(response.content, "html.parser")

        # Extraction des informations du restaurant (assurez-vous d'utiliser les bonnes classes HTML)
        nom = soup.find("h1", class_="").text.strip() if soup.find("h1", class_="") else "Nom non trouvé"
        localisation = soup.find("span", class_="").text.strip() if soup.find("span", class_="") else "Localisation non trouvée"
        categorie = "Brasserie"  # Remplir avec des catégories fixes ou dynamiques
        tags = "Cuisine Française, Ambiance décontractée"  # Exemple de tags, à extraire dynamiquement si possible
        note_globale = float(soup.find("span", class_="").text.strip().replace(",", ".")) if soup.find("span", class_="") else 0.0

        # Enregistrer les informations dans le fichier restaurant.csv
        with open(restaurant_csv, mode="a", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=restaurant_columns)
            writer.writerow({
                "id_restaurant": restaurant_id,
                "nom": nom,
                "localisation": localisation,
                "categorie": categorie,
                "tags": tags,
                "note_globale": note_globale,
            })

        # Scraper les avis
        avis_divs = soup.find_all("div", class_="")  # Classe des avis (à ajuster)
        for avis_id, avis_div in enumerate(avis_divs, start=1):
            contenu_avis = avis_div.find("q", class_="").text.strip() if avis_div.find("q", class_="") else "Contenu non trouvé"
            note_restaurant = float(avis_div.find("span", class_="").text.strip()) if avis_div.find("span", class_="") else 0.0
            date_avis = datetime.strptime(avis_div.find("span", class_="").text.strip(), "%d %B %Y") if avis_div.find("span", class_="") else datetime.now()
            ratio_avis = note_restaurant / 5.0  # Exemple de ratio calculé

            # Enregistrer les avis dans le fichier avis.csv
            with open(avis_csv, mode="a", encoding="utf-8", newline="") as file:
                writer = csv.DictWriter(file, fieldnames=avis_columns)
                writer.writerow({
                    "id_avis": avis_id,
                    "id_restaurant": restaurant_id,
                    "id_utilisateur": avis_id,  # À remplacer par un vrai ID utilisateur si disponible
                    "note_restaurant": note_restaurant,
                    "date_avis": date_avis.strftime("%Y-%m-%d"),
                    "contenu_avis": contenu_avis,
                    "ratio_avis": ratio_avis,
                })

        # Simuler des utilisateurs
        with open(utilisateur_csv, mode="a", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=utilisateur_columns)
            writer.writerow({
                "id_utilisateur": avis_id,
                "nom": f"Utilisateur {avis_id}",
                "ratio_avis_global": ratio_avis,
            })

    except Exception as e:
        print(f"Erreur lors du scraping du restaurant {url} : {e}")

# Exemple : URL du restaurant Brasserie Georges
base_url = "https://www.tripadvisor.fr/Restaurant_Review-g187265-d13365201-Reviews-Brasserie_Georges-Lyon_Rhone_Auvergne_Rhone_Alpes.html"

# Scraper plusieurs restaurants (ajouter leurs URLs et IDs dans une liste)
restaurants_to_scrape = [
    {"url": base_url, "id": 1},
    # Ajouter d'autres restaurants ici...
]
