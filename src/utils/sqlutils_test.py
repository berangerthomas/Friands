from sqlutils import sqlutils
from schemaDB import schemaDB
from pathlib import Path

# Définir le chemin de la base de données
db_path = Path("data/friands.db")

# Créer une instance de sqlUtils
db = sqlutils(db_path)

# Créer plusieurs tables à partir de schemaDB
for k, v in schemaDB.items():
    success, message = db.create_table(k, v)
    if not success:
        print(f"Erreur lors de la création de la table '{k}': {message}")


### PARTIE TEST ###
# Créer une autre table "users"
#schema = {"id": "INTEGER PRIMARY KEY", "name": "TEXT", "age": "INTEGER"}
schema = {
    "id": "INTEGER PRIMARY KEY", 
    "restaurant": "TEXT", 
    "cuisine": "TEXT", 
    "adresse": "TEXT", 
    "note": "REAL", 
    "nombre_avis": "INTEGER", 
    "prix_moyen": "INTEGER", 
    "avis": "TEXT"
}

success, message = db.create_table("users", schema)
if not success:
    print(f"Erreur lors de la création de la table 'users': {message}")

# Insérer des données dans users
# data = [("Alice", 12), ("Bob", 24), ("John", 34)]
data = [
    ("Brasserie Georges", "Française", "30 Cours de Verdun Perrache, 69002 Lyon France", 4.5, 120, 40, "blabla1"),
    ("Les terrasses de Lyon", "Italienne", "25 Montee Saint Barthelemy, 69005 Lyon France", 4.2, 200, 20, "blabla2"),
    ("Frazarin Bistrot Franco Italien", "Japonaise", "23 Rue De Condé, 69002 Lyon France", 4.8, 150, 35, "blabla3"),
    ("Agastache Restaurant", "Américaine", "134 Rue Duguesclin, 69006 Lyon France", 4.0, 80, 15, "blabla4"),
    ("Burger & Wine", "Indienne", "14 quai Antoine Riboud, 69002 Lyon France", 4.3, 100, 25, "blabla5")
]

success, message = db.insert("users", data, chk_duplicates=True)
if not success:
    print(f"Erreur lors de l'insertion: {message}")

# # Insérer d'autres données dans users
# data = [
#     ("Eloise", 29),
# ]
# success, message = db.insert("users", data, chk_duplicates=True)
# if not success:
#     print(f"Erreur lors de l'insertion: {message}")

# Tous les select possibles
# print("\nselect de toute la table")
# print(db.select("users"))

# print("\nselect de colonnes spécifiques 'cols'")
# cols = ["name", "age"]
# print(db.select("users", columns=cols))

# print("\nselect de colonnes spécifiques avec where age > 20")
# print(db.select("users", columns=cols, where=["age > 20"]))

# print('\nselect de colonnes spécifiques avec where=["name like \'%hn%\'", "age > 2"]')
# print(db.select("users", columns=cols, where=["name like '%hn%'", "age > 2"]))


# # Updater des données
# data = {"name": "Eloise", "age": 51}
# success, message = db.update("users", data, where=["name = 'Eloise'"])

# if not success:
#     print(f"Erreur lors de la mise à jour: {message}")

# print("\nupdate avec where name = 'Eloise'")
# print(db.select("users", where=["name = 'Eloise'"]))


# # Supprimer des données
# success, message = db.delete("users", where=["name = 'Eloise'"])
# if not success:
#     print(f"\nErreur lors de la suppression: {message}")

# # Lancer une maintenance sur la base
# db.maintenance()
# success, message = db.maintenance()
# print(f"\n{message}")
