import decimal
from datetime import datetime
from django.db import models
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
    name = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('place', args=[self.name])


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE, editable=False)
    games = models.ManyToManyField("Game", related_name="owners",
        related_query_name="owner", through="GameList")
    place = models.ForeignKey(Place, on_delete=models.SET_DEFAULT, default=1)

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
    name = models.CharField(max_length=50, unique=True)
    cover = models.ImageField(upload_to=games_images_path,
        null=True, blank=True)
    description = models.TextField(blank=True)
    eshop_url = models.URLField(null=True, blank=True)

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
        ('c', 'change'),
        ('b', 'buy'),
        ('w', 'wish')
    )
    profile = models.ForeignKey(Profile,
        on_delete=models.CASCADE)
    game = models.ForeignKey(Game,
        on_delete=models.CASCADE)
    active = models.BooleanField(default=True)
    desc = models.TextField(blank=True, max_length=1000,
        verbose_name='Description')
    prop = models.CharField(max_length=1, choices=PROPS, default='k',
        verbose_name='Proposition')
    price = models.DecimalField(max_digits=6, decimal_places=2,
        default=decimal.Decimal())
    public_date = models.DateTimeField(default=timezone.now)
    up_time = models.DateTimeField(default=timezone.now)
    change_to = models.ManyToManyField("self",
        related_name="ready_change_to",
        blank=True,
        symmetrical = False,
        limit_choices_to = (models.Q(prop='b') | models.Q(prop='w')) & \
            models.Q(profile=models.F("profile")))

    @property
    def place(self):
        return self.profile.place

    class Meta:
        #last upped - first
        ordering=['-up_time']


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

    def set_change_to(self, *args):
        self.change_to.clear()
        for a in args:
            if a.profile == self.profile and \
                (a.prop == 'b' or a.prop == 'w'):
                a.change_to.add(a)

    def get_can_change_to(self):
        return self.profile.games.filter(models.Q(prop='b') | \
            models.Q(prop='w'))

    def get_absolute_url(self):
        return reverse('gamelist_item', args=[self.id,])

    def update_up_time(self):
        self.up_time = timezone.now()
        self.save()


class Comment(models.Model):
    author = models.ForeignKey(Profile, on_delete=models.CASCADE,
        editable=False)
    timestamp = models.DateTimeField(default=timezone.now)
    text = models.TextField(max_length=300)
    game_instance = models.ForeignKey(GameList, on_delete=models.CASCADE,
        related_name='comments', related_query_name='comment',
        editable=False)

    class Meta:
        #old first, new last
        ordering = ['timestamp']

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
