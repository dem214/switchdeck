"""List of all used models."""
import decimal

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.urls import reverse
from django.conf import settings


class User(AbstractUser):
    """Class of user.Inherits from AbstractUser login methods and add link
    to `Profile` instance
    """

    def get_absolute_url(self):
        """
        Return the URL of User.

        Refer to the related :model:``switchdeck.Profile`` instance.
        """
        return reverse('profile', args=[self.get_username()])


class Place(models.Model):
    """Represent place for convinient searching."""

    name = models.CharField(
        max_length=20,
        unique=True,
        verbose_name=_('Name'),
        help_text=_("Name of the region or city."))
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
        return reverse('place', args=[self.name])


class Profile(models.Model):
    """Profile have link to User identity and additional information."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        editable=False,
        verbose_name=_("User"),
        help_text=_("Link to the user instanse, which have authentication "
                    "methods, email, first name, last name, etc."))
    games = models.ManyToManyField(
        "Game",
        related_name="owners",
        related_query_name="owner", through="GameList",
        verbose_name=_("Games"),
        help_text=_("All games user have"))
    place = models.ForeignKey(
        Place,
        on_delete=models.SET_DEFAULT,
        default=1,
        verbose_name=_("Place"),
        help_text=_("Place of registration of user. Place of all his "
                    "gamelists."))

    class Meta():
        """Meta class for some `Profile` class properties."""

        verbose_name = _("Profile"),
        verbose_name_plural = _("Profiles")

    def __str__(self) -> str:
        """Return the string representation of Profile (Profile username)."""
        return self.user.get_username()

    def get_absolute_url(self) -> str:
        """Return URL there placed info about Profile."""
        return reverse('profile', args=[self.user.username])

    def get_username(self) -> str:
        """Username of Profile."""
        return self.user.get_username()

    def keep_list(self, with_inactive: bool = False):
        """
        Return list with keep or sell prop instalnces.

        Retrun the list of related :model:`switchdeck.GameList` instances
        marked as ``keep`` or ``sell``.
        """
        query = self.gamelist_set.filter(
            models.Q(prop='k') | models.Q(prop='s')
        )
        if not with_inactive:
            query = query.filter(active=True)
        return query.order_by('game__name')

    def wish_list(self, with_inactive: bool = False):
        """
        Return list with wish or buy prop instances.

        Retrun the list of related :model:`switchdeck.GameList` instances
        marked as ``wish`` or ``buy``.
        """
        query = self.gamelist_set.filter(
            models.Q(prop='w') | models.Q(prop='b'))
        if not with_inactive:
            query = query.filter(active=True)
        return query.order_by('game__name')

    def sell_list(self, with_inactive: bool = False):
        """
        Return list with sell instances.

        Retrun the list of related :model:`switchdeck.GameList` instances
        marked as ``sell``.
        """
        query = self.gamelist_set.filter(prop='s')
        if not with_inactive:
            query = query.filter(active=True)
        return query.order_by('-public_date')

    def buy_list(self, with_inactive: bool = False):
        """
        Return list with buy prop instances.

        Retrun the list of related :model:`switchdeck.GameList` instances
        marked as ``buy``.
        """
        query = self.gamelist_set.filter(prop='b')
        if not with_inactive:
            query = query.filter(active=True)
        return query.order_by('-public_date')

    @classmethod
    def create_profile(cls, *args, place: Place, **kwargs):
        """Create new profile.

        Refers to :model:`swithcdeck.User` `create_user` method
        """
        user = get_user_model().objects.create_user(*args, **kwargs)
        return cls.objects.create(user=user, place=place)


def games_images_path(instance, filename: str) -> str:
    """Generate fs path to save image file.

    :param instance: Related Game instance.
    :param filename: Name of the posted file.
    :type filename: str
    :returns: Path to save the file.
    :rtype: str
    """
    return "games_images/" + instance.underscored_name + "/" + filename


class Game(models.Model):
    """Stores the information about available games."""

    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_('Name'),
        help_text=_("Full name of the game in english "
                    "(may look from the shop page)."))
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

    class Meta():
        """Meta class for some `Game` class properties."""

        verbose_name = _('Game')
        verbose_name_plural = _('Games')

    def gamelists_to_sell(self):
        """
        Return list with gamelists for sell.

        Get list of related :model:`switchdeck.GameList` instances marked as
        ``sell``.
        """
        return self.gamelist_set.filter(active__exact=True).\
            filter(public_date__lte=timezone.now()).\
            filter(prop='s')

    def gamelists_to_buy(self):
        """
        Return list with gamelists for buy.

        Get list of related :model:`switchdeck.GameList` instances marked as
        ``buy``.
        """
        return self.gamelist_set.filter(active__exact=True).\
            filter(public_date__lte=timezone.now()).\
            filter(prop='b')

    @property
    def underscored_name(self) -> str:
        """
        Return fs readable names.

        Return lowerscale name of game and replaced ' ' to '_' (fs friendly).
        """
        return self.name.replace(" ", "_").lower()

    def __repr__(self) -> str:
        """Readable representation for Game instance."""
        return f"<Game: '{self.name}'>"

    def __str__(self) -> str:
        """Return name of game when printing."""
        return self.name

    def get_absolute_url(self) -> str:
        """Return the URL there this ``Game`` can founded."""
        return reverse('game_id', args=[self.id])

    @classmethod
    def objects_ordered_by_sell(cls):
        """
        Return ordered list of all games.

        Get list of all games ordered by ammount of active GameLists marked
        as ``sell``.
        """
        return cls.objects.annotate(
            num_of_sales=models.Count(
                'gamelist',
                filter=models.Q(gamelist__prop='s')
                & models.Q(gamelist__public_date__lte=timezone.now())
                & models.Q(gamelist__active=True)))\
            .order_by('-num_of_sales')


class GameList(models.Model):
    """
    ``GameList`` represent the relation between ``Profile``
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
        Profile,
        on_delete=models.CASCADE,
        verbose_name=_('Profile'),
        help_text=_("Related Profile. Represent the owner of ``GameList`` "
                    "instance"))
    game = models.ForeignKey(
        Game,
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
        help_text=_("Proposition of gamelist - what user want to do with this "
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
        help_text=_("Up time show last activity from the gamelist. "
                    "The newest up time - the highest this gamelist in lists. "
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
        """Meta class for some `Gamelist` class games."""

        # last upped - first
        ordering = ['-up_time']
        verbose_name = _('GameList')
        verbose_name_plural = _('GameLists')

    @property
    def place(self) -> Place:
        """
        Return `Place` property of `Gamelist`.

        Related :model:`switchdeck.Place` instance. Setted by ``Profile``
        field instance
        """
        return self.profile.place

    def __str__(self) -> str:
        """Return readable representation of `Gamelist`."""
        return f"{self.profile.user} {self.get_prop_display()} " +\
            f"{self.game.name}"

    @property
    def ready_to_sell(self):
        """Return True, if gamelist ready to sale."""
        return self.prop == 's' and self.active and \
            self.public_date < timezone.now()

    def set_keep(self) -> None:
        """Set `Gamelist` prop to keep."""
        self.prop = 'k'
        self.price = 0.0
        self.change_to.clear()

    def get_absolute_url(self) -> str:
        """Return url there leaved info about instance."""
        return reverse('gamelist_item', args=[self.id])

    def update_up_time(self) -> None:
        """Update ``up_time`` to now."""
        self.up_time = timezone.now()
        self.save()
    update_up_time.short_description = _("Update uptime")

    def get_change_to_choices(self):
        """
        Return available variants of change.

        Returns all :model:`switchdeck.GameList` instances of related
        ``Profile`` ready to set to change (marked as ``keep`` and ``sell``).
        """
        return self.profile.gamelist_set.filter(
            models.Q(prop='k') | models.Q(prop='s'))

    def get_ready_to_change_choices(self):
        """
        Return available variants of pieces ready to be change.

        Returns all :model:`switchdeck.GameList` instances of related
        ``Profile`` ready to set as changable (marked as ``buy`` and ``want``).
        """
        return self.profile.gamelist_set.filter(
            models.Q(prop='b') | models.Q(prop='w'))


class Comment(models.Model):
    """
    Comment there users can leave comment on the page of
    :view:`switchdeck.views.gamelist_view`.
    """

    author = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        editable=False,
        verbose_name=_('Author'),
        help_text=_("Author of the comment."))
    timestamp = models.DateTimeField(
        default=timezone.now,
        verbose_name=_('Timestamp'),
        help_text=_("Date of publication."))
    text = models.TextField(
        max_length=300,
        verbose_name=_('Text'))
    game_instance = models.ForeignKey(
        GameList,
        on_delete=models.CASCADE,
        related_name='comments',
        related_query_name='comment',
        editable=False,
        verbose_name=_("GameList"),
        help_text=_("Related gamelist."))

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
        gamelist_query = self.game_instance.get_absolute_url()
        comment_index = list(self.game_instance.comments.all()).index(self)
        page = comment_index // opp + 1
        if page > 1:
            page_query = "page=" + str(page)
        else:
            page_query = False

        query = gamelist_query
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
