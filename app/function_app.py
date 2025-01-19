import pandas as pd
import numpy as np
import os
from pathlib import Path
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
                    columns.extend(
                        [f"{table_name}.{col[1]}" for col in pragma_result[1]]
                    )
                else:
                    print(
                        f"Erreur : Impossible de récupérer les colonnes pour {table_name}."
                    )
                    return None
        else:
            # Extraire les colonnes directement depuis la requête
            select_part = query.split("FROM")[0].strip()
            columns = [col.strip() for col in select_part[len("SELECT ") :].split(",")]

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
    # Suppression de la partie heures:min:sec pour certaines dates
    df.loc[: , date_column] = (
        df[date_column].str.split(" ", n=1).str[0]
        if df[date_column].dtype == "object"
        else df[date_column]
    )

    df[f"{date_column}"] = pd.to_datetime(df[f"{date_column}"])
    df.loc[:, "année"] = df[f"{date_column}"].dt.year

    if fun == "mean":
        grp_years = df.groupby(col_to_group)[f"{col_to_analyze}"].mean().reset_index()
    elif fun == "nunique":
        grp_years = (
            df.groupby(col_to_group)[f"{col_to_analyze}"].nunique().reset_index()
        )
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


def check_url(url, db):
    """
    Vérifie si l'URL du restaurant est déjà dans la base de données

    Args:
        url (str): URL du restaurant
        db : objet sqlutils
    Returns:
        bool: True si l'URL est déjà dans la base, False
    """
    query = transform_to_df("restaurants", db, "SELECT url FROM restaurants;")
    existing_urls = query["url"].tolist()
    return url in existing_urls


def delete_restaurant(bdd, id_restaurant):
    """
    Supprime un restaurant de la base de données.

    Args:
        bdd: Instance de la base de données.
        id_restaurant (int): ID du restaurant à supprimer.

    Returns:
        tuple: Booléen indiquant si la suppression a réussi (True) ou non (False),
        message d'erreur en cas d'échec.
    """
    try:
        success1, message1 = bdd.delete(
            table_name="geographie", where=[f"id_restaurant = {id_restaurant}"]
        )
        success2, message2 = bdd.delete(
            table_name="avis", where=[f"id_restaurant = {id_restaurant}"]
        )
        success3, message3 = bdd.delete(
            table_name="restaurants", where=[f"id_restaurant = {id_restaurant}"]
        )

        if not success1 or not success2 or not success3:
            bdd.rollback()
            raise Exception(f"{message1}\n{message2}\n{message3}")
        else:
            # Supression de l'image wordcloud dans assets
            # Obtenir le chemin absolu
            try:
                base_path = os.path.dirname(os.path.abspath(__file__))
                file_path = os.path.join(
                    base_path, "assets", f"wordcloud_{id_restaurant}.png"
                )
                Path(file_path).unlink(missing_ok=True)
            except Exception as e:
                return False, f"Erreur lors de la suppression de l'image : {file_path}"
            bdd.commit()
            return (
                True,
                f"Le restaurant {id_restaurant} a été supprimé avec succès !",
            )
    except Exception as e:
        return (
            False,
            f"Erreur lors de la suppression du restaurant {id_restaurant} : {e}",
        )
