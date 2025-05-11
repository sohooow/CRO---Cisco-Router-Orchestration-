#!/bin/bash

echo "Lancement de l'environnement Docker..."

docker-compose build
docker-compose up -d

echo "Attente de la base de données..."
sleep 10

echo "Création automatique des fichiers de migrations..."
docker-compose exec web python manage.py makemigrations --noinput

echo "Migration de la base de données..."
docker-compose exec web python manage.py migrate --noinput

echo "Collecte des fichiers statiques..."
docker-compose exec web python manage.py collectstatic --noinput

echo "Serveur prêt sur http://localhost:8080"
