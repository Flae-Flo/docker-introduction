# Utiliser une image de base python

FROM python:latest


# Définir le répertoire de travail de l'application

WORKDIR /app

# Copier les fichiers 

COPY . /app

# Installer les dépendances, construire l'application et nettoyer 

RUN pip install --no-cache-dir -r requirements.txt

# Exposer le port

EXPOSE 5000

# Démarrer l'application 

CMD ["flask", "--app", "app", "run", "--host=0.0.0.0", "--port=5000"]