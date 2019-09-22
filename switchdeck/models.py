import decimal
from datetime import datetime
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.urls import reverse
from django.conf import settings

#from .views import COMMENTS_PER_PAGE

class User(AbstractUser):

    def get_absolute_url(self):
        return reverse('profile', args=[self.get_username()])

class Place(models.Model):
    """Represent place for convinient searching"""
    name = models.CharField(max_length=20, unique=True, verbose_name=_('Name'),
        help_text=_("Name of the region or city."))
    popularity = models.IntegerField(default=0,
        help_text=_("Popularity of place. The higher popularity - the higher this place in place list."),
        verbose_name=_('Popularity')
    )

    class Meta():
        #order of descending popularity
        ordering = ['-popularity', 'name']
        verbose_name = _('Place')
        verbose_name_plural = _('Places')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('place', args=[self.name])


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE, editable=False,
        verbose_name=_("User"),
        help_text=_("Link to the user instanse, which have authentication methods, email, first name, last name, etc."))
    games = models.ManyToManyField("Game", related_name="owners",
        related_query_name="owner", through="GameList",
        verbose_name=_("Games"),
        help_text=_("All games user have"))
    place = models.ForeignKey(Place, on_delete=models.SET_DEFAULT, default=1,
        verbose_name=_("Place"),
        help_text=_("Place of registration of user. Place of all his gamelists."))

    class Meta():
        verbose_name = _("Profile"),
        verbose_name_plural = _("Profiles")

    def __str__(self):
        return self.user.get_username()

    def get_absolute_url(self):
        return reverse('profile', args=[self.user.username])

    def get_username(self):
        return self.user.get_username()

    def keep_list(self, with_inactive=False):
        query = self.gamelist_set.filter(
            models.Q(prop='k') | models.Q(prop='s')
        )
        if not with_inactive:
            query = query.filter(active=True)
        return query.order_by('game__name')

    def wish_list(self, with_inactive=False):
        query = self.gamelist_set.filter(
            models.Q(prop='w') | models.Q(prop='b'))
        if not with_inactive:
            query = query.filter(active=True)
        return query.order_by('game__name')

    def sell_list(self, with_inactive=False):
        query = self.gamelist_set.filter(prop='s')
        if not with_inactive:
            query = query.filter(active=True)
        return query.order_by('-public_date')

    def buy_list(self, with_inactive=False):
        query = self.gamelist_set.filter(prop='b')
        if not with_inactive:
            query = query.filter(active=True)
        return query.order_by('-public_date')

    @classmethod
    def create_profile(cls, *args, place, **kwargs):
        user = get_user_model().objects.create_user(*args, **kwargs)
        return cls.objects.create(user=user, place=place)



def games_images_path(instance, filename):
    return "games_images/" + instance.underscored_name + "/" + filename

class Game(models.Model):
    name = models.CharField(max_length=50, unique=True,
        verbose_name=_('Name'),
        help_text=_("Full name of the game in english (may look from the shop page)."))
    cover = models.ImageField(upload_to=games_images_path,
        null=True, blank=True, verbose_name=_('Cover'),
        help_text=_("Cover of the game box or any related image."))
    description = models.TextField(blank=True,
        verbose_name=_('Description'),
        help_text=_("Description of the game. Related from shop page."))
    eshop_url = models.URLField(null=True, blank=True,
        verbose_name=_('Link to eshop'),
        help_text=_("Link to page there can locate additional information (nintendo eshop)."))

    class Meta():
        verbose_name = _('Game')
        verbose_name_plural = _('Games')

    def gamelists_to_sell(self):
        return self.gamelist_set.filter(active__exact=True).\
            filter(public_date__lte = timezone.now()).\
            filter(prop='s')

    def gamelists_to_buy(self):
        return self.gamelist_set.filter(active__exact=True).\
            filter(public_date__lte = timezone.now()).\
            filter(prop='b')

    @property
    def underscored_name(self):
        return self.name.replace(" ", "_").lower()

    def __repr__(self):
        return f"<Game: '{self.name}'>"
    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('game_id', args=[self.id,])

    @classmethod
    def objects_ordered_by_sell(cls):
        return cls.objects.annotate(num_of_sales=models.Count('gamelist',
            filter=models.Q(gamelist__prop='s') & \
            models.Q(gamelist__public_date__lte=timezone.now()) &
            models.Q(gamelist__active=True)))\
            .order_by('-num_of_sales')


class GameList(models.Model):
    PROPS = (
        ('k', 'keep'),
        ('s', 'sell'),
        ('b', 'buy'),
        ('w', 'wish')
    )
    profile = models.ForeignKey(Profile,
        on_delete=models.CASCADE, verbose_name=_('Profile'))
    game = models.ForeignKey(Game,
        on_delete=models.CASCADE, verbose_name=_('Game'))
    active = models.BooleanField(default=True, verbose_name=_('Active'),
        help_text=_("Set game to can be founded through the global search."))
    desc = models.TextField(blank=True, max_length=1000,
        verbose_name=_('Description'),
        help_text=_("Description leaved by the user"))
    prop = models.CharField(max_length=1, choices=PROPS, default='k',
        verbose_name=_('Proposition'),
        help_text=_("Proposition of gamelist - what user want to do with this game."))
    price = models.DecimalField(max_digits=6, decimal_places=2,
        default=decimal.Decimal(),
        verbose_name = _('Price'),
        help_text=_("Amount of money user want to buy/sell this game.")
    )
    public_date = models.DateTimeField(default=timezone.now,
        verbose_name=_('Public date'),
        help_text=_("Date of publication. Just additional information."))
    up_time = models.DateTimeField(default=timezone.now,
        verbose_name=_('Up time'),
        help_text=_("Up time show last activity from the gamelist. The newest up time - the highest this gamelist in lists. Up time update from each comment, updating or etc."))
    change_to = models.ManyToManyField("self",
        related_name="ready_change_to",
        blank=True,
        symmetrical=False,
        limit_choices_to=(models.Q(prop='b') | models.Q(prop='w')),
        verbose_name=_("Change to"),
        help_text=_("List of games user want to change this game.")
    )


    class Meta:
        #last upped - first
        ordering=['-up_time']
        verbose_name = _('GameList')
        verbose_name_plural = _('GameLists')


    @property
    def place(self):
        return self.profile.place

    def __str__(self):
        return f"{self.profile.user} {self.get_prop_display()} \
{self.game.name}"

    @property
    def ready_to_sell(self):
        return self.prop == 's' and self.active and \
            self.public_date < timezone.now()

    def set_keep(self):
        self.prop = 'k'
        self.price = 0.0
        self.change_to.clear()

    def get_absolute_url(self):
        return reverse('gamelist_item', args=[self.id,])

    def update_up_time(self):
        self.up_time = timezone.now()
        self.save()
    update_up_time.short_description = _("Update uptime")

    def get_change_to_choices(self):
        return self.profile.gamelist_set.filter(
            models.Q(prop='k') | models.Q(prop='s'))

    def get_ready_to_change_choices(self):
        return self.profile.gamelist_set.filter(
            models.Q(prop='b') | models.Q(prop='w'))


class Comment(models.Model):
    author = models.ForeignKey(Profile, on_delete=models.CASCADE,
        editable=False, verbose_name=_('Author'),
        help_text=_("Author of the comment."))
    timestamp = models.DateTimeField(default=timezone.now,
        verbose_name=_('Timestamp'),
        help_text=_("Date of publication."))
    text = models.TextField(max_length=300, verbose_name=_('Text'))
    game_instance = models.ForeignKey(GameList, on_delete=models.CASCADE,
        related_name='comments', related_query_name='comment',
        editable=False, verbose_name=_("GameList"),
        help_text=_("Related gamelist."))

    class Meta:
        #old first, new last
        ordering = ['timestamp']
        verbose_name = _('Comment')
        verbose_name_plural = _('Comments')

    def __str__(self, length=50):
        said = f"'{self.author.get_username()}' says '{self.text}"
        if len(said) > length - 1:
            said = said[:length-47] + "...'"
        else:
            said = said + "'"
        return said

    def get_absolute_url(self, opp=None):
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