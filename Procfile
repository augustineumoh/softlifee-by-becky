web: python manage.py collectstatic --noinput && gunicorn softlifee.wsgi --workers 2 --threads 2 --worker-class gthread --log-file -
release: python manage.py migrate && python manage.py create_superuser_auto
