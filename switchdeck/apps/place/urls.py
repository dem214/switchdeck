from django.urls import path

from .views import PlaceView, PlacesListView

app_name = 'place'

urlpatterns = [
    path('<slug:slug>/', PlaceView.as_view(), name='place_detail'),
    path('', PlacesListView.as_view(), name='place_list'),
]