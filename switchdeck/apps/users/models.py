from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from django.conf import settings
from django.contrib.auth import get_user_model


class User(AbstractUser):
    """Class of user.Inherits from AbstractUser login methods and add link
    to `Profile` instance
    """

    def get_absolute_url(self):
        """
        Return the URL of User.

        Refer to the related :model:``switchdeck.Profile`` instance.
        """
        return reverse('account:profile_detail', args=[self.get_username()])


class Profile(models.Model):
    """Profile have link to User identity and additional information."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profiles",
        editable=False,
        verbose_name=_("User"),
        help_text=_("Link to the user instanse, which have authentication "
                    "methods, email, first name, last name, etc."))
    games = models.ManyToManyField(
        'game.Game',
        related_name="owners",
        related_query_name="owner", through="lot.Lot",
        verbose_name=_("Games"),
        help_text=_("All games user have"))
    place = models.ForeignKey(
        'place.Place',
        on_delete=models.SET_DEFAULT,
        default=1,
        verbose_name=_("Place"),
        help_text=_("Place of registration of user. Place of all his "
                    "lots."))

    class Meta():
        """Meta class for some `Profile` class properties."""

        verbose_name = _("Profile")
        verbose_name_plural = _("Profiles")

    def __str__(self) -> str:
        """Return the string representation of Profile (Profile username)."""
        return self.user.get_username()

    def get_absolute_url(self) -> str:
        """Return URL there placed info about Profile."""
        return reverse('users:list', args=[self.get_username()])

    def get_username(self) -> str:
        """Username of Profile."""
        return self.user.get_username()

    def keep_list(self, with_inactive: bool = False):
        """
        Return list with keep or sell prop instalnces.

        Retrun the list of related :model:`switchdeck.Lot` instances
        marked as ``keep`` or ``sell``.
        """
        query = self.lot_set.filter(
            models.Q(prop='k') | models.Q(prop='s')
        )
        if not with_inactive:
            query = query.filter(active=True)
        return query.order_by('game__name')

    def wish_list(self, with_inactive: bool = False):
        """
        Return list with wish or buy prop instances.

        Retrun the list of related :model:`switchdeck.Lot` instances
        marked as ``wish`` or ``buy``.
        """
        query = self.lot_set.filter(
            models.Q(prop='w') | models.Q(prop='b'))
        if not with_inactive:
            query = query.filter(active=True)
        return query.order_by('game__name')

    def sell_list(self, with_inactive: bool = False):
        """
        Return list with sell instances.

        Retrun the list of related :model:`switchdeck.Lot` instances
        marked as ``sell``.
        """
        query = self.lot_set.filter(prop='s')
        if not with_inactive:
            query = query.filter(active=True)
        return query.order_by('-public_date')

    def buy_list(self, with_inactive: bool = False):
        """
        Return list with buy prop instances.

        Retrun the list of related :model:`switchdeck.Lot` instances
        marked as ``buy``.
        """
        query = self.lot_set.filter(prop='b')
        if not with_inactive:
            query = query.filter(active=True)
        return query.order_by('-public_date')

    @classmethod
    def create_profile(cls, *args, place: 'Place', **kwargs):
        """Create new profile.

        Refers to :model:`swithcdeck.User` `create_user` method
        """
        user = get_user_model().objects.create_user(*args, **kwargs)
        return cls.objects.create(user=user, place=place)

