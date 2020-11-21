from django.contrib import admin

from .models import Place

# Register your models here.

@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    """`Place` class admin pages."""

    list_display = ['name', 'popularity']
    list_display_links = ['name']
    search_fields = ['name']
    list_editable = ['popularity']
    prepopulated_fields = {'slug': ('name',)}