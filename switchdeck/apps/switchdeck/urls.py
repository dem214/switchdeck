"""List of all registred urls."""
from django.urls import path, include, re_path
from django.views.generic.base import TemplateView

from . import views


urlpatterns = [
    # Index page.
    path('', views.index, name='index'),
    # Page with game info.
    
    # Lot page.
    path('lot/<int:glid>/', views.lot_view, name='lot_item'),
    # Page to add lot to keep list.
    path('add-game/keep/', views.add_game_reduced, {'prop': 'k'},
         name='add_game_keep'),
    # Page to add lot to wish list.
    path('add-game/wish/', views.add_game_reduced, {'prop': 'w'},
         name='add_game_wish'),
    # Page to add lot to generic list.
    path('add-game/', views.add_game, name='add_game'),
    # Setting existig lot to another prop
    path('set-game/<int:glid>/', include([
        path('to-sell/', views.set_game, {'set_prop': 's'},
             name="set_game_to_sell"),
        path('to-buy/', views.set_game, {'set_prop': 'b'},
             name="set_game_to_buy"),
        path('to-keep/', views.set_game, {'set_prop': 'k'},
             name="set_game_to_keep"),
        path('to-wish/', views.set_game, {'set_prop': 'w'},
             name="set_game_to_wish")
    ])),
    # URL to delete lot
    path('delete-game/<int:glid>/', views.delete_game, name='delete_game'),
    # Page with profile info.
    
    path('comments/<int:cid>/delete/', views.delete_comment,
         name='delete_comment'),
    # URL to change some info of lot.
    path('lot/<int:glid>/change/', include([
        path('description/', views.change_description,
             name='change_description'),
        path('price/', views.change_price, name='change_price'),
        path('activate/', views.change_activation, {'activate': True},
             name='change_activate'),
        path('deactivate/', views.change_activation, {'activate': False},
             name='change_deactivate'),
        path('change-to/', views.UpdateChangeToView.as_view(),
             name='lot_change_to')
    ])),
    # Lots search page/
    path('search/', views.search, name='search'),
]
