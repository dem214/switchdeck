from django.urls import path, re_path
from django.views.generic.base import TemplateView

from .views import (
    UserProfileView, profile_redirect, SignUpView, activate, ProfileListView, UpdateProfileView
)

app_name = 'account'

urlpatterns = [
    path('profiles/<str:username>/', UserProfileView.as_view(), name='profile_detail'),
#     path('/', profile_redirect),
    path('profiles/', ProfileListView.as_view(), name='profile_list'),
    path('update/',
         UpdateProfileView.as_view(),
         name='update'),
    path('signup/', SignUpView.as_view(),
         name='signup'),
    path('need-confirmation/',
         TemplateView.as_view(
            template_name='account/need_confirm_email.html'
         ),
         name='need_confirmation'),
    re_path(r'^accounts/activate/(?P<uid>[0-9A-Za-z_\-]+)/'
            r'(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
            activate, name='activate'),
]