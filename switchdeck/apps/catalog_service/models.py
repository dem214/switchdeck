from bs4 import BeautifulSoup
import requests
from decimal import Decimal
from tempfile import NamedTemporaryFile

from django.db import models
from django.core.files.base import ContentFile
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
        verbose_name = _("Catalog")
        verbose_name_plural = _("Catalogs")

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
        verbose_name = _("Link")
        verbose_name_plural = _("Links")
        default_related_name = 'links'
        unique_together = ['game', 'catalog']

    def __repr__(self) -> str:
        return f'<Link {self.game.name} in {self.catalog.name}>'

    def __str__(self) -> str:
        return gettext(f'{self.game.name} in {self.catalog.name}')

    def parse(self):
        page = None
        try:
            resp = requests.get(self.url)
            page = resp.text
            tempfile = NamedTemporaryFile('w')
            # with open(tempfile) as f:
            #     f.write(page)
            tempfile = ContentFile(page)
            if resp.status_code != 200:
                raise Exception(f'On request to {self.url} got status {resp.status_code}.')
            soup = BeautifulSoup(page, 'html.parser')
            price_string = soup.select(self.catalog.price_selector)[0].get_text()
            price_string = price_string.split()[0].strip()
            price_string = price_string.replace(',', '.')
            price = Decimal(price_string)
        except Exception as e:
            result = ParseResult.objects.create(
                link=self,
                page_file=tempfile,
                exception=str(e),
                successful=False,
            )
            return result
        result = ParseResult.objects.create(
            link=self,
            page_file=tempfile,
            price=price,
        )
        return result
        
            


def upload_to_file_page(instance, filename):
    return '{catalog}/{year}/{month}/{day}/{game}_at_{isodatetime}.html'.format(
        catalog=instance.link.catalog.slug,
        year=instance.time.year,
        month=instance.time.month,
        day=instance.time.day,
        game=instance.link.game.slug,
        isodatetime=instance.time.isoformat(timespec='seconds'),
    )


class ParseResult(models.Model):
    """Saved parsing results of links."""
    link = models.ForeignKey(
        Link,
        on_delete=models.CASCADE,
        related_name='parse_results',
        related_query_name='parse_result',
        verbose_name=_("Link")
    )
    time = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Time"),
        help_text=("Time of parsing.")
    )
    page_file = models.FileField(
        upload_to=upload_to_file_page,
        verbose_name=_("Page file"),
        help_text=_("Requested and parsed page."),
    )
    price = models.DecimalField(
        null=True, blank=True,
        max_digits=6, decimal_places=2,
        default=None,
        verbose_name=_("Price"),
        help_text=_("Parsed price value.")
    )
    exception = models.TextField(
        null=True, blank=True,
        verbose_name=_("Exception"),
        help_text=_("Text of exception if occured."),
    )
    successful = models.BooleanField(
        default=True,
        verbose_name=_("Successful"),
    )

    class Meta:
        verbose_name = _("Parse Result")
        verbose_name_plural = _("Parse Results")
        ordering = ('-time', )
        get_latest_by=('time', )
