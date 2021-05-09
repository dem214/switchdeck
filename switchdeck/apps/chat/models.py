import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

from .managers import DialogManager
from .constants import DIALOG_DB_TABLE_NAME, MESSAGE_DB_TABLE_NAME

class Dialog(models.Model):
    uuid = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text=_('Unique identifier')
    )
    participant1 = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='+',
        null=False, blank=False,
        verbose_name=_('First participant')
    )
    participant2 = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='+',
        null=False, blank=False,
        verbose_name=_('Second participant')
    )

    objects = DialogManager()

    class Meta:
        verbose_name = _('Dialog')
        verbose_name_plural = _('Dialogs')
        db_table=DIALOG_DB_TABLE_NAME
        unique_together=('participant1', 'participant2')

    


class Message(models.Model):
    uuid = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text=_('Unique identifier')
    )
    dialog = models.ForeignKey(
        Dialog,
        on_delete=models.CASCADE,
        related_name='messages',
        related_query_name='message',
        verbose_name=_('Dialog')
    )
    sender = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_('Sender'),
    )
    text = models.CharField(
        verbose_name=_('Text'),
        null=False, blank=False,
        max_length=200,
    )
    datetime = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Date and time')
    )

    class Meta:
        verbose_name = _('Message')
        verbose_name_plural = _('Messages')
        db_table = MESSAGE_DB_TABLE_NAME
        ordering = ('-datetime', )
        get_latest_by = ('datetime')

