from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CatalogServiceConfig(AppConfig):
    name = 'switchdeck.apps.catalog_service'
    verbose_name = _('Catalog Service')
    verbose_name_plural = _('Catalog Services')