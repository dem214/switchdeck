from django.urls import path

from .views import PlaceView, PlacesListView

urlpatterns = [
    # Place page
    path('<slug:slug>/',
         PlaceView.as_view(),
         name='place_view'),
    # Page with list of all pages.
    path('',
         PlacesListView.as_view(),
         name='place_list'),
]