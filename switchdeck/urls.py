"""switchdecksite URL Configuration.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))

"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.contrib.flatpages import views as flatpage_views

from .sitemaps import sitemaps
from .api_router import router
from switchdeck.apps.account import urls as account_url

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('switchdeck.apps.switchdeck.urls')),
    path('api-auth', include('rest_framework.urls',
                             namespace='rest_framework')),
    path('api/v1/', include(router.urls)),
    path('places/', include('switchdeck.apps.place.urls')),
    path('games/', include('switchdeck.apps.game.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/', include(account_url)),
    path('admin/doc/', include('django.contrib.admindocs.urls')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps},
         name="django.contrib.sitemaps.views.sitemap"),
    path('about/', flatpage_views.flatpage, {'url': '/about/'},
         name='about'),
    path('license/', flatpage_views.flatpage, {'url': '/license/'},
         name='license'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
