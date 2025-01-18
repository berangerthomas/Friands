# Utiliser Python 3.11 comme image de base
FROM python:3.11-slim

# Installation des dépendances système avec la configuration des locales
RUN apt-get update && apt-get install -y locales && \
    echo "fr_FR.UTF-8 UTF-8" >> /etc/locale.gen && \
    locale-gen fr_FR.UTF-8

# Configurer les variables d'environnement pour les locales
ENV LANG fr_FR.UTF-8
ENV LANGUAGE fr_FR:fr
ENV LC_ALL fr_FR.UTF-8

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier uniquement le fichier requirements.txt pour installer les dépendances
COPY requirements.txt .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Télécharger le modèle de langue française de spaCy
RUN python -m spacy download fr_core_news_sm

# Télécharger les données nécessaires pour NLTK
RUN python -m nltk.downloader stopwords

# Copier tout le dossier app/ dans le conteneur
COPY app/ /app

# Exposer le port par défaut de Streamlit (8501)
EXPOSE 8501

# Commande pour lancer l'application Streamlit
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=localhost"]