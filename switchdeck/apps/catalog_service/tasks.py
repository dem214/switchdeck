from switchdeck.celery import app
from .models import Link


@app.task
def parse_all_links(active_only=True):
    links = Link.objects.all()
    if active_only:
        links = links.filter(active=True)
    for link in links:
        link.parse()