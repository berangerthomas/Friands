# Utiliser Python 3.11 comme image de base
FROM python:3.11-slim

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier uniquement le fichier requirements.txt pour installer les dépendances
COPY requirements.txt .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copier tout le dossier app/ dans le conteneur
COPY app/ /app

# Exposer le port par défaut de Streamlit (8501)
EXPOSE 8501

# Commande pour lancer l'application Streamlit
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]
