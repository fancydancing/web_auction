web: daphne web_auction.asgi:application --port $PORT --bind 0.0.0.0
worker: celery -A tasks.py worker -B --loglevel=info
python manage.py runworker