from django.urls import path, include

from .views import (
    GameDetailView, GameListView, GameBuyListView, GameSellListView)


app_name = 'game'

urlpatterns = [
    path('<slug:slug>/', include([
        path('', GameDetailView.as_view(), name='game_detail'),
        # Additional page with lots to sell
        path('sell-list/', GameSellListView.as_view(),
             name='game_sell_list'),
        # Additional list with gamelsists to buy.
        path('buy-list/', GameBuyListView.as_view(),
             name='game_buy_list')
    ])),
    # Page with all games.
    path('', GameListView.as_view(), name='game_list'),
]