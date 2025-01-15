import re
import pandas as pd
from datetime import datetime
from pathlib import Path
import requests
import time
import random
from bs4 import BeautifulSoup

from sqlutils import sqlutils
from schemaDB import schemaDB
import locale

locale.setlocale(locale.LC_TIME, 'French_France.1252')  





# Définir des headers réalistes pour éviter d'être bloqué
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    "accept-language": "en-US,en;q=0.9,fr;q=0.8",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
}

 # Suppression des espaces et ponctuations bizarres dans les champs texte
def clean_text(text):
    if isinstance(text, str):
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[\"\'”“‘’]', '', text)
        text = re.sub(r'[^\w\s,.-]', '', text)  
        text = text.strip()
    return text

def extract_address(soup):
    # Try using span
    address_div = None
    spans = soup.find_all("span", class_="biGQs _P XWJSj Wb")
    for s in spans:
        address_div = s.find("div", class_="biGQs _P pZUbB hmDzD")
        if address_div is not None:
            return address_div.get_text(strip=True)
        
    # Try using div
    address_span = None
    divs = soup.find_all('div', class_='OFtgC')
    for div in divs:
        address_span = div.find('span', class_='biGQs _P pZUbB KxBGd')  
        if address_span is not None:
            return address_span.get_text(strip=True)
        
    
    return None


def  scrape_restaurant_info(restaurant_url):

    id_restaurant = db.select("select max(id_restaurant)+1 from restaurants")
    id_restaurant = id_restaurant[1][0][0] 
    try:
    
        time.sleep(random.uniform(5, 10))
        response = requests.get(restaurant_url, headers=headers)

        # Vérification du statut de la requête
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extraire les informations principales
            nom = soup.find('h1', class_='rRtyp').text.strip() if soup.find('h1', class_='rRtyp') else "Nom non trouvé"
            localisation = extract_address(soup)
            print("localisation", localisation)
            categorie = "Restaurant"
            

            # Extraire les tags et séparer les catégories du prix
            tags_element = soup.find('span', class_=re.compile(r'(VdWAl|HUMGB cPbcf)'))
            tags_text = tags_element.text.strip() if tags_element else ""

            # Séparer les tags et le prix
            price = re.search(r'[€$£]+(?:\s*-\s*[€$£]+)?', tags_text).group(0)  # Extraire le prix
            tags = tags_text.replace(price, "").strip().strip(",")  # Supprimer le prix des tags


            # Note globale
            note_globale = soup.find('div', class_='biGQs _P fiohW hzzSG uuBRH')
            note_globale = float(note_globale.text.strip().replace(",", ".")) if note_globale else 0.0



            # Nombre total de commentaires
            total_comments_element = soup.find('span', class_='GPKsO')
            if total_comments_element:
                total_comments_text = total_comments_element.text.strip()
                # Extraire uniquement le nombre avant "avis"
                total_comments = int(re.search(r'\d+', total_comments_text).group(0))
            else:
                total_comments = 0


            # Retourner les informations
            return {
                "id_restaurant": id_restaurant,
                "nom": nom,
                "localisation": localisation,
                "categorie": categorie,
                "tags": tags,
                "price": price,
                "note_globale": note_globale,
                "total_comments": total_comments,
                "url": restaurant_url
            }
        else:
            print(f"Erreur: code de statut {response.status_code} pour {restaurant_url}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Erreur de connexion pour {restaurant_url}: {e}")
        return None

    except Exception as e:
        print(f"Erreur lors du scraping de {restaurant_url} : {e}")
        return None





def scrape_avis(restaurant_url, id_restaurant, max_pages=5):
    avis_list = [] 
    page_num = 0  # Numéro de page des avis
    avis_id = db.select("select max(id_avis)+1 from avis") 
    avis_id = avis_id[1][0][0] 

    while page_num < max_pages:  
        try:
            url = f"{restaurant_url}-or{page_num * 15}"  
            print(f"Scraping des avis pour le restaurant {id_restaurant}, page {page_num + 1}: {url}")

            # Requête HTTP
            response = requests.get(url, headers=headers) 
            if response.status_code != 200:
                print(f"Erreur lors de la récupération de la page {url}, code de statut {response.status_code}")
                break

            soup = BeautifulSoup(response.text, 'html.parser')

            # Sélectionner les conteneurs d'avis
            avis_containers = soup.find_all('div', class_='_c')  
            if not avis_containers:  
                break

            for avis in avis_containers:
                # Nom de l'utilisateur
                nom_utilisateur = avis.find('span', class_='biGQs _P fiohW fOtGX').text.strip() if avis.find('span', class_='biGQs _P fiohW fOtGX') else "Anonyme"

                # Note du restaurant
                svg_element = avis.find('svg', class_='UctUV')
                note_restaurant = None
                if svg_element:
                    title_element = svg_element.find('title')
                    if title_element:
                        note_text = title_element.text.strip()
                        note_restaurant = float(note_text.split(' ')[0].replace(',', '.'))

                 # Date de l'avis
                date_avis = avis.find('div', class_='biGQs _P pZUbB ncFvv osNWb').text.strip() if avis.find('div', class_='biGQs _P pZUbB ncFvv osNWb') else None
                # Supprimer "Rédigé le " et convertir la date
                cleaned_date = re.sub(r'^Rédigé le ', '', date_avis).strip()
                date_avis = datetime.strptime(cleaned_date, '%d %B %Y')

                # Titre avis
                titre_avis = avis.find('div', class_="biGQs _P fiohW qWPrE ncFvv fOtGX").text.strip() if avis.find('div', class_="biGQs _P fiohW qWPrE ncFvv fOtGX") else "Titre non disponible"
                titre_avis=clean_text(titre_avis)

                # Contenu de l'avis
                contenu_avis = avis.find('span', class_='JguWG').text.strip() if avis.find('span', class_='JguWG') else "Contenu non disponible"
                contenu_avis=clean_text(contenu_avis)

                # Ajouter les informations à la liste des avis
                avis_list.append({
                    "id_avis": avis_id,
                    "id_restaurant": id_restaurant,
                    "nom_utilisateur": nom_utilisateur,
                    "note_restaurant": note_restaurant,
                    "date_avis": date_avis,
                    "titre_avis": titre_avis,
                    "contenu_avis": contenu_avis,
                })
                avis_id += 1

            # Pause aléatoire pour éviter d'être bloqué par le site
            time.sleep(random.uniform(5, 15))

            # Passer à la page suivante
            page_num += 1

        except Exception as e:
            print(f"Erreur lors du scraping des avis : {e}")
            break

    return avis_list


def get_coordinates(address):
    """Utilise l'API Nominatim pour obtenir latitude et longitude à partir d'une adresse."""
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": address,
        "format": "json",
        "addressdetails": 1,
        "limit": 1,
    }
    headers = {
        "User-Agent": "YourAppName/1.0 (your@email.com)"
    }

    response = requests.get(url, params=params, headers=headers)

    if response.status_code == 200:
        data = response.json()
        if data:
            lat = data[0].get("lat")
            lon = data[0].get("lon")
            return lat, lon
        else:
            print(f"Aucune donnée trouvée pour l'adresse : {address}")
    else:
        print(f"Erreur lors de la requête : {response.status_code}")
    
    return None, None


def get_density_of_restaurants(lat, lon, radius=500):
    """Utilise l'API Overpass pour récupérer les restaurants à proximité d'une latitude/longitude."""
    overpass_url = "http://overpass-api.de/api/interpreter"
    overpass_query = f"""
    [out:json];
    (
      node["amenity"="restaurant"](around:{radius},{lat},{lon});
      way["amenity"="restaurant"](around:{radius},{lat},{lon});
      relation["amenity"="restaurant"](around:{radius},{lat},{lon});
    );
    out body;
    """
    response = requests.get(overpass_url, params={'data': overpass_query})
    
    if response.status_code == 200:
        data = response.json()
        # Le nombre total de restaurants trouvés
        return len(data["elements"])
    else:
        print(f"Erreur lors de la requête Overpass : {response.status_code}")
        return 0


def get_transport_info(lat, lon, radius=500):
    """Récupère les informations sur les transports publics à proximité d'une latitude/longitude."""
    overpass_url = "http://overpass-api.de/api/interpreter"
    overpass_query = f"""
    [out:json];
    (
      node["highway"="bus_stop"](around:{radius},{lat},{lon});
      node["railway"="station"](around:{radius},{lat},{lon});
      node["amenity"="subway"](around:{radius},{lat},{lon});
    );
    out body;
    """
    response = requests.get(overpass_url, params={'data': overpass_query})
    
    if response.status_code == 200:
        data = response.json()
        return len(data["elements"])
    else:
        print(f"Erreur lors de la requête Overpass : {response.status_code}")
        return 0


def enrich_geographic_data(localisation, id_restaurant):
    """Récupère les données géographiques pour la table `geographie`."""
    id_localisation = db.select("select max(id_localisation)+1 from geographie")
    id_localisation = id_localisation[1][0][0]
     

    # Obtenir les coordonnées géographiques
    lat, lon = get_coordinates(localisation)

    if lat is None or lon is None:
        print(f"Impossible de récupérer les coordonnées pour {localisation}")
        return None

    # Récupérer la densité des restaurants dans les environs
    restaurant_density = get_density_of_restaurants(lat, lon)

    # Récupérer les informations sur les transports à proximité
    transport_count = get_transport_info(lat, lon)

    # Enrichir les données géographiques
    return {
        "id_localisation": id_localisation, 
        "id_restaurant": id_restaurant,
        "localisation": localisation,
        "latitude": lat,
        "longitude": lon,
        "restaurant_density": restaurant_density,
        "transport_count": transport_count,
    }





def process_pipeline(url):
    """Pipeline complet pour scraper, nettoyer et insérer un restaurant dans la base de données."""


    # Étape 0 : Vérifier si l'URL existe déjà dans la table "restaurants"
    sanitized_url = url.replace("'", "''")  # Échappement des guillemets simples pour SQL
    query = f"SELECT * FROM restaurants WHERE url = '{sanitized_url}'"
    existing_record = db.select(query)
   
    if existing_record[1]:
        print("L'URL existe déjà dans la base de données. Arrêt du pipeline.")
        return

    # Étape 1 : Scraper les infos principales
    try:
        restaurant_info = scrape_restaurant_info(url)
        if not restaurant_info:
            print("Impossible de scraper les informations principales. Arrêt du pipeline.")
            return
        restaurant_info = tuple(restaurant_info.values())
        restaurant_info_without_loc = restaurant_info[:2] + restaurant_info[3:]
    except Exception as e:
        print(f"Erreur lors du scraping des informations principales : {e}")
        return
    
   # Étape 2 : Enrichir avec des données géographiques
    try:
        geo_data = enrich_geographic_data(restaurant_info[2], restaurant_info[0])
        if not geo_data:
            print("Impossible d'enrichir les données géographiques. Arrêt du pipeline.")
            return
        geo_data = tuple(geo_data.values())
    except Exception as e:
        print(f"Erreur lors de l'enrichissement des données géographiques : {e}")
        return

    # Étape 3 : Scraper les avis
    try:
        avis_data = scrape_avis(url, restaurant_info[0])
        if not avis_data:
            print("Impossible de scraper les avis. Arrêt du pipeline.")
            return
        avis_data = [tuple(avis.values()) for avis in avis_data]
    except Exception as e:
        print(f"Erreur lors du scraping des avis : {e}")
        return

    
    # Étape 4 : Enregistrement dans la base de données
    try:
        # Insérer les données dans la table "restaurants"
        success, message = db.insert("restaurants", [restaurant_info_without_loc], chk_duplicates=True)
        if not success:
            print(f"Erreur lors de l'insertion dans 'restaurants': {message}")
            return

        # Insérer les données dans la table "geographie"
        success, message = db.insert("geographie", [geo_data], chk_duplicates=True)
        if not success:
            print(f"Erreur lors de l'insertion dans 'geographie': {message}")
            return

        # Insérer les données dans la table "avis"
        success, message = db.insert("avis", avis_data, chk_duplicates=True)
        if not success:
            print(f"Erreur lors de l'insertion dans 'avis': {message}")
            return

        print("Pipeline exécuté avec succès.")
    except Exception as e:
        print(f"Erreur lors de l'enregistrement dans la base de données : {e}")



#execution du pipeline 
if __name__ == "__main__":
    db_path = Path("../../data/friands.db")
    db = sqlutils(db_path)

    # restaurant_url = "https://www.tripadvisor.fr/Restaurant_Review-g187265-d25360215-Reviews-Kopain_Cafe-Lyon_Rhone_Auvergne_Rhone_Alpes.html" 
    # process_pipeline(restaurant_url)
