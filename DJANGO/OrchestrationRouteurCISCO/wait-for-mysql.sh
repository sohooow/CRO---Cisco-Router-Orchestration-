#!/bin/sh

# Attendre que MySQL soit prêt
echo "Attente de MySQL à $MYSQL_HOST:$MYSQL_PORT..."
until nc -z "$MYSQL_HOST" "$MYSQL_PORT"; do
  sleep 1
done

echo "MySQL est prêt, démarrage de Django..."
exec "$@"