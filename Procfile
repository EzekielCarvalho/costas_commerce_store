web: gunicorn costas.wsgi:core --log-file - --log-level debug
python manage.py collectstatic --noinput
manage.py migrate