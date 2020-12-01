"""
Site sitemap.

XML file with some pages, needed for robots and search services crowlers.
"""
from django.contrib.flatpages.sitemaps import FlatPageSitemap
from django.contrib.sitemaps import Sitemap, GenericSitemap
from django.urls import reverse

from switchdeck.apps.place.models import Place
from switchdeck.apps.users.models import Profile
from switchdeck.apps.game.models import Game
from switchdeck.apps.lot.models import Lot, Comment


class StaticViewSitemap(Sitemap):
    """Sitemap for objects and some static pages."""

    priority = 0.7
    changefreq = 'always'

    def items(self):
        """Return lis tof sitemapping items."""
        return ['index', 'places', 'users', 'games', 'search']

    def location(self, obj):
        """Return source location of object."""
        return reverse(obj)


sitemaps = {
    'static': StaticViewSitemap,
    'flatpages': FlatPageSitemap,
    'place': GenericSitemap(
        {'queryset': Place.objects.all()},
        priority=0.8,
        changefreq='always'),
    'game': GenericSitemap(
        {'queryset': Game.objects.all()},
        priority=0.8,
        changefreq='always'),
    'lot': GenericSitemap(
        {'queryset': Lot.objects.filter(active=True),
         'date_field': 'up_time'},
        priority=0.5,
        changefreq='always'),
    'profile': GenericSitemap(
        {'queryset': Profile.objects.filter(user__is_active=True)},
        priority=0.4,
        changefreq='daily')}
