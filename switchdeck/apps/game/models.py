from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.urls import reverse
from django.conf import settings

# Create your models here.
def games_images_path(instance, filename: str) -> str:
    """Generate fs path to save image file.

    :param instance: Related Game instance.
    :param filename: Name of the posted file.
    :type filename: str
    :returns: Path to save the file.
    :rtype: str
    """
    return "games_images/" + instance.slug + "/" + filename


class Game(models.Model):
    """Stores the information about available games."""

    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_('Name'),
        help_text=_("Full name of the game in english "
                    "(may look from the shop page)."))
    slug = models.SlugField(
        max_length=30,
        verbose_name="Slug",
        allow_unicode=False
    )
    cover = models.ImageField(
        upload_to=games_images_path,
        null=True,
        blank=True,
        verbose_name=_('Cover'),
        help_text=_("Cover of the game box or any related image."))
    description = models.TextField(
        blank=True,
        verbose_name=_('Description'),
        help_text=_("Description of the game. Related from shop page."))
    eshop_url = models.URLField(
        null=True,
        blank=True,
        verbose_name=_('Link to eshop'),
        help_text=_("Link to page there can locate additional information "
                    "(nintendo eshop)."))
    catalogs = models.ManyToManyField(
        'catalog_service.Catalog',
        through='catalog_service.Link',
        through_fields=('game', 'catalog'),
        related_name='games',
        related_query_name='game',
    )

    class Meta():
        """Meta class for some `Game` class properties."""

        verbose_name = _('Game')
        verbose_name_plural = _('Games')

    def lots_to_sell(self):
        """
        Return list with lots for sell.

        Get list of related :model:`switchdeck.Lot` instances marked as
        ``sell``.
        """
        return self.lot_set.filter(active__exact=True).\
            filter(public_date__lte=timezone.now()).\
            filter(prop='s')

    def lots_to_buy(self):
        """
        Return list with lots for buy.

        Get list of related :model:`switchdeck.Lot` instances marked as
        ``buy``.
        """
        return self.lot_set.filter(active__exact=True).\
            filter(public_date__lte=timezone.now()).\
            filter(prop='b')

    def __repr__(self) -> str:
        """Readable representation for Game instance."""
        return f"<Game: '{self.name}'>"

    def __str__(self) -> str:
        """Return name of game when printing."""
        return self.name

    def get_absolute_url(self) -> str:
        """Return the URL there this ``Game`` can founded."""
        return reverse('game:game_detail', args=[self.slug])

    @classmethod
    def objects_ordered_by_sell(cls):
        """
        Return ordered list of all games.

        Get list of all games ordered by ammount of active Lots marked
        as ``sell``.
        """
        return cls.objects.annotate(
            num_of_sales=models.Count(
                'lot',
                filter=models.Q(lot__prop='s')
                & models.Q(lot__public_date__lte=timezone.now())
                & models.Q(lot__active=True)))\
            .order_by('-num_of_sales')

