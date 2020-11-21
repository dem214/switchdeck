from ._base import *

ALLOWED_HOSTS = ['127.0.0.1', '0.0.0.0', 'localhost']

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

DEBUG = True