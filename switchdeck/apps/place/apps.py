from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class PlaceConfig(AppConfig):
    name = 'switchdeck.apps.place'
    verbose_name = _('Place')
    verbose_name_plural = _('Places')
