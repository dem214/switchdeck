from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.http.response import HttpResponseForbidden
from django.urls import reverse
from django.core.paginator import Paginator
from django.utils import timezone
from django.views.generic import DetailView, ListView, CreateView
from django.views.generic.edit import FormMixin

from .models import Game, GameList, Comment, Place
from .forms import CommentForm, GameListForm, GameListReducedForm,\
SetGameListForm

COMMENTS_PER_PAGE=10
GAMELISTS_PER_PAGE=15

def index(request):
    """Index page view"""
    context = {'games': Game.objects_ordered_by_sell()}
    return render(request, 'switchdeck/index.html', context)

def game_id(request, gid):
    """Page with game info"""
    game = get_object_or_404(Game , pk=gid)
    context = {'game': game}
    gamelists_to_sell = game.gamelists_to_sell()
    gamelists_to_buy = game.gamelists_to_buy()
    context['sell_list'] = gamelists_to_sell[:GAMELISTS_PER_PAGE]
    context['buy_list'] = gamelists_to_buy[:GAMELISTS_PER_PAGE]
    context['sell_list_count'] = gamelists_to_sell.count()
    context['buy_list_count'] = gamelists_to_buy.count()
    return render(request, 'switchdeck/game.html', context)


def gamelist_view(request, glid: int):
    """Gamelist view with controls and comments

    glid: gamelist id (GameList.id)
    """
    gamelist_item = get_object_or_404(GameList, id=glid)
    context = {'object': gamelist_item}
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            if request.user.is_authenticated:
                comm = Comment(author=request.user.profile,
                    game_instance = gamelist_item,
                    text = form.cleaned_data['text'])
                comm.save()
                gamelist_item.update_up_time()
                return redirect('gamelist_item', gamelist_item.id)
            else:
                return redirect('login')
    else:
        context['form'] = CommentForm()
    cpp = request.GET.get('objects-per-page', COMMENTS_PER_PAGE)
    paginator = Paginator(gamelist_item.comments.all(), cpp)
    page = request.GET.get('page', 1)
    context['comments'] = paginator.get_page(page)
    if int(request.GET.get('objects-per-page', 0)) > 0:
        context['objects_per_page'] = request.GET['objects-per-page']
    return render(request, 'switchdeck/gamelist.html', context)

@login_required
def add_game(request):
    """Add gamelist method from user"""
    context = dict()
    if request.method == 'POST':
        form = GameListForm(request.POST)
        if form.is_valid():
            gl = GameList(
                profile=request.user.profile,
                game=form.cleaned_data['game'],
                desc=form.cleaned_data['desc'],
                prop=form.cleaned_data['prop'],
                price=form.cleaned_data['price']
            )
            gl.save()
            return redirect(gamelist_item)
    else:
        context['form'] = GameListForm()
    return render(request, 'switchdeck/add_game.html', context)

class AddGameBaseView(CreateView, LoginRequiredMixin):
    template_name = "swithcdeck/add_game_reduced.html"

@login_required
def add_game_reduced(request, prop):
    context = dict()
    if request.method == 'POST':
        form = GameListReducedForm(request.POST)
        if form.is_valid():
            gl = GameList(
                profile=request.user.profile,
                game=form.cleaned_data['game'],
                desc=form.cleaned_data['desc'],
                prop=prop,
            )
            gl.save()
            return redirect(gl)
    else:
        context['form'] = GameListReducedForm()
        context['prop'] = prop
    return render(request, 'switchdeck/add_game_reduced.html', context)


@login_required
def delete_game(request, glid: int):
    """Delete view. Dont render the template, just delete"""
    gamelist_item = get_object_or_404(GameList, id=glid)
    if request.user == gamelist_item.profile.user:
        gamelist_item.delete()
        return redirect(request.user.profile)
    else:
        return HttpResponseForbidden


class GameBaseList(ListView):
    '''Base class for views that return list with sell or buy lots'''
    template_name = 'switchdeck/game_base_list.html'
    allow_empty = False

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.game = get_object_or_404(Game, pk=self.kwargs['gid'])

    def get_paginate_by(self, queryset):
        if int(self.request.GET.get('objects-per-page', 0)) > 0:
            return self.request.GET['objects-per-page']
        else:
            return GAMELISTS_PER_PAGE

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["game"] = self.game
        if int(self.request.GET.get('objects-per-page', 0)) > 0:
            context['objects_per_page'] = self.request.GET['objects-per-page']
        return context

class GameSellListView(GameBaseList):
    '''Class view for list of lots of game to sell'''
    extra_context = {'proposition': 'sell'}

    def get_queryset(self):
        return self.game.gamelists_to_sell()

class GameBuyListView(GameBaseList):
    '''Class view for list of lots of game to buy'''
    extra_context = {'proposition': 'buy'}

    def get_queryset(self):
        return self.game.gamelists_to_buy()

@login_required
def delete_comment(request, cid: int):
    comment = get_object_or_404(Comment, id=cid)
    next=request.GET.get('next', reverse('index'))
    if request.user == comment.author.user:
        comment.delete()
        return redirect(next)
    else:
        return HttpResponseForbidden

@login_required
def set_game(request, glid: int, set_prop: str):
    context = dict()
    gamelist = get_object_or_404(GameList, id=glid)
    if request.user != gamelist.profile.user:
        return HttpResponseForbidden
    if set_prop == 'k' or set_prop == 'w':
        gamelist.prop = set_prop
        gamelist.price = 0
        gamelist.comments.all().delete()
        gamelist.save()
        return redirect(gamelist)
    elif set_prop == 's' or set_prop == 'b':
        if request.method == 'POST':
            form = SetGameListForm(request.POST)
            if form.is_valid():
                gamelist.prop = set_prop
                gamelist.desc = form.cleaned_data['desc']
                gamelist.price = form.cleaned_data['price']
                gamelist.public_date = timezone.now()
                gamelist.up_time = timezone.now()
                gamelist.save()
            return redirect(gamelist)
        else:
            form = SetGameListForm()
            form.desc = gamelist.desc
            form.price = gamelist.price
            context['form'] = form
            context['set_prop'] = set_prop
            context['gamelist'] = gamelist
        return render(request, 'switchdeck/set_game.html', context)

class PlaceView(DetailView):
    model = Place
    slug_field = 'name'
    slug_url_kwarg = 'name'

class PlacesListView(ListView):
    model=Place
