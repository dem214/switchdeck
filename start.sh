#!/bin/bash
python /app/manage.py migrate
# /bin/python3 /app/manage.py compilemessages
python /app/manage.py collectstatic -c
gunicorn -w 4 switchdeck.wsgi --bind="0.0.0.0:8000" --forwarded-allow-ips="nginx"
