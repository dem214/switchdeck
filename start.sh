#!/bin/bash
python /app/manage.py migrate
python /app/manage.py compilemessages
python /app/manage.py collectstatic -c --noinput
gunicorn switchdeck.wsgi
