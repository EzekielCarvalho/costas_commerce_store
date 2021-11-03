web: gunicorn django_project.wsgi:costas --log-file - --log-level debug
python manage.py collectstatic --noinput
manage.py migrate