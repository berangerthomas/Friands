import pandas as pd
import numpy as np
import re
from pathlib import Path
import sys
import os
#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','src', 'utils')))

from sqlutils import sqlutils


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
            tables_part = from_part.split("WHERE")[0].strip()
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

def get_db():
    """
    Récupère la base de données SQLite

    Returns :
        db : bdd sqlutils
    """
    db_path = Path("data/friands.db")
    db = sqlutils(db_path)
    return db

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
    
    # Convertir le rayon en degrés
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

def retrieve_year(df, date_column, col_to_group, col_to_analyze, fun):
    """
    Récupère les données d'une colonne en fonction de l'année.

    Args:  
        df : DataFrame
        date_column : nom de la colonne contenant les dates
        col_to_group : nom de ou des colonnes à grouper
        col_to_analyze : nom de la colonne à analyser
        fun : fonction à appliquer (mean ou sum)
    Returns:
        grp_years : Df contenant les données agrégées par année
    """
    # suppression de la partie heures:min:sec pour certaines dates
    df[date_column] = df[date_column].str.split(' ', n=1).str[0] if df[date_column].dtype == 'object' else df[date_column]

    df[f"{date_column}"] = pd.to_datetime(df[f"{date_column}"])
    df.loc[:, "année"] = df[f"{date_column}"].dt.year
    
    if fun == 'mean':
        grp_years = df.groupby(col_to_group)[f'{col_to_analyze}'].mean().reset_index()
    elif fun == 'nunique':
        grp_years = df.groupby(col_to_group)[f'{col_to_analyze}'].nunique().reset_index()
    else:
        raise ValueError("L'argument fun doit être soit 'mean' ou 'nunique'.")
    return grp_years

def selected_tags_any(row_tags, selected_tags):
    """
    Vérifie si au moins un tag correspond à un tag sélectionné.

    Args:
        row_tags (str): Tags de la ligne
        selected_tags (list): Tags sélectionnés
    Returns:
        bool: True si au moins un tag correspond, False sinon
    """
    row_tags_set = set(map(str.strip, row_tags.split(","))) 
    return any(tag in row_tags_set for tag in selected_tags) 

def retrieve_filter_list(df_col): 
    """
    Preprocesse une colonne pour obtenir une liste unique d'éléments

    Args:
        df_col (pd.Series): Colonne du DataFrame
    Returns:
        np.array: Liste unique des éléments
    """
    tags_list = df_col.str.split(",").explode().str.strip()
    return tags_list.unique()

def tags_cleans(tags):
    """
    Nettoie les tags en supprimant les caractères spéciaux

    Args:       
        tags (list): Liste des tags
    Returns:
        tags_clean (list): Liste des tags nettoyés
    """
    if any('€' in tag for tag in tags):
        # Filtrage des caractères non alphanumériques sauf espaces, accents et "/"
        tags_clean = [re.sub(r'[^a-zA-Z0-9À-ÿ/ ]', '', tag) for tag in tags]
        
        # Suppression des éléments vides
        tags_clean = [tag for tag in tags_clean if tag]
    else:
        # Si aucun signe € n'est trouvé, ne pas modifier les tags
        tags_clean = tags
    return tags_clean




def check_url (url, db):
    """
    Vérifie si l'URL du restaurant est déjà dans la base de données

    Args:
        url (str): URL du restaurant
        db : objet sqlutils
    Returns:
        bool: True si l'URL est déjà dans la base, False
    """
    query = transform_to_df("restaurants",db,"SELECT url FROM restaurants;")
    existing_urls = query['url'].tolist()
    return url in existing_urls

def check_no_null (db, column_name, table_name):
    """
    Vérifie qu'une colonne ne possède plus de valeurs nulles.

    Args:
        db: Instance de la base de données.
        column_name (str): Nom de la colonne à vérifier.
        table_name (str): Nom de la table contenant la colonne.

    Returns:
        bool: True si la colonne ne contient plus de valeurs nulles, False sinon.
    """
    query = f"SELECT COUNT(*) FROM {table_name} WHERE {column_name} IS NULL"
    success, result = db.select(query)
    
    if not success:
        raise Exception(f"""Erreur lors de l'exécution de la requête la colonne {column_name} de {table_name} contient des valeurs nulls :
                        \n {result}""")
    
    return result[0][0] == 0




