from django.contrib import admin

from .models import Catalog

@admin.register(Catalog)
class CatalogAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('name', 'url')
    search_fields = ('name',)
