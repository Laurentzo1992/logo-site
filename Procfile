release: python manage.py migrate --noinput
web: gunicorn logosite.wsgi:application --bind 0.0.0.0:$PORT
