web: daphne web_auction.asgi:channel_layer --port $PORT --bind 0.0.0.0 --log-file -
worker: celery -A tasks.py worker -B --loglevel=info
python manage.py runworker