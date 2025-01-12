import numpy as np
from collections import Counter
from typing import List, Dict, Tuple, Optional
import spacy
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import seaborn as sns
from factor_analyzer import FactorAnalyzer
from pathlib import Path
from sqlutils import sqlutils


"""
pip install spacy nltk scikit-learn wordcloud factor_analyzer
python -m spacy download fr_core_news_md
python -m nltk.downloader vader_lexicon stopwords
"""


class ReviewAnalyzer:
    def __init__(self, lang: str = "fr"):
        """
        Initialise l'analyseur d'avis avec les modèles et ressources nécessaires.

        Args:
            lang: Code de langue ('fr' ou 'en')
        """
        # Charger les modèles et ressources
        self.lang = lang
        self.nlp = spacy.load("fr_core_news_md" if lang == "fr" else "en_core_web_md")
        self.sia = SentimentIntensityAnalyzer()
        self.stop_words = set(stopwords.words("french" if lang == "fr" else "english"))
        self.reviews = []
        self.processed_reviews = []

    def add_review(
        self,
        review: str,
        rating: Optional[float] = None,
        metadata: Optional[Dict] = None,
    ) -> None:
        """
        Ajoute un avis à analyser avec métadonnées optionnelles.

        Args:
            review: Texte de l'avis
            rating: Note numérique (optionnelle)
            metadata: Dictionnaire de métadonnées (date, utilisateur, etc.)
        """
        self.reviews.append(
            {"text": review, "rating": rating, "metadata": metadata or {}}
        )

    def preprocess_text(self, text: str) -> Tuple[str, List[str]]:
        """
        Prétraite le texte avec Spacy pour une analyse approfondie.

        Returns:
            Tuple contenant le texte nettoyé et les lemmes
        """
        doc = self.nlp(text)

        # Extraire les tokens pertinents
        tokens = [
            token.lemma_.lower()
            for token in doc
            if not token.is_stop
            and not token.is_punct
            and not token.is_space
            and len(token.text) > 2
        ]

        # Reconstruire le texte nettoyé
        clean_text = " ".join(tokens)

        return clean_text, tokens

    def analyze_sentiment(self, text: str) -> Dict[str, float]:
        """
        Analyse le sentiment avec NLTK's VADER.

        Returns:
            Dictionnaire des scores de sentiment
        """
        scores = self.sia.polarity_scores(text)
        return {
            "positif": scores["pos"],
            "negatif": scores["neg"],
            "neutre": scores["neu"],
            "compose": scores["compound"],
        }

    def extract_topics(self, texts: List[str], n_topics: int = 3) -> List[List[str]]:
        """
        Extrait les principaux thèmes avec TF-IDF et K-means.

        Returns:
            Liste des mots-clés par thème
        """
        vectorizer = TfidfVectorizer(
            max_features=1000, stop_words=list(self.stop_words)
        )
        tfidf_matrix = vectorizer.fit_transform(texts)

        # Clustering pour identifier les thèmes
        kmeans = KMeans(n_clusters=n_topics, random_state=42)
        kmeans.fit(tfidf_matrix)

        # Extraire les mots-clés par thème
        feature_names = vectorizer.get_feature_names_out()
        topics = []

        for cluster_center in kmeans.cluster_centers_:
            top_indices = cluster_center.argsort()[-10:][::-1]
            topics.append([feature_names[i] for i in top_indices])

        return topics

    def create_wordcloud(self, texts: List[str]) -> WordCloud:
        """
        Génère un nuage de mots à partir des avis.

        Returns:
            Objet WordCloud
        """
        combined_text = " ".join(texts)
        wordcloud = WordCloud(
            width=800,
            height=400,
            background_color="white",
            stopwords=self.stop_words,
            max_words=100,
        ).generate(combined_text)

        return wordcloud

    def perform_factor_analysis(self, features: np.ndarray, n_factors: int = 3) -> Dict:
        """
        Réalise une analyse factorielle des caractéristiques textuelles.

        Returns:
            Résultats de l'analyse factorielle
        """
        fa = FactorAnalyzer(rotation=None, n_factors=n_factors)
        fa.fit(features)

        # Extraire les loadings et la variance expliquée
        loadings = fa.loadings_
        variance = fa.get_factor_variance()

        return {"loadings": loadings, "variance_expliquee": variance}

    def analyze_all(self, detailed: bool = False) -> Dict:
        """
        Analyse complète des avis avec visualisations optionnelles.

        Args:
            detailed: Si True, inclut des analyses supplémentaires

        Returns:
            Dictionnaire contenant toutes les analyses
        """
        if not self.reviews:
            return {"error": "Aucun avis à analyser"}

        # Prétraitement
        processed_texts = []
        all_tokens = []
        sentiments = []
        ratings = []

        for review in self.reviews:
            clean_text, tokens = self.preprocess_text(review["text"])
            processed_texts.append(clean_text)
            all_tokens.extend(tokens)

            sentiment = self.analyze_sentiment(review["text"])
            sentiments.append(sentiment)

            if review["rating"]:
                ratings.append(review["rating"])

        # Analyses de base
        summary = {
            "nombre_avis": len(self.reviews),
            "sentiments": {
                "moyen": np.mean([s["compose"] for s in sentiments]),
                "distribution": {
                    "positif": np.mean([s["positif"] for s in sentiments]),
                    "negatif": np.mean([s["negatif"] for s in sentiments]),
                    "neutre": np.mean([s["neutre"] for s in sentiments]),
                },
            },
            "note_moyenne": np.mean(ratings) if ratings else None,
            "mots_frequents": Counter(all_tokens).most_common(10),
        }

        if detailed:
            # Analyses avancées
            topics = self.extract_topics(processed_texts)
            summary.update(
                {"themes": topics, "wordcloud": self.create_wordcloud(processed_texts)}
            )

            # Analyses temporelles si les métadonnées contiennent des dates
            dates = [
                r["metadata"].get("date")
                for r in self.reviews
                if "date" in r["metadata"]
            ]
            if dates:
                summary["evolution_temporelle"] = {
                    "dates": dates,
                    "sentiments": [s["compose"] for s in sentiments],
                }

        return summary

    def generate_report(self, summary: Dict) -> str:
        """
        Génère un rapport textuel à partir des analyses.

        Returns:
            Rapport formaté en texte
        """
        report = [
            "Rapport d'analyse des avis",
            "========================\n",
            f"Nombre total d'avis analysés : {summary['nombre_avis']}",
            (
                f"Note moyenne : {summary['note_moyenne']:.1f}/5"
                if summary["note_moyenne"]
                else "Pas de notes"
            ),
            "\nAnalyse des sentiments:",
            f"- Score moyen : {summary['sentiments']['moyen']:.2f}",
            f"- Distribution : {summary['sentiments']['distribution']}\n",
            "\nPrincipaux mots-clés:",
        ]

        for mot, freq in summary["mots_frequents"]:
            report.append(f"- {mot}: {freq} occurrences")

        if "themes" in summary:
            report.extend(
                [
                    "\nThèmes principaux identifiés:",
                    *[
                        f"Thème {i+1}: {', '.join(theme[:5])}"
                        for i, theme in enumerate(summary["themes"])
                    ],
                ]
            )

        return "\n".join(report)

    def plot_sentiment_trends(self, summary: Dict) -> None:
        """
        Génère des visualisations des tendances de sentiment.
        """
        if "evolution_temporelle" in summary:
            plt.figure(figsize=(12, 6))
            plt.plot(
                summary["evolution_temporelle"]["dates"],
                summary["evolution_temporelle"]["sentiments"],
            )
            plt.title("Évolution des sentiments dans le temps")
            plt.xlabel("Date")
            plt.ylabel("Score de sentiment")
            plt.grid(True)
            plt.show()


# Exemple d'utilisation
if __name__ == "__main__":
    # Installation des dépendances requises :
    # pip install spacy nltk scikit-learn wordcloud factor_analyzer
    # python -m spacy download fr_core_news_md
    # python -m nltk.downloader vader_lexicon stopwords

    analyzer = ReviewAnalyzer(lang="fr")

    # Récupérer le chemin de ce script
    script_path = Path(__file__).resolve().parent

    # Définir le chemin de la base de données, relativement au chemin de ce fichier
    db_path = script_path / "../../data/friands.db"

    # Vérifier le chemin de la base de données
    print(f"Chemin de la base de données: {db_path.resolve()}")

    # Créer une instance de sqlUtils
    db = sqlutils(db_path)

    # Récupérer les avis par restaurants
    success, avis = db.select("SELECT id_restaurant, contenu_avis FROM avis;")

    for idres, avis in avis:
        analyzer.add_review(avis)

    # Ajouter des avis avec métadonnées
    # analyzer.add_review(
    #     "Le produit est excellent, très satisfait de mon achat !",
    #     rating=5,
    #     metadata={"date": "2024-01-01", "user_id": "user1"},
    # )
    # analyzer.add_review(
    #     "Livraison rapide mais qualité moyenne",
    #     rating=3,
    #     metadata={"date": "2024-01-02", "user_id": "user2"},
    # )
    # analyzer.add_review(
    #     "Je ne recommande pas, trop cher pour la qualité",
    #     rating=2,
    #     metadata={"date": "2024-01-03", "user_id": "user3"},
    # )

    # Analyser et générer le rapport
    resultats = analyzer.analyze_all(detailed=True)
    rapport = analyzer.generate_report(resultats)
    print(rapport)

    # Afficher le nuage de mots
    if "wordcloud" in resultats:
        plt.figure(figsize=(10, 5))
        plt.imshow(resultats["wordcloud"])
        plt.axis("off")
        plt.title("Nuage de mots des avis")
        plt.show()
