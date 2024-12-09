# Définition des tables
tables = {
    "restaurant": {
        "id_restaurant": "INTEGER PRIMARY KEY AUTOINCREMENT",
        "nom": "TEXT NOT NULL",
        "categorie": "TEXT",
        "tags": "TEXT",
        "prix_min": "REAL",
        "prix_max": "REAL",
        "tags": "DATE",
        "localisation": "TEXT",
    },
    "utilisateur": {
        "id_utilisateur": "INTEGER PRIMARY KEY AUTOINCREMENT",
        "nom": "TEXT NOT NULL",
        "ratio_avis": "TEXT UNIQUE",
    },
    "avis": {
        "id_avis": "INTEGER PRIMARY KEY AUTOINCREMENT",
        "id_restaurant": "INTEGER",
        "id_utilisateur": "INTEGER",
        "note": "INTEGER CHECK(note BETWEEN 1 AND 5)",
        "contenu_avis": "TEXT",
        "date_avis": "DATE",
        "ratio_avis": "TEXT",
        "recommande": "BOOLEAN",
        "FOREIGN KEY (id_restaurant)": "REFERENCES restaurant(id_restaurant)",
        "FOREIGN KEY (id_utilisateur)": "REFERENCES utilisateur(id_utilisateur)",
    },
}
