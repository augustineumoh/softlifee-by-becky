web: python manage.py collectstatic --noinput && gunicorn softlifee.wsgi --log-file -
release: python manage.py migrate && python manage.py create_superuser_auto