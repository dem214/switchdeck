#!/bin/bash
python /app/manage.py migrate
# /bin/python3 /app/manage.py compilemessages
python /app/manage.py collectstatic -c
gunicorn --config="gunicorn.conf.py" switchdeck.wsgi
