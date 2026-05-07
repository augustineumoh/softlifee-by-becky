web: python manage.py collectstatic --noinput && gunicorn softlifee.wsgi --workers 4 --threads 4 --worker-class gthread --timeout 60 --keep-alive 5 --log-file -
release: python manage.py migrate && python manage.py create_superuser_auto && python manage.py seed_products
