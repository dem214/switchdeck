from django.contrib import admin

from .models import Game

# Register your models here.
@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    """`Game` class admin pages."""

    list_display = ['name']
    ordering = ['name']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}