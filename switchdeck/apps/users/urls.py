from django.urls import path, re_path
from django.views.generic.base import TemplateView

from .views import (
    UserProfileView, profile_redirect, SignUpView, activate, ProfileListView, UpdateProfileView
)

app_name = 'users'

urlpatterns = [
    path('', ProfileListView.as_view(), name='list'),
    path('profile/<str:username>/', UserProfileView.as_view(), name='detail'),
    path('update/',
         UpdateProfileView.as_view(),
         name='update'),
]