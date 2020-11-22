from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class GameConfig(AppConfig):
    name = 'switchdeck.apps.game'
    verbose_name = _('Game')
    verbose_name_plural = _('Games')
