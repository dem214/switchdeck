from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AccountConfig(AppConfig):
    name = 'switchdeck.apps.account'
    verbose_name = _('Account')
    verbose_name_plural = _('Accounts')
