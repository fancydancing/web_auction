web: gunicorn web_auction.wsgi --log-file -
worker: celery -A tasks.py worker -B --loglevel=info