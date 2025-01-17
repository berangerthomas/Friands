from sqlutils import sqlutils
from schemaDB import schemaDB
from pathlib import Path


# Récupérer le chemin de ce script
script_path = Path(__file__).resolve().parent

# Définir le chemin de la base de données, relativement au chemin de ce fichier
db_path = script_path / "../../data/friands.db"


# Vérifier le chemin de la base de données
print(f"Chemin de la base de données: {db_path.resolve()}")


# Créer une instance de sqlUtils
db = sqlutils(db_path)

print(db.select("SELECT url FROM restaurants"))

# # Lister toutes les tables de la base de données
# tables = db.select("SELECT name FROM sqlite_master WHERE type='table';")
# print(f"Tables de la base de données: {tables}")


# # Créer plusieurs tables à partir de schemaDB
# for k, v in schemaDB.items():
#     success, message = db.create_table(k, v)
#     if not success:
#         print(f"Erreur lors de la création de la table '{k}': {message}")


# ### PARTIE TEST ###
# # Créer une autre table "employes"
# schema = {"id": "INTEGER PRIMARY KEY", "name": "TEXT", "age": "INTEGER"}
# success, message = db.create_table("employes", schema)
# if not success:
#     print(f"Erreur lors de la création de la table 'employes': {message}")
# else:
#     print("Table 'employes' créée avec succès")


# # Insérer des données dans employes
# data = [(1, "Alice", 12), (2, "Bob", 24), (3, "John", 34)]
# success, message = db.insert("employes", data, chk_duplicates=True)
# if not success:
#     print(f"Erreur lors de l'insertion: {message}")
# else:
#     print(message)


# # Insérer d'autres données dans employes
# data = [
#     (9, "Eloise", 29),
# ]
# success, message = db.insert("employes", data, chk_duplicates=True)
# if not success:
#     print(f"Erreur lors de l'insertion de {data}: {message}")
# else:
#     print(message)


# # Tous les select possibles
# print("\nselect de toute la table")
# print(db.select("select * from employes"))

# print("\nselect de colonnes spécifiques 'cols'")
# print(db.select("select name, age from employes"))

# print("\nselect de colonnes spécifiques avec where age > 20")
# print(db.select("select name, age from employes where age > 20"))

# print('\nselect de colonnes spécifiques avec where=["name like \'%hn%\'", "age > 2"]')
# print(db.select("select name, age from employes where name like '%hn%' and age > 2"))


# # Updater des données
# print("\nupdate avec where name = 'Eloise' : ")
# data = {"name": "Eloise", "age": 51}
# success, message = db.update("employes", data, where=["name = 'Eloise'"])
# if not success:
#     print(f"Erreur lors de la mise à jour avec {data}: {message}")
# else:
#     print(message)


# print(db.select("select * from employes where name = 'Eloise'"))


# # Supprimer des données
# success, message = db.delete("employes", where=["name = 'Eloise'"])
# if not success:
#     print(f"\nErreur lors de la suppression: {message}")
# else:
#     print(message)

# # Lancer une maintenance sur la base
# db.maintenance()
# success, message = db.maintenance()
# print(f"\n{message}")
