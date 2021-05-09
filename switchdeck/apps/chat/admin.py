from django.contrib import admin

from .models import Dialog, Message

@admin.register(Dialog)
class DialogAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'participant1', 'participant2')
    # readonly_fields = ('participant1', 'participant2')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('text', 'sender', 'datetime')
    # readonly_fields = ('dialog', 'sender')
    list_filter=('sender', )
    date_hierarchy = 'datetime'
