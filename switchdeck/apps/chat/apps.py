from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ChatConfig(AppConfig):
    name = 'switchdeck.apps.chat'
    verbose_name = _('Chat')
    verbose_name_plural = _('Chats')