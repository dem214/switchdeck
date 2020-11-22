"""List of all used models."""
import decimal

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.urls import reverse
from django.conf import settings

class Lot(models.Model):
    """
    ``Lot`` represent the relation between ``Profile``
    (:model:`switchdeck.Profile`) and `Game` (:model:`switchdeck.Game`)
    such as keep (added to library), wish, sell (setted to sell), buy
    (setted to buy).
    """

    PROPS = (
        ('k', 'keep'),
        ('s', 'sell'),
        ('b', 'buy'),
        ('w', 'wish')
    )
    profile = models.ForeignKey(
        'account.Profile',
        on_delete=models.CASCADE,
        verbose_name=_('Profile'),
        help_text=_("Related Profile. Represent the owner of ``Lot`` "
                    "instance"))
    game = models.ForeignKey(
        'game.Game',
        on_delete=models.CASCADE,
        verbose_name=_('Game'))
    active = models.BooleanField(
        default=True,
        verbose_name=_('Active'),
        help_text=_("Set game to can be founded through the global search."))
    desc = models.TextField(
        blank=True,
        max_length=1000,
        verbose_name=_('Description'),
        help_text=_("Description leaved by the user"))
    prop = models.CharField(
        max_length=1,
        choices=PROPS,
        default='k',
        verbose_name=_('Proposition'),
        help_text=_("Proposition of lot - what user want to do with this "
                    "game."))
    price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=decimal.Decimal(),
        verbose_name=_('Price'),
        help_text=_("Amount of money user want to buy/sell this game.")
    )
    public_date = models.DateTimeField(
        default=timezone.now,
        verbose_name=_('Public date'),
        help_text=_("Date of publication. Just additional information."))
    up_time = models.DateTimeField(
        default=timezone.now,
        verbose_name=_('Up time'),
        help_text=_("Up time show last activity from the lot. "
                    "The newest up time - the highest this lot in lists. "
                    "Up time update from each comment, updating or etc."))
    change_to = models.ManyToManyField(
        "self",
        related_name="ready_change_to",
        blank=True,
        symmetrical=False,
        limit_choices_to=(models.Q(prop='b') | models.Q(prop='w')),
        verbose_name=_("Change to"),
        help_text=_("List of games user want to change this game."))

    class Meta:
        """Meta class for some `Lot` class games."""

        # last upped - first
        ordering = ['-up_time']
        verbose_name = _('Lot')
        verbose_name_plural = _('Lots')

    @property
    def place(self) -> 'Place':
        """
        Return `Place` property of `Lot`.

        Related :model:`switchdeck.Place` instance. Setted by ``Profile``
        field instance
        """
        return self.profile.place

    def __str__(self) -> str:
        """Return readable representation of `Lot`."""
        return f"{self.profile.user} {self.get_prop_display()} " +\
            f"{self.game.name}"

    @property
    def ready_to_sell(self):
        """Return True, if lot ready to sale."""
        return self.prop == 's' and self.active and \
            self.public_date < timezone.now()

    def set_keep(self) -> None:
        """Set `Lot` prop to keep."""
        self.prop = 'k'
        self.price = 0.0
        self.change_to.clear()

    def get_absolute_url(self) -> str:
        """Return url there leaved info about instance."""
        return reverse('lot_item', args=[self.id])

    def update_up_time(self) -> None:
        """Update ``up_time`` to now."""
        self.up_time = timezone.now()
        self.save()
    update_up_time.short_description = _("Update uptime")

    def get_change_to_choices(self):
        """
        Return available variants of change.

        Returns all :model:`switchdeck.Lot` instances of related
        ``Profile`` ready to set to change (marked as ``keep`` and ``sell``).
        """
        return self.profile.lot_set.filter(
            models.Q(prop='k') | models.Q(prop='s'))

    def get_ready_to_change_choices(self):
        """
        Return available variants of pieces ready to be change.

        Returns all :model:`switchdeck.Lot` instances of related
        ``Profile`` ready to set as changable (marked as ``buy`` and ``want``).
        """
        return self.profile.lot_set.filter(
            models.Q(prop='b') | models.Q(prop='w'))


class Comment(models.Model):
    """
    Comment there users can leave comment on the page of
    :view:`switchdeck.views.lot_view`.
    """

    author = models.ForeignKey(
        'account.Profile',
        on_delete=models.CASCADE,
        editable=False,
        verbose_name=_('Author'),
        help_text=_("Author of the comment."))
    timestamp = models.DateTimeField(
        _('Timestamp'),
        auto_now_add=True,
        help_text=_("Date of publication."))
    text = models.TextField(
        max_length=300,
        verbose_name=_('Text'))
    lot = models.ForeignKey(
        Lot,
        on_delete=models.CASCADE,
        related_name='comments',
        related_query_name='comment',
        editable=False,
        verbose_name=_("Lot"),
        help_text=_("Related lot."))

    class Meta:
        """Meta properties of class."""

        # old first, new last
        ordering = ['timestamp']
        verbose_name = _('Comment')
        verbose_name_plural = _('Comments')

    def __str__(self, length: int = 50) -> str:
        """
        Return readable presentation of Comment.

        Used for admin pages.
        Looks like '{Author_name} says {Comment_text}.'
        """
        said = f"'{self.author.get_username()}' says '{self.text}"
        if len(said) > length - 1:
            said = said[:length-47] + "...'"
        else:
            said = said + "'"
        return said

    def get_absolute_url(self, opp: int = None) -> str:
        """Return the URL of page there comment is placed."""
        if opp is None:
            opp = settings.COMMENTS_PER_PAGE
            opp_query = False
        else:
            opp_query = "&objects-per-page=" + str(opp)
        comment_query = "#comment_" + str(self.id)
        lot_query = self.lot.get_absolute_url()
        comment_index = list(self.game_instance.comments.all()).index(self)
        page = comment_index // opp + 1
        if page > 1:
            page_query = "page=" + str(page)
        else:
            page_query = False

        query = lot_query
        if opp_query or page_query:
            query += '?'
            if page_query:
                query += page_query
                if opp_query:
                    query += '&'
            if opp_query:
                query += opp_query
        query += comment_query
        return query
