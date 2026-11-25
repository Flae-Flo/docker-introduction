FROM python:3.12-slim

# Définir le répertoire de travail de l'application

WORKDIR /app

# Copier les fichiers 

COPY . /app

# Installer les dépendances, construire l'application et nettoyer 

RUN pip install --no-cache-dir -r requirements.txt

# Exposer le port

EXPOSE 5000

# Démarrer l'application 

CMD ["python", "app.py"]