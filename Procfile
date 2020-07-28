web: gunicorn gettingstarted.wsgi --log-file -
worker: celery -A tasks.py worker -B --loglevel=info
