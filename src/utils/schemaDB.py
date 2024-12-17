schemaDB = {
    "avis": {
        "id_avis": "INTEGER PRIMARY KEY",
        "id_restaurant": "INTEGER REFERENCES restaurant(id_restaurant)",
        "id_utilisateur": "INTEGER REFERENCES utilisateur(id_utilisateur)",
        "note_restaurant": "FLOAT",
        "date_avis": "DATETIME",
        "contenu_avis": "TEXT",
        "ratio_avis": "FLOAT",
    },
    "restaurant": {
        "id_restaurant": "INTEGER PRIMARY KEY",
        "nom": "TEXT",
        "localisation": "TEXT",
        "categorie": "TEXT",
        "tags": "TEXT",
        "note_globale": "FLOAT",
    },
    "utilisateur": {
        "id_utilisateur": "INTEGER PRIMARY KEY",
        "nom": "TEXT",
        "ratio_avis_global": "FLOAT",
    },
    "log": {
        "id_log": "INTEGER PRIMARY KEY",
        "timestamp": "DATETIME",
        "module": "TEXT",
        "priorite": "TEXT",
        "message": "TEXT",
    },
}
