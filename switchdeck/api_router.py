"""List and registration of REST api urls."""
from django.urls import include, path
from rest_framework import routers

from switchdeck.apps.switchdeck import api_views
from switchdeck.apps.place.api.views import PlaceViewSet

router = routers.DefaultRouter()
router.register('places', PlaceViewSet)
router.register('profiles', api_views.ProfileViewSet)
router.register('games', api_views.GameViewSet)
router.register('lots', api_views.LotViewSet)
router.register('users', api_views.UserViewSet)
router.register('comments', api_views.CommentViewSet)

