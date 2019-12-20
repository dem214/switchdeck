"""List and registration of REST api urls."""
from django.urls import include, path
from rest_framework import routers

from . import api_views

router = routers.DefaultRouter()
router.register('places', api_views.PlaceViewSet)
router.register('profiles', api_views.ProfileViewSet)
router.register('games', api_views.GameViewSet)
router.register('lots', api_views.GameListViewSet)
router.register('users', api_views.UserViewSet)
router.register('comments', api_views.CommentViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('api-auth', include('rest_framework.urls',
                             namespace='rest_framework')),
]
