schemaDB = {
    "avis": {
        "id_avis": "INTEGER PRIMARY KEY",
        "id_restaurant": "INTEGER REFERENCES restaurant(id_restaurant)",
        "nom_utilisateur": "TEXT",
        "note_restaurant": "FLOAT",
        "date_avis": "DATETIME",
        "titre_avis": "TEXT",
        "contenu_avis": "TEXT",
        "nlp_note": "FLOAT",
        "nlp_score": "FLOAT",
    },
    "restaurants": {
        "id_restaurant": "INTEGER PRIMARY KEY",
        "id_localisation": "INTEGER REFERENCES geographie(id_localisation)",
        "nom": "TEXT",
        "categorie": "TEXT",
        "tags": "TEXT",
<<<<<<< Updated upstream
        "note_globale": "FLOAT",
        "total_comments": "FLOAT",
        "url": "TEXT",
        "id_localisation": "INTEGER REFERENCES geographie(id_localisation)",
=======
        "price": "TEXT",
        "note_globale": "FLOAT",
        "total_comments": "FLOAT",
        "url": "TEXT",
        "nlp_summary": "TEXT",
        "nlp_tags": "TEXT",
>>>>>>> Stashed changes
    },
    "geographie": {
        "id_localisation": "INTEGER PRIMARY KEY",
        "id_restaurant": "INTEGER REFERENCES restaurant(id_restaurant)",
        "localisation": "TEXT",
        "latitude": "FLOAT",
        "longitude": "FLOAT",
        "restaurant_density": "INTEGER",
        "transport_count": "INTEGER",
    },
}
