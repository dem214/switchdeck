from django.contrib import admin

from .models import Catalog, Link
from switchdeck.apps.game.models import Game

class LinkInline(admin.TabularInline):
    model = Link
    show_change_link=True
    
    def get_max_num(self, request, obj=None, **kwargs):
        max_num = super().get_max_num(request, obj, **kwargs)
        if obj and obj._meta.model == Catalog:
            max_num = Game.objects.all().count()
        elif obj and obj._meta.model == Game:
            max_num = Catalog.objects.all().count()
        return max_num

@admin.register(Catalog)
class CatalogAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('name', 'url')
    search_fields = ('name',)
    inlines = [LinkInline, ]

@admin.register(Link)
class LinkAdmin(admin.ModelAdmin):
    list_display = ('id', 'game', 'catalog', 'active')
    list_filter = ('active', 'catalog', 'game')
    search_fields = ('name', )


