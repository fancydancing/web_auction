#!/bin/sh

until PGPASSWORD="django_password" psql -h "db" -d "web_auction" -U "django_user" -c '\q'; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

>&2 echo "Postgres is up - executing command"

python manage.py makemigrations auction
python manage.py migrate
exec "$@"