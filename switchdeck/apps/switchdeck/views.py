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

from .models import Game, Lot, Comment
from . import forms

from django.conf import settings
COMMENTS_PER_PAGE = settings.COMMENTS_PER_PAGE
LOTS_PER_PAGE = 15


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


def game_slug(request, slug):
    """
    Page with game info.

    **Arguments**

    ``slug: slug``
        Slug name of the :model:`switchdeck.Game` instance in database.

    **Context**

    ``game``
        An instanse of :model:`switchdeck.Game`.
    ``sell_list``
        Related :model:`switchdeck.Lot` instances, ready to sell.
    ``buy_list``
        Related :model:`switchdeck.Lot` instances, ready to buy.
    ``sell_list_count``
        Amount of related :model:`switchdeck.Lot` instances, ready to
        sell.
    ``buy_list_count``
        Amount of related :model:`switchdeck.Lot` instances, ready to buy.

    **Template**

    :template:`switchdeck/game.html`
    """
    game = get_object_or_404(Game, slug=slug)
    context = {'game': game}
    lots_to_sell = game.lots_to_sell()
    lots_to_buy = game.lots_to_buy()
    context['sell_list'] = lots_to_sell[:LOTS_PER_PAGE]
    context['buy_list'] = lots_to_buy[:LOTS_PER_PAGE]
    context['sell_list_count'] = lots_to_sell.count()
    context['buy_list_count'] = lots_to_buy.count()
    return render(request, 'switchdeck/game.html', context)


def lot_view(request, glid: int):
    """
    Lot view with controls and comments.

    **Arguments**

    ``glid: int``
        Primary kay of the :model:`switchdeck.Lot` instance in database.

    **Context**

    ``object``
        An instance of represented :model:`switchdeck.Lot`.
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

    :template:`switchdeck/lot.html`
    """
    lot_item = get_object_or_404(Lot, id=glid)
    context = {'object': lot_item}
    if request.method == 'POST':
        form = forms.CommentForm(request.POST)
        if form.is_valid():
            if request.user.is_authenticated:
                comm = Comment(author=request.user.profile,
                               game_instance=lot_item,
                               text=form.cleaned_data['text'])
                comm.save()
                lot_item.update_up_time()
                opp = request.POST.get('objects_per_page', None)
                if opp is not None:
                    opp = int(opp)
                return redirect(comm.get_absolute_url(opp))
            else:
                return redirect('login')
    else:
        context['form'] = forms.CommentForm()
    cpp = request.GET.get('objects-per-page', COMMENTS_PER_PAGE)
    paginator = Paginator(lot_item.comments.all(), cpp)
    page = request.GET.get('page', 1)
    context['comments'] = paginator.get_page(page)
    context['change_desc_form'] = forms.ChangeDescLotForm(
        {'desc': lot_item.desc}
    )
    context['change_price_form'] = forms.ChangePriceLotForm(
        {'price': lot_item.price}
    )
    if int(request.GET.get('objects-per-page', 0)) > 0:
        context['objects_per_page'] = request.GET['objects-per-page']
    return render(request, 'switchdeck/lot.html', context)


@login_required
def add_game(request):
    """Add lot method from user."""
    context = dict()
    if request.method == 'POST':
        form = forms.LotForm(request.POST)
        if form.is_valid():
            gl = Lot(
                profile=request.user.profile,
                game=form.cleaned_data['game'],
                desc=form.cleaned_data['desc'],
                prop=form.cleaned_data['prop'],
                price=form.cleaned_data['price']
            )
            gl.save()
            return redirect(gl)
    else:
        context['form'] = forms.LotForm()
    return render(request, 'switchdeck/add_game.html', context)


class AddGameBaseView(CreateView, LoginRequiredMixin):
    """View base class for generic add lot pages."""

    template_name = "swithcdeck/add_game_reduced.html"


@login_required
def add_game_reduced(request, prop):
    """View func for page to add generic lot."""
    context = dict()
    if request.method == 'POST':
        form = forms.LotReducedForm(request.POST)
        if form.is_valid():
            gl = Lot(
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
        context['form'] = forms.LotReducedForm()
        context['prop'] = prop
    return render(request, 'switchdeck/add_game_reduced.html', context)


@login_required
def delete_game(request, glid: int):
    """
    Delete lot view.

    Dont render the template, just delete.
    Than redirecting to user profile page.
    """
    lot_item = get_object_or_404(Lot, id=glid)
    if request.user == lot_item.profile.user:
        lot_item.delete()
        messages.success(request, f"{lot_item.game.name.title()} removed")
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
        self.game = get_object_or_404(Game, slug=self.kwargs['slug'])

    def get_paginate_by(self, queryset):
        """Generate pagination with requested size."""
        if int(self.request.GET.get('objects-per-page', 0)) > 0:
            return self.request.GET['objects-per-page']
        else:
            return LOTS_PER_PAGE

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
        List of represented :model:`switchdeck.Lot` instances. Paginated.
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
        return self.game.lots_to_sell()


class GameBuyListView(GameBaseList):
    '''
    Class view for list of lots of game to buy.

    **Context**

    ``game``
        Related :model:`switchdeck.Game` instance.
    ``objects``
        List of represented :model:`switchdeck.Lot` instances. Paginated.
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
        return self.game.lots_to_buy()


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
    """Set new prop to that lot."""
    context = dict()
    lot = get_object_or_404(Lot, id=glid)
    if request.user != lot.profile.user:
        return HttpResponseForbidden

    # cleared change_to fields per change of prop
    if (set_prop == 'k' or set_prop == 'w') and (lot.prop == 's'
                                                 or lot.prop == 'b'):
        lot.change_to.clear()
        messages.info("Change list cleared")
    if (set_prop == 's' or set_prop == 'b') and (lot.prop == 'k'
                                                 or lot.prop == 'w'):
        lot.ready_change_to.clear()
        messages.info(request, "Change list cleared")

    if set_prop == 'k' or set_prop == 'w':
        lot.prop = set_prop
        lot.price = 0
        lot.comments.all().delete()
        lot.save()
        messages.success(request, f"{lot.game.name.title()} setted to "
                         f"{lot.get_prop_display()} list")
        return redirect(lot)
    elif set_prop == 's' or set_prop == 'b':
        if request.method == 'POST':
            form = forms.SetLotForm(request.POST)
            if form.is_valid():
                lot.prop = set_prop
                lot.desc = form.cleaned_data['desc']
                lot.price = form.cleaned_data['price']
                lot.public_date = timezone.now()
                lot.up_time = timezone.now()
                lot.save()
                messages.success(request, f"{lot.game.name.title()} "
                                 f"setted to {lot.get_prop_display()} "
                                 "list")
            return redirect(lot)
        else:
            context['form'] = forms.SetLotForm(
                {'desc': lot.desc, 'price': lot.price}
            )
            context['set_prop'] = set_prop
            context['lot'] = lot
        return render(request, 'switchdeck/set_game.html', context)


@require_POST
@login_required
def change_description(request, glid: int):
    """View method to change description of lot."""
    gl = get_object_or_404(Lot, id=glid)
    if gl.profile != request.user.profile:
        return HttpResponseForbidden
    form = forms.ChangeDescLotForm(request.POST)
    if form.is_valid():
        gl.desc = form.cleaned_data['desc']
        gl.update_up_time()
        gl.save()
        messages.success(request, message='Description has been changed')
    return redirect(gl.get_absolute_url())


@require_POST
@login_required
def change_price(request, glid: int):
    """View method to price description of lot."""
    gl = get_object_or_404(Lot, id=glid)
    if gl.profile != request.user.profile:
        return HttpResponseForbidden
    form = forms.ChangePriceLotForm(request.POST)
    if form.is_valid():
        gl.price = form.cleaned_data['price']
        gl.update_up_time()
        gl.save()
        messages.success(request, message='Price has been changed')
    return redirect(gl.get_absolute_url())


@login_required
def change_activation(request, glid: int, activate: bool):
    """View method to change activation status of lot."""
    gl = get_object_or_404(Lot, id=glid)
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
    """Update related change field of lot."""

    template_name = 'switchdeck/lot_change_to.html'
    form_class = forms.ChangeToForm

    def setup(self, request, *args, **kwargs):
        """Initialize atributes or get 404 for nonexisting lot."""
        super().setup(request, *args, **kwargs)
        self.object = get_object_or_404(Lot, pk=kwargs['glid'])
        if request.user.is_authenticated\
                and self.object.profile.user != request.user:
            raise PermissionDenied

    def get_form_kwargs(self):
        """Return keyword to install form."""
        kw = super().get_form_kwargs()
        kw['instance'] = self.object
        return kw

    def form_valid(self, form):
        """Change lot if form valid."""
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
        Form to search :model:`switchdeck.Lot`.
    ``lots``
        List of :model:`switchdeck.Lot` instances - result of searching

    **Template**

    :template:`switchdeck/search.html`
    """

    if request.method == 'GET':
        context = dict()
        context['form'] = forms.SearchForm
        if request.GET.get('query', False):
            context['search_posted'] = True
            query = Lot.objects.filter(active=True)
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

            context['lots'] = query

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
