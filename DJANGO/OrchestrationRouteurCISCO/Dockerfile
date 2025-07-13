# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.12.6
FROM python:${PYTHON_VERSION}-slim as base

# Prevent creation of .pyc files and disable buffering
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Add an unprivileged user
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

# Install system dependencies needed for mysqlclient and other libraries
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    netcat-openbsd \
    libmariadb-dev \
    gcc \
    build-essential \
    libffi-dev \
    libssl-dev \
    nginx \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt into the container
COPY requirements.txt /app/

# Install Python dependencies
RUN python3 -m pip install --no-cache-dir -r requirements.txt

# Copy the rest of the source code into the container
COPY  . .

# Ensure static files are collected (if needed)
RUN python3 manage.py collectstatic --noinput || true

COPY wait-for-mysql.sh /wait-for-mysql.sh
RUN chmod +x /wait-for-mysql.sh

# Copy Nginx configuration into the container
COPY nginx.conf /etc/nginx/nginx.conf

#Set file permissions for static files
RUN chown -R appuser:appuser /app/staticfiles

# Switch to the unprivileged user
USER appuser


# Expose port 8080 for the Django server
EXPOSE 8080 
#EXPOSE 8000 8000

# DEV startup command
#CMD ["python", "manage.py", "runserver", "0.0.0.0:8080"]

# PROD startup command
CMD service nginx start && gunicorn OrchestrationRouteurCISCO.wsgi:application --bind 0.0.0.0:8080 --workers 4

