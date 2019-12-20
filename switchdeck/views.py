"""All common views of the path."""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import QueryDict, HttpResponseRedirect
from django.http.response import HttpResponseForbidden
from django.urls import reverse
from django.core.paginator import Paginator
from django.utils import timezone
from django.views.generic import DetailView, ListView, CreateView, FormView
from django.views.decorators.http import require_POST
from django.core.exceptions import PermissionDenied
from django.db import models

from .models import Game, GameList, Comment, Place, Profile
from . import forms

from django.conf import settings
COMMENTS_PER_PAGE = settings.COMMENTS_PER_PAGE
GAMELISTS_PER_PAGE = 15


def index(request):
    """
    Index page view.

    **Context**

    ``games``
        List of available :model:`switchdeck.Game`, ordered by sell popularity.

    **Template**

    :template:`switchdeck/index.html`
    """
    context = {'games': Game.objects_ordered_by_sell()}
    return render(request, 'switchdeck/index.html', context)


def game_id(request, gid):
    """
    Page with game info.

    **Arguments**

    ``gid: int``
        Primary key of the :model:`switchdeck.Game` instance in database.

    **Context**

    ``game``
        An instanse of :model:`switchdeck.Game`.
    ``sell_list``
        Related :model:`switchdeck.GameList` instances, ready to sell.
    ``buy_list``
        Related :model:`switchdeck.GameList` instances, ready to buy.
    ``sell_list_count``
        Amount of related :model:`switchdeck.GameList` instances, ready to
        sell.
    ``buy_list_count``
        Amount of related :model:`switchdeck.GameList` instances, ready to buy.

    **Template**

    :template:`switchdeck/game.html`
    """
    game = get_object_or_404(Game, pk=gid)
    context = {'game': game}
    gamelists_to_sell = game.gamelists_to_sell()
    gamelists_to_buy = game.gamelists_to_buy()
    context['sell_list'] = gamelists_to_sell[:GAMELISTS_PER_PAGE]
    context['buy_list'] = gamelists_to_buy[:GAMELISTS_PER_PAGE]
    context['sell_list_count'] = gamelists_to_sell.count()
    context['buy_list_count'] = gamelists_to_buy.count()
    return render(request, 'switchdeck/game.html', context)


def gamelist_view(request, glid: int):
    """
    Gamelist view with controls and comments.

    **Arguments**

    ``glid: int``
        Primary kay of the :model:`switchdeck.GameList` instance in database.

    **Context**

    ``object``
        An instance of represented :model:`switchdeck.Gamelist`.
    ``form``
        Comment (:model:`switchdeck.Comment`) post form.
    ``comments``
        List of related comments (:model:`switchdeck.Comment`). Paginated.
    ``change_desc_form``
        Form to change description.
    ``change_price_form``
        Form to change price.
    ``objects_per_page``
        Ammount of queried comments per page.

    **Template**

    :template:`switchdeck/gamelist.html`
    """
    gamelist_item = get_object_or_404(GameList, id=glid)
    context = {'object': gamelist_item}
    if request.method == 'POST':
        form = forms.CommentForm(request.POST)
        if form.is_valid():
            if request.user.is_authenticated:
                comm = Comment(author=request.user.profile,
                               game_instance=gamelist_item,
                               text=form.cleaned_data['text'])
                comm.save()
                gamelist_item.update_up_time()
                opp = request.POST.get('objects_per_page', None)
                if opp is not None:
                    opp = int(opp)
                return redirect(comm.get_absolute_url(opp))
            else:
                return redirect('login')
    else:
        context['form'] = forms.CommentForm()
    cpp = request.GET.get('objects-per-page', COMMENTS_PER_PAGE)
    paginator = Paginator(gamelist_item.comments.all(), cpp)
    page = request.GET.get('page', 1)
    context['comments'] = paginator.get_page(page)
    context['change_desc_form'] = forms.ChangeDescGamelistForm(
        {'desc': gamelist_item.desc}
    )
    context['change_price_form'] = forms.ChangePriceGamelistForm(
        {'price': gamelist_item.price}
    )
    if int(request.GET.get('objects-per-page', 0)) > 0:
        context['objects_per_page'] = request.GET['objects-per-page']
    return render(request, 'switchdeck/gamelist.html', context)


@login_required
def add_game(request):
    """Add gamelist method from user."""
    context = dict()
    if request.method == 'POST':
        form = forms.GameListForm(request.POST)
        if form.is_valid():
            gl = GameList(
                profile=request.user.profile,
                game=form.cleaned_data['game'],
                desc=form.cleaned_data['desc'],
                prop=form.cleaned_data['prop'],
                price=form.cleaned_data['price']
            )
            gl.save()
            return redirect(gl)
    else:
        context['form'] = forms.GameListForm()
    return render(request, 'switchdeck/add_game.html', context)


class AddGameBaseView(CreateView, LoginRequiredMixin):
    """View base class for generic add gamelist pages."""

    template_name = "swithcdeck/add_game_reduced.html"


@login_required
def add_game_reduced(request, prop):
    """View func for page to add generic gamelist."""
    context = dict()
    if request.method == 'POST':
        form = forms.GameListReducedForm(request.POST)
        if form.is_valid():
            gl = GameList(
                profile=request.user.profile,
                game=form.cleaned_data['game'],
                desc=form.cleaned_data['desc'],
                prop=prop,
            )
            gl.save()
            messages.success(request, f"{gl.game.name.title()} added to "
                             f"your {gl.get_prop_display()} list")
            return redirect(gl)
    else:
        context['form'] = forms.GameListReducedForm()
        context['prop'] = prop
    return render(request, 'switchdeck/add_game_reduced.html', context)


@login_required
def delete_game(request, glid: int):
    """
    Delete gamelist view.

    Dont render the template, just delete.
    Than redirecting to user profile page.
    """
    gamelist_item = get_object_or_404(GameList, id=glid)
    if request.user == gamelist_item.profile.user:
        gamelist_item.delete()
        messages.success(request, f"{gamelist_item.game.name.title()} removed")
        return redirect(request.user.profile)
    else:
        return HttpResponseForbidden


class GameBaseList(ListView):
    '''Base class for views that return list with sell or buy lots.'''

    template_name = 'switchdeck/game_base_list.html'
    allow_empty = False

    def setup(self, request, *args, **kwargs):
        """Initialize atributes and return 404 for nonexisting games."""
        super().setup(request, *args, **kwargs)
        self.game = get_object_or_404(Game, pk=self.kwargs['gid'])

    def get_paginate_by(self, queryset):
        """Generate pagination with requested size."""
        if int(self.request.GET.get('objects-per-page', 0)) > 0:
            return self.request.GET['objects-per-page']
        else:
            return GAMELISTS_PER_PAGE

    def get_context_data(self, **kwargs):
        """Get context and add info about game."""
        context = super().get_context_data(**kwargs)
        context["game"] = self.game
        if int(self.request.GET.get('objects-per-page', 0)) > 0:
            context['objects_per_page'] = self.request.GET['objects-per-page']
        return context


class GameSellListView(GameBaseList):
    '''
    Class view for list of lots of game to sell.

    **Context**

    ``game``
        Related :model:`switchdeck.Game` instance.
    ``objects``
        List of represented :model:`switchdeck.GameList` instances. Paginated.
    ``objects_per_page``
        Queried ammount of objects per page (related to pagination).
    ``proposition``
        Always is ``sell``.

    **Template**

    :template:`switchdeck/game_base_list.html`
    '''

    extra_context = {'proposition': 'sell'}

    def get_queryset(self):
        """Return queryset of objects to display."""
        return self.game.gamelists_to_sell()


class GameBuyListView(GameBaseList):
    '''
    Class view for list of lots of game to buy.

    **Context**

    ``game``
        Related :model:`switchdeck.Game` instance.
    ``objects``
        List of represented :model:`switchdeck.GameList` instances. Paginated.
    ``objects_per_page``
        Queried ammount of objects per page (related to pagination).
    ``proposition``
        Always is ``buy``.

    **Template**

    :template:`switchdeck/game_base_list.html`
    '''

    extra_context = {'proposition': 'buy'}

    def get_queryset(self):
        """Return queryset of objects to display."""
        return self.game.gamelists_to_buy()


@login_required
def delete_comment(request, cid: int):
    """Veiw delete comment on GET."""
    comment = get_object_or_404(Comment, id=cid)
    next = request.GET.get('next', reverse('index'))
    if request.user == comment.author.user:
        comment.delete()
        messages.success(request, 'Comment removed')
        return redirect(next)
    else:
        return HttpResponseForbidden


@login_required
def set_game(request, glid: int, set_prop: str):
    """Set new prop to that gamelist."""
    context = dict()
    gamelist = get_object_or_404(GameList, id=glid)
    if request.user != gamelist.profile.user:
        return HttpResponseForbidden

    # cleared change_to fields per change of prop
    if (set_prop == 'k' or set_prop == 'w') and (gamelist.prop == 's'
                                                 or gamelist.prop == 'b'):
        gamelist.change_to.clear()
        messages.info("Change list cleared")
    if (set_prop == 's' or set_prop == 'b') and (gamelist.prop == 'k'
                                                 or gamelist.prop == 'w'):
        gamelist.ready_change_to.clear()
        messages.info(request, "Change list cleared")

    if set_prop == 'k' or set_prop == 'w':
        gamelist.prop = set_prop
        gamelist.price = 0
        gamelist.comments.all().delete()
        gamelist.save()
        messages.success(request, f"{gamelist.game.name.title()} setted to "
                         f"{gamelist.get_prop_display()} list")
        return redirect(gamelist)
    elif set_prop == 's' or set_prop == 'b':
        if request.method == 'POST':
            form = forms.SetGameListForm(request.POST)
            if form.is_valid():
                gamelist.prop = set_prop
                gamelist.desc = form.cleaned_data['desc']
                gamelist.price = form.cleaned_data['price']
                gamelist.public_date = timezone.now()
                gamelist.up_time = timezone.now()
                gamelist.save()
                messages.success(request, f"{gamelist.game.name.title()} "
                                 f"setted to {gamelist.get_prop_display()} "
                                 "list")
            return redirect(gamelist)
        else:
            context['form'] = forms.SetGameListForm(
                {'desc': gamelist.desc, 'price': gamelist.price}
            )
            context['set_prop'] = set_prop
            context['gamelist'] = gamelist
        return render(request, 'switchdeck/set_game.html', context)


class PlaceView(DetailView):
    """
    Show the details about Place instance.

    **Arguments**

    ``name: str``
        Name of the place.

    **Context**

    ``object``
        Related :model:`switchdeck.Place` instance.
    ``profiles``
        List of :model:`switchdeck.Profile` instances related to that place.
    ``sell_list``
        List of all available :model:`switchdeck.GameList` objects related to
        this place, ready to sell.
    ``buy_list``
        List of all available :model:`switchdeck.GameList` objects related to
        this place, ready to buy.

    **Template**

    :template:`switchdeck/place_detail.html`
    """

    model = Place
    slug_field = 'name'
    slug_url_kwarg = 'name'

    def get_context_data(self, **kwargs):
        """Insert related context data.

        Insert `Place `object and lists of related profiles and gamelists.
        """
        context = super().get_context_data(**kwargs)
        context['profiles'] = Profile.objects.filter(place=self.object)\
            .order_by("user__username")
        gl_query = GameList.objects.filter(profile__place=self.object)\
            .filter(active=True)
        context['sell_list'] = gl_query.filter(prop='s')
        context['buy_list'] = gl_query.filter(prop='b')
        return context


class PlacesListView(ListView):
    """
    Show all available Places.

    **Context**

    ``objects``
        List of all :model:`switchdeck.Place` instances. Ordered.

    **Template**

    :template:`switchdeck/place_list.html`
    """

    model = Place


@require_POST
@login_required
def change_description(request, glid: int):
    """View method to change description of gamelist."""
    gl = get_object_or_404(GameList, id=glid)
    if gl.profile != request.user.profile:
        return HttpResponseForbidden
    form = forms.ChangeDescGamelistForm(request.POST)
    if form.is_valid():
        gl.desc = form.cleaned_data['desc']
        gl.update_up_time()
        gl.save()
        messages.success(request, message='Description has been changed')
    return redirect(gl.get_absolute_url())


@require_POST
@login_required
def change_price(request, glid: int):
    """View method to price description of gamelist."""
    gl = get_object_or_404(GameList, id=glid)
    if gl.profile != request.user.profile:
        return HttpResponseForbidden
    form = forms.ChangePriceGamelistForm(request.POST)
    if form.is_valid():
        gl.price = form.cleaned_data['price']
        gl.update_up_time()
        gl.save()
        messages.success(request, message='Price has been changed')
    return redirect(gl.get_absolute_url())


@login_required
def change_activation(request, glid: int, activate: bool):
    """View method to change activation status of gamelist."""
    gl = get_object_or_404(GameList, id=glid)
    if gl.profile != request.user.profile:
        return HttpResponseForbidden
    if activate and not gl.active:
        gl.active = True
        gl.save(update_fields=['active'])
    elif not activate and gl.active:
        gl.active = False
        gl.save(update_fields=['active'])
    return redirect(gl.get_absolute_url())


class GamesView(ListView):
    """
    Show the list of all available games.

    **Context**

    ``objects``
        List of all available :model:`switchdeck.Game` instances.
        Ordered by name.

    **Template**

    :template:`switchdeck/games.html`
    """

    model = Game
    template_name = 'switchdeck/games.html'
    ordering = ['name']


class UpdateChangeToView(LoginRequiredMixin, FormView):
    """Update related change field of gamelist."""

    template_name = 'switchdeck/gamelist_change_to.html'
    form_class = forms.ChangeToForm

    def setup(self, request, *args, **kwargs):
        """Initialize atributes or get 404 for nonexisting gamelist."""
        super().setup(request, *args, **kwargs)
        self.object = get_object_or_404(GameList, pk=kwargs['glid'])
        if request.user.is_authenticated\
                and self.object.profile.user != request.user:
            raise PermissionDenied

    def get_form_kwargs(self):
        """Return keyword to install form."""
        kw = super().get_form_kwargs()
        kw['instance'] = self.object
        return kw

    def form_valid(self, form):
        """Change gamelist if form valid."""
        prop = self.object.prop
        changelets = list(form.cleaned_data['changelets'])
        if prop == 'w' or prop == 'b':
            self.object.change_to.set(changelets)
        elif prop == 'k' or prop == 's':
            self.object.ready_change_to.set(changelets)
        messages.success(self.request, "Change list updated")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        """Initialize context and add additional info there."""
        context = super().get_context_data(**kwargs)
        prop = self.object.prop
        context['object'] = self.object
        if prop == 'k' or prop == 's':
            context['is_ready_to_change'] = True
        elif prop == 'w' or prop == 'b':
            context['is_wanna_change'] = True
        return context

    def get_success_url(self):
        """Return url in succesful case."""
        return self.object.get_absolute_url()


def search(request):
    """
    Page with form to search gamelsites and results of searching

    **Context**

    ``form``
        Form to search :model:`switchdeck.GameList`.
    ``gamelists``
        List of :model:`switchdeck.GameList` instances - result of searching

    **Template**

    :template:`switchdeck/search.html`
    """

    if request.method == 'GET':
        context = dict()
        context['form'] = forms.SearchForm
        if request.GET.get('query', False):
            context['search_posted'] = True
            query = GameList.objects.filter(active=True)
            if request.GET.get('game', '') != '':
                try:
                    game = Game.objects.get(name=request.GET['game'])
                except Game.DoesNotExist:
                    context['no_game'] = request.GET['game']
                else:
                    query = query.filter(game=game)
                    context['game'] = game
            else:
                context['all_game'] = True

            if request.GET.get('place', '') != '':
                try:
                    place = Place.objects.get(name=request.GET['place'])
                except Place.DoesNotExist:
                    context['no_place'] = request.GET['place']
                else:
                    query = query.filter(profile__place=place)
                    context['place'] = place
            else:
                context['all_place'] = True

            prop = request.GET.get('proposition', 'a')
            if prop == 's' or prop == 'b':
                context['prop'] = prop
                query = query.filter(prop=prop)
            else:
                context['prop'] = 'a'
                query = query.filter(models.Q(prop='s') | models.Q(prop='b'))

            context['gamelists'] = query

            context['form'] = forms.SearchForm({
                'game': request.GET.get('game', ''),
                'place': request.GET.get('place', ''),
                'proposition': request.GET.get('proposition', 's')
            })
        return render(request, 'switchdeck/search.html', context)
    elif request.method == 'POST':
        form = forms.SearchForm(request.POST)
        if form.is_valid():
            q = QueryDict(mutable=True)
            q['query'] = True
            q['game'] = form.cleaned_data['game']
            q['place'] = form.cleaned_data['place']
            q['proposition'] = form.cleaned_data['proposition']
            return HttpResponseRedirect(reverse('search') + '?'
                                        + q.urlencode())
