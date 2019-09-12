from django.urls import path, include, re_path
from django.views.generic.base import TemplateView

from . import views
from . import profile_views


urlpatterns = [
    path('', views.index, name='index'),
    path('game/<int:gid>/', include([
        path('', views.game_id, name='game_id'),
        path('sell-list/', views.GameSellListView.as_view(),
            name='game_sell_list'),
        path('buy-list/', views.GameBuyListView.as_view(),
            name='game_buy_list')
    ])),
    path('lot/<int:glid>/', views.gamelist_view, name='gamelist_item'),
    path('add-game/keep/', views.add_game_reduced, {'prop': 'k'},
        name='add_game_keep'),
    path('add-game/wish/', views.add_game_reduced, {'prop': 'w'},
        name='add_game_wish'),
    path('add-game/', views.add_game, name='add_game'),
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
    path('delete-game/<int:glid>/', views.delete_game, name='delete_game'),
    path('accounts/profile/<str:username>/',
        profile_views.UserProfileView.as_view(),
        name='profile'),
    path('accounts/profile/', profile_views.profile_redirect),
    path('accounts/signup/', profile_views.SignUpView.as_view(), name='signup'),
    path('accounts/need-confirmation/',
        TemplateView.as_view(
            template_name='registration/need_confirm_email.html'),
        name='need_confirmation' ),
    re_path(r'^accounts/activate/(?P<uid>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        profile_views.activate, name='activate'),
    path('comments/<int:cid>/delete/', views.delete_comment,
        name='delete_comment'),
    path('place/<str:name>/', views.PlaceView.as_view(), name='place'),
    path('place/', views.PlacesListView.as_view(), name='places'),
    path('accounts/', profile_views.UsersListView.as_view(), name = 'users'),
    path('lot/<int:glid>/change/', include([
        path('description/', views.change_description,
            name='change_description'),
        path('price/', views.change_price, name='change_price'),
        path('activate/', views.change_activation, {'activate': True},
            name='change_activate'),
        path('deactivate/', views.change_activation, {'activate': False},
            name='change_deactivate')
    ])),
    path('accounts/update-profile/',
    profile_views.UpdateProfileView.as_view(),
    name = 'update_profile'),
    path('games/', views.GamesView.as_view(), name='games')
]
