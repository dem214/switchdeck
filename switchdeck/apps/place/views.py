from django.shortcuts import render
from django.views.generic import DetailView, ListView

from switchdeck.apps.switchdeck.models import Lot

from .models import Place

# Create your views here.

class PlaceView(DetailView):
    """
    Show the details about Place instance.

    **Arguments**

    ``name: str``
        Name of the place.

    **Context**

    ``object``
        Related :model:`switchdeck.Place` instance.
    ``sell_list``
        List of all available :model:`switchdeck.Lot` objects related to
        this place, ready to sell.
    ``buy_list``
        List of all available :model:`switchdeck.Lot` objects related to
        this place, ready to buy.

    **Template**

    :template:`switchdeck/place_detail.html`
    """

    model = Place

    def get_context_data(self, **kwargs):
        """Insert related context data.

        Insert `Place `object and lists of related profiles and lots.
        """
        context = super().get_context_data(**kwargs)
        gl_query = Lot.objects.filter(profile__place=self.object)\
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