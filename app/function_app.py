import pandas as pd
import numpy as np

def transform_to_df_join(db, query):
    """
    Transforme les données d'une requête SQL avec jointure en DataFrame.
    Args : 
        db : objet sqlutils
        query : requête SQL
    Returns :   
        df : DataFrame
    """
    success, data = db.select(query)
    if success:
        # Si SELECT * est utilisé, récupérer les colonnes des tables concernées
        if "SELECT *" in query.upper():
            from_part = query.split("FROM")[1].strip()
            tables_part = from_part.split("WHERE")[0].strip()  # Extrait les tables avant WHERE
            table_names = [t.strip() for t in tables_part.split(",")]
            
            columns = []
            for table_name in table_names:
                # Récupérer les colonnes pour chaque table avec PRAGMA
                pragma_result = db.select(f"PRAGMA table_info({table_name});")
                if pragma_result[0]:
                    columns.extend([f"{table_name}.{col[1]}" for col in pragma_result[1]])
                else:
                    print(f"Erreur : Impossible de récupérer les colonnes pour {table_name}.")
                    return None
        else:
            # Extraire les colonnes directement depuis la requête
            select_part = query.split("FROM")[0].strip()
            columns = [col.strip() for col in select_part[len("SELECT "):].split(",")]

        # Vérifier que le nombre de colonnes correspond aux données
        if len(data[0]) != len(columns):
            print("Erreur : Le nombre de colonnes ne correspond pas aux données.")
            return None

        # Création du DataFrame
        df = pd.DataFrame(data, columns=columns)
        return df
    else:
        print("Erreur lors de la récupération des données.")
        return None

# Exemple d'utilisation
query = """SELECT price, transport_count FROM restaurants, geographie
           WHERE restaurants.id_restaurant = geographie.id_restaurant
           AND restaurants.nom = 'KUMA cantine';"""

query = """SELECT * FROM restaurants, geographie
           WHERE restaurants.id_restaurant = geographie.id_restaurant
           AND restaurants.nom = 'KUMA cantine';"""

# print(transform_to_df(db, query))

def transform_to_df(table_name, db, query):
    """
    Transforme les données d'une requête SQL sans jointure en DataFrame.

    Args: 
        table_name : nom de la table
        db : objet sqlutils
        query : requête SQL
    Returns:
        df : DataFrame
    """
    success, data = db.select(query)
    
    # Vérifier si la requête a réussi
    if success:
        # Si la requête contient '*', récupérer les colonnes de la table
        if "*" in query:
            result = db.select(f"PRAGMA table_info({table_name});")
            columns = [column[1] for column in result[1]]
        else:
            # Sinon, extraire les noms des colonnes directement de la requête
            select_part = query.lower().split("from")[0].replace("select", "").strip()
            columns = [col.strip() for col in select_part.split(",")]

        # Création du dataframe
        df = pd.DataFrame(data, columns=columns)
    else:
        print("Erreur lors de la récupération des données.")
        return None
    
    return df

# Exemple d'utilisation
query = """SELECT price, nom FROM restaurants;"""
# print(transform_to_df("restaurants", db, query))


# Fonction pour générer les coordonnées du cercle
def generate_circle(lat, lon, rayon, num_points=100):
    """
    Génère les coordonnées d'un cercle autour d'un point donné.
    
    Args:
        lat (float): Latitude du centre du cercle
        lon (float): Longitude du centre du cercle
        rayon (float): Rayon du cercle en mètres
        num_points (int): Nombre de points à générer sur le cercle

    Returns:
        circle_lats (list): Liste des latitudes des points du cercle
        circle_lons (list): Liste des longitudes des points du cercle
    """
    circle_lats = []
    circle_lons = []
    
    # Convertir le rayon en degrés (approximativement)
    radius_deg = rayon / 111320  # 1 degré de latitude ~ 111.32 km
    
    # Générer les points autour du centre du cercle
    for i in range(num_points):
        angle = 2 * np.pi * i / num_points  # Calcul de l'angle pour chaque point
        delta_lat = radius_deg * np.sin(angle)
        delta_lon = radius_deg * np.cos(angle) / np.cos(np.radians(lat))
        
        new_lat = lat + delta_lat
        new_lon = lon + delta_lon
        
        circle_lats.append(new_lat)
        circle_lons.append(new_lon)
    
    return circle_lats, circle_lons
