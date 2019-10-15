from django.contrib.sitemaps import Sitemap, GenericSitemap
from django.urls import reverse

from switchdeck import models


class StaticViewSitemap(Sitemap):
    priority = 0.7
    changefreq = 'always'

    def items(self):
        return ['index', 'places', 'users', 'games']

    def location(self, obj):
        return reverse(obj)


sitemaps = {
    'static': StaticViewSitemap,
    'place': GenericSitemap(
        {'queryset': models.Place.objects.all()},
        priority=0.8,
        changefreq='always'),
    'game': GenericSitemap(
        {'queryset': models.Game.objects.all()},
        priority=0.8,
        changefreq='always'),
    'gamelist': GenericSitemap(
        {'queryset': models.GameList.objects.filter(active=True),
         'date_field': 'up_time'},
        priority=0.5,
        changefreq='always'),
    'profile': GenericSitemap(
        {'queryset': models.Profile.objects.filter(user__is_active=True),
         'date_field': 'user__last_login'},
        priority=0.4,
        changefreq='daily')}