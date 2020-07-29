web: daphne web_auction.asgi:application --port $PORT --bind 0.0.0.0 -v2
worker: celery -A tasks.py worker -B --loglevel=info
worker2: python manage.py runworker -v2