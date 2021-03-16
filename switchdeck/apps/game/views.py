from django.shortcuts import render, get_object_or_404
from django.views.generic import DetailView, ListView

from .models import Game

class GameDetailView(DetailView):
    """
    Page with game info.

    **Arguments**

    ``slug: slug``
        Slug name of the :model:`switchdeck.Game` instance in database.

    **Context**

    ``object``
        An instanse of :model:`switchdeck.Game`.
    ``sell_list``
        Related :model:`switchdeck.Lot` instances, ready to sell.
    ``buy_list``
        Related :model:`switchdeck.Lot` instances, ready to buy.
    
    **Template**

    :template:`game/game-detail.html`
    """

    model = Game

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sell_list'] = self.object.lots_to_sell()
        context['buy_list'] = self.object.lots_to_buy()
        return context

# Create your views here.
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

    :template:`game/game-detail.html`
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

class GameListView(ListView):
    """
    Show the list of all available games.

    **Context**

    ``objects``
        List of all available :model:`switchdeck.Game` instances.
        Ordered by name.

    **Template**

    :template:`switchdeck/game-list.html`
    """

    model = Game
    ordering = ['name']


class GameBaseList(ListView):
    '''Base class for views that return list with sell or buy lots.'''

    template_name = 'switchdeck/game_additional_list.html'
    allow_empty = False

    def setup(self, request, *args, **kwargs):
        """Initialize atributes and return 404 for nonexisting games."""
        super().setup(request, *args, **kwargs)
        self.game = get_object_or_404(Game, slug=self.kwargs['slug'])

    def get_paginate_by(self, queryset):
        """Generate pagination with requested size."""
        return int(self.request.GET.get('objects-per-page', 24))

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

    :template:`switchdeck/game_additional_list.html`
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

    :template:`switchdeck/game_additional_list.html`
    '''

    extra_context = {'proposition': 'buy'}

    def get_queryset(self):
        """Return queryset of objects to display."""
        return self.game.lots_to_buy()
