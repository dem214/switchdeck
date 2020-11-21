from django.urls import path

from .views import PlaceView, PlacesListView

app_name = 'place'

urlpatterns = [
    # Place page
    path('<slug:slug>/',
         PlaceView.as_view(),
         name='view'),
    # Page with list of all pages.
    path('',
         PlacesListView.as_view(),
         name='list'),
]