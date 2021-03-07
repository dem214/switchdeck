from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.translation import gettext


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
    price_selector = models.CharField(
        max_length=100,
        verbose_name=_("Price Selector"),
        help_text=_("CSS selector of object with price num.")
    )
    
    class Meta:
        verbose_name=_("Catalog")
        verbose_name_plural=_("Catalogs")

    def __repr__(self) -> str:
        return f'<Catalog {self.name}>'

    def __str__(self) -> str:
        return self.name


class Link(models.Model):
    """Link between game and catalog - url of game page in catalog."""
    game = models.ForeignKey(
        'game.Game',
        on_delete=models.CASCADE,
        verbose_name=_("Game"),
        related_name='links',
        related_query_name='link',
    )
    catalog = models.ForeignKey(
        'catalog_service.Catalog',
        on_delete=models.CASCADE,
        verbose_name=_("Catalog"),
        related_name='links',
        related_query_name='link',
    )
    url = models.URLField(
        max_length=200,
        verbose_name="URL",
        help_text=_("URL of page there this game presented in catalog"),
    )
    active = models.BooleanField(
        default=True,
        verbose_name=_("Active"),
        help_text=_("Determine parsing of this link is enabled."),
    )

    class Meta:
        verbose_name=_("Link")
        verbose_name_plural=_("Links")
        default_related_name='links'
        unique_together=['game', 'catalog']

    def __repr__(self) -> str:
        return f'<Link {self.game.name} in {self.catalog.name}>'

    def __str__(self) -> str:
        return gettext(f'{self.game.name} in {self.catalog.name}')
