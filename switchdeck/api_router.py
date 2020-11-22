"""List and registration of REST api urls."""
from django.urls import include, path
from rest_framework import routers

from switchdeck.apps.lot.api.views import LotViewSet, CommentViewSet
from switchdeck.apps.place.api.views import PlaceViewSet
from switchdeck.apps.account.api.views import ProfileViewSet, UserViewSet
from switchdeck.apps.game.api.views import GameViewSet

router = routers.DefaultRouter()
router.register('places', PlaceViewSet)
router.register('profiles', ProfileViewSet)
router.register('games', GameViewSet)
router.register('lots', LotViewSet)
router.register('users', UserViewSet)
router.register('comments', CommentViewSet)

