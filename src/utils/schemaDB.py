schemaDB = {
    "avis": {
        "id_avis": "INTEGER PRIMARY KEY",
        "id_restaurant": "INTEGER REFERENCES restaurant(id_restaurant)",
        "nom_utilisateur": "TEXT",
        "note_restaurant": "FLOAT",
        "date_avis": "DATETIME",
        "titre_avis": "TEXT",
        "contenu_avis": "TEXT",
    },
    "restaurants": {
        "id_restaurant": "INTEGER PRIMARY KEY",
        "nom": "TEXT",
        "categorie": "TEXT",
        "tags": "TEXT",
        "price":"TEXT",
        "note_globale": "FLOAT",
        "total_comments": "FLOAT",
        "url": "TEXT",
        
    },
    "geographie": {
        "id_localisation": "INTEGER",
        "localisation": "TEXT",
        "latitude": "FLOAT",
        "longitude": "FLOAT",
        "restaurant_density": "INTEGER",
        "transport_count": "INTEGER",
        "id_restaurant": "INTEGER REFERENCES restaurant(id_restaurant)",
    },
}
