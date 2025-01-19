import string
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import cpu_count
from pathlib import Path
import pandas as pd
import unidecode
from sqlutils import sqlutils
from wordcloud import WordCloud


def clean_avis(avis, translation_table, mots_vides):
    """Nettoie un texte d'avis en remplaçant les ponctuations par des espaces et en supprimant les mots vides.

    Parameters
    ----------
    avis : str
        Le texte à nettoyer.
    translation_table : str.maketrans
        La table de traduction pour remplacer les ponctuations.
    mots_vides : set
        Les mots vides à supprimer.

    Returns
    -------
    str
        Le texte nettoyé.
    """
    # 3 opérations en une ici :
    # 1. On enlève les caractères diacritiques (accents, cédilles, etc.)
    # 2. On met tout en minuscules
    # 3. On remplace les ponctuations et chiffres par des espaces
    avis = unidecode.unidecode(avis).lower().translate(translation_table)

    # Puis on retourne les mots qui ne sont pas dans les mots vides, séparés par un espace
    return " ".join(mot for mot in avis.split() if mot not in mots_vides)


def makeImage(text, script_path, id_restaurant):
    """Génère une image de type wordcloud représentant le texte passé en paramètre.

    Parameters
    ----------
    text : dict
        Le dictionnaire des mots avec leur fréquence.
    script_path : Path
        Le chemin du script actuel.
    id_restaurant : int
        L'identifiant du restaurant.

    Returns
    -------
    None, mais écrit le fichier image généré dans le dossier app/assets/images.
    """
    # Définition du nuage
    nuage = WordCloud(
        background_color=None,  # transparent
        mode="RGBA",
        max_words=350,
        width=1600,  # largeur
        height=350,  # hauteur
    )
    # Générer le word cloud
    nuage.generate_from_frequencies(text)

    # Enregistrer l'image dans le dossier app/assets/images pour streamlit
    nom_image = f"wordcloud_{id_restaurant}.png"
    nuage.to_file(script_path / "assets" / nom_image)


def generate_wordcloud(id_restaurant):
    """
    Génère un wordcloud pour le restaurant d'id id_restaurant en utilisant les
    commentaires associés à ce restaurant dans la base de données.

    Parameters
    ----------
    id_restaurant : int
        L'identifiant du restaurant pour lequel générer un wordcloud.

    Returns
    -------
    None, mais enregistre le fichier image généré dans le dossier app/assets/images.
    """
    # Chemin du script
    script_path = Path(__file__).parent

    # Accès à la base de données
    db_path = Path("data/friands.db")
    bdd = sqlutils(db_path)

    # Select des avis pour le restaurant d'id 'id_restaurant'
    query = f"SELECT avis.id_restaurant, avis.contenu_avis, restaurants.nom FROM avis JOIN restaurants ON avis.id_restaurant = restaurants.id_restaurant WHERE avis.id_restaurant = {id_restaurant}"
    success, t_avis = bdd.select(query)

    if not success:
        print("Erreur lors de l'extraction des avis depuis la base de données")

    # # Insérer les champs extraits dans un dataframe pour plus de souplesse
    df = pd.DataFrame(
        t_avis,
        columns=[
            "id_restaurant",
            "contenu_avis",
            "nom",
        ],
    )

    # Mots vides
    # Chargement du fichier stopwords-fr.txt, qui contient un mot vide par ligne
    with open("stopwords-fr.txt", "r") as f:
        mots_vides = f.read().splitlines()

        # Ce fichier stopwords-fr.txt a été créer à partir de la liste de mots vides de nltk
        # puis en ajoutant des mots vides provenant de https://github.com/stopwords-iso/stopwords-fr/blob/master/stopwords-fr.txt
        # Des mots propres à l'univers de la restauration, mais trop génériques, ont aussi été enlevés (ex: restaurant, cuisine, etc.)
        # Enfin, les mots ont été nettoyés pour enlever les caractères diacritiques.
        # le fichier fourni ici est déjà propre et ne nécessite plus de traitement.

        # Définition de la table de traduction pour enlever ponctuation et chiffres
        translation_table = str.maketrans(
            {char: " " for char in string.punctuation + string.digits}
        )

    # On ajoute aux mots vides les mots composant le nom du restaurant
    noms = df["nom"].str.lower().unique()
    noms = [l for n in noms for l in n.split()]
    noms = [unidecode.unidecode(n).lower().translate(translation_table) for n in noms]
    mots_vides.extend(noms)

    # Moulinette pour nettoyer les avis en multi-threading
    n_jobs = cpu_count()
    with ThreadPoolExecutor(max_workers=n_jobs) as executor:
        results = executor.map(
            clean_avis,
            df["contenu_avis"],
            [translation_table] * len(df),
            [mots_vides] * len(df),
        )
    df["avis_clean"] = pd.DataFrame(results)

    # Compiler tous les avis par restaurant sous forme d'une liste de mots
    avis_clean = " ".join(df["avis_clean"])
    df_grouped = pd.DataFrame(
        {"id_restaurant": [id_restaurant], "avis_clean": [avis_clean]}
    )

    # Transformer en dico pour tous les restaurants
    avis = df_grouped["avis_clean"].iloc[0]
    mots = avis.split()
    serie_mots = pd.Series(mots).value_counts()
    dico_mots = {id_restaurant: serie_mots.to_dict()}

    # Générer un wordcloud
    makeImage(dico_mots[id_restaurant], script_path, id_restaurant)
