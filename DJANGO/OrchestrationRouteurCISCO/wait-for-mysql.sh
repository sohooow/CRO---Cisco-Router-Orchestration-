#!/bin/sh

#  Wait for MySQL to be ready
echo "Waiting for MySQL at $MYSQL_HOST:$MYSQL_PORT..."
until nc -z "$MYSQL_HOST" "$MYSQL_PORT"; do
  sleep 1
done

echo "MySQL is ready, starting Django..."
exec "$@"