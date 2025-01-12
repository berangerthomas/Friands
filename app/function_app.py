import pandas as pd
def transform_to_df(table_name, db) :
    success, data = db.select(f"SELECT * FROM {table_name};")
    # Vérifier si la requête a réussi
    if success:
        # Extraire uniquement les noms des colonnes
        result = (db.select(f"PRAGMA table_info({table_name});"))
        columns = [column[1] for column in result[1]]
        # Création du dataframe
        df = pd.DataFrame(data, columns = columns)
    else:
        print("Erreur lors de la récupération des données.")
    return df

