from django.shortcuts import render

from switchdeck.apps.game.models import Game

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
