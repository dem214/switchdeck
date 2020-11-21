"""
Django settings for switchdeck project.

Generated by 'django-admin startproject' using Django 2.2.4.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os
import sys
import pathlib

from django.core.exceptions import ImproperlyConfigured

import django_heroku
import dj_database_url

def get_secret(setting):
    """Get the secret variable from env or raise the exception."""
    try:
        return os.environ[setting]
    except KeyError:
        error_msg = f'Set the {setting} environment variable'
        raise ImproperlyConfigured(error_msg)

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = pathlib.Path(__file__).parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get(
    'SECRET_KEY', '!c75dli6my&&8sp-(qkgk8b(#5n4vqrvfrxhecbq%912+k1u63')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['*']


# Application definition


DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.admindocs',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',      # Data and time humanization
    'django.contrib.sitemaps',      # Framework for '/sitemap.xml'
    'django.contrib.sites',         # site for flatpages
    'django.contrib.flatpages',     # Flatpages like 'about', 'copyright' etc
]
THIRD_PARTY_APPS = [
    'crispy_forms',                 # Template forms rendering bootstrap-like
    'rest_framework',               # Framework for REST API
]
LOCAL_APPS = [
    'switchdeck.apps.account.apps.AccountConfig',
    'switchdeck.apps.switchdeck.apps.SwitchdeckConfig',
    'switchdeck.apps.place.apps.PlaceConfig',
]
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.admindocs.middleware.XViewMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'django.contrib.sites.middleware.CurrentSiteMiddleware'
]

ROOT_URLCONF = 'switchdeck.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'switchdeck' / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'switchdeck.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases


DATABASES = {
    # 'default': dj_database_url.config(
    #     default='sqlite:///' + os.path.join(BASE_DIR, 'db.sqlite3'),
    #     conn_max_age=600)
    'default': {
        'NAME': 'postgres',
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'HOST': get_secret('POSTGRES_HOST'),
        'USER': get_secret('POSTGRES_USER'),
        'PASSWORD': get_secret('POSTGRES_PASSWORD'),
        'PORT': get_secret('POSTGRES_PORT'),
        'CONN_MAX_AGE': 600,
    }
}

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.'
        'UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.'
        'MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.'
        'CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.'
        'NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'ru-ru'

TIME_ZONE = 'Europe/Minsk'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'static'
STATICFILES_DIRS = [
    BASE_DIR / 'site_static',
]

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


LOGOUT_REDIRECT_URL = 'index'
AUTH_USER_MODEL = 'account.User'

# Email wirting to file
EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = BASE_DIR / 'emails'

# crispy bootstrap forms
CRISPY_TEMPLATE_PACK = 'bootstrap4'

# path for localization files
LOCALE_PATHS = [BASE_DIR / 'locale', ]

COMMENTS_PER_PAGE = 10

# Activate django-heroku
# deactivating logging and datavases because it make troubles with local
# development process
# django_heroku.settings(locals(), logging=not DEBUG, databases=not DEBUG)

# settings for REST service
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS':
        'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10
}

# Site identification for flat pages processing to store multiple sites in
# one DB

SITE_ID = 1

# Set the externals
# `libs` for required python modules
# `apps` for additional Django apps

EXTERNAL_BASE = BASE_DIR / 'externals'
EXTERNAL_LIBS_PATH = EXTERNAL_BASE / 'libs'
EXTERNAL_APPS_PATH = EXTERNAL_BASE / 'apps'

sys.path = ['', EXTERNAL_LIBS_PATH, EXTERNAL_APPS_PATH] + sys.path
