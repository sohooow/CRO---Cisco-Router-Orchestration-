# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.12.6
FROM python:${PYTHON_VERSION}-slim as base

# Prévenir la création de fichiers pyc et désactiver le buffering
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Définir le répertoire de travail
WORKDIR /app

# Ajouter un utilisateur non privilégié
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

# Installer les dépendances système nécessaires pour mysqlclient et autres bibliothèques
RUN apt-get update && apt-get install -y --no-install-recommends \
    libmariadb-dev gcc build-essential libffi-dev libssl-dev nginx\
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copier le fichier requirements.txt dans le conteneur
COPY requirements.txt /app/

# Installer les dépendances Python
RUN python3 -m pip install --no-cache-dir -r requirements.txt

# Copier le reste du code source dans le conteneur
COPY . .

# Assurez-vous que les fichiers statiques sont collectés (si nécessaire)
RUN python3 manage.py collectstatic --noinput || true

# Copier la configuration Nginx dans le conteneur
#COPY nginx.conf /etc/nginx/nginx.conf

# Passer à l'utilisateur non privilégié
USER appuser

# Exposer le port 8000 pour le serveur Django
EXPOSE 8000 
#EXPOSE 8000 8000

# Commande de démarrage DEV
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# Commande de démarrage PROD
#CMD service nginx start && gunicorn OrchestrationRouteurCISCO.wsgi:application --bind 0.0.0.0:8000 --workers 4
