schema = {
    "avis": {
        "primary_key": "id_avis",
        "foreign_keys": {
            "id_restaurant": "restaurant.id_restaurant",
            "id_utilisateur": "utilisateur.id_utilisateur",
        },
        "fields": {
            "id_avis": "INTEGER",
            "id_restaurant": "INTEGER",
            "id_utilisateur": "INTEGER",
            "note_restaurant": "FLOAT",
            "date_avis": "DATETIME",
            "contenu_avis": "TEXT",
            "ratio_avis": "FLOAT",
        },
    },
    "restaurant": {
        "primary_key": "id_restaurant",
        "foreign_keys": {},
        "fields": {
            "id_restaurant": "INTEGER",
            "nom": "TEXT",
            "localisation": "TEXT",
            "categorie": "TEXT",
            "tags": "TEXT",
            "note_globale": "FLOAT",
        },
    },
    "utilisateur": {
        "primary_key": "id_utilisateur",
        "foreign_keys": {},
        "fields": {
            "id_utilisateur": "INTEGER",
            "nom": "TEXT",
            "ratio_avis_global": "FLOAT",
        },
    },
}
