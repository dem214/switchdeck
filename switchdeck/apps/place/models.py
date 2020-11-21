from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

# Create your models here.

class Place(models.Model):
    """Represent place for convinient searching."""
    name = models.CharField(
        max_length=20,
        unique=True,
        verbose_name=_('Name'),
        help_text=_("Name of the region or city."))
    slug = models.SlugField()
    popularity = models.IntegerField(
        default=0,
        help_text=_("Popularity of place. The higher popularity - the higher "
                    "this place in place list."),
        verbose_name=_('Popularity')
    )

    class Meta():
        """Meta class for some `Place` class properties."""

        # order of descending popularity
        ordering = ['-popularity', 'name']
        verbose_name = _('Place')
        verbose_name_plural = _('Places')

    def __str__(self) -> str:
        """Return string representation of the Place (Place name)."""
        return self.name

    def get_absolute_url(self) -> str:
        """Return URL, there placed the info about a Place."""
        return reverse('place_view', args=[self.slug])
        

