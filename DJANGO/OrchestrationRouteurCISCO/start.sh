#!/bin/bash

echo "Starting the Docker environment..."

docker compose build
docker compose up -d

echo "Waiting for the database..."
sleep 10

echo "Automatically creating migration files..."
docker compose exec web python manage.py makemigrations --noinput

echo "Applying database migrations..."
docker compose exec web python manage.py migrate --noinput

echo "Running the data population script..."
docker compose exec web python orchestration/init_data.py

echo "Collecting static files..."
docker compose exec web python manage.py collectstatic --noinput

echo "Server is ready at http://localhost:8080"
