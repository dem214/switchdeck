from django.db import models
from django.utils.translation import gettext_lazy as _


class Catalog(models.Model):
    """Model of sites where games can be brought."""
    name = models.CharField(
        max_length=30,
        unique=True,
        verbose_name=_('Name')
    )
    slug = models.SlugField(
        max_length=30,
        unique=True,
        verbose_name="Slug",
        allow_unicode=False,
    )
    url = models.URLField(
        max_length=200,
        verbose_name="URL",
        help_text="Main page URL."
    )
    
    class Meta:
        verbose_name=_("Catalog")
        verbose_name_plural=_("Catalogs")

    def __repr__(self) -> str:
        return f'<Catalog {self.name}>'

    def __str__(self) -> str:
        return self.name