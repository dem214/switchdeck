from django.contrib import admin
from django.utils.translation import gettext as _

from .models import Catalog, Link, ParseResult
from switchdeck.apps.game.models import Game


class LinkInline(admin.TabularInline):
    model = Link
    show_change_link = True

    def get_max_num(self, request, obj=None, **kwargs):
        max_num = super().get_max_num(request, obj, **kwargs)
        if obj and obj._meta.model == Catalog:
            max_num = Game.objects.all().count()
        elif obj and obj._meta.model == Game:
            max_num = Catalog.objects.all().count()



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
    
    def parse_queryset(self, request, queryset):
        for link in queryset:
            link.parse()
        self.message_user(request, message='parsed')
    parse_queryset.short_description = _("Do parsing of selected links.")

    actions = [parse_queryset, ]


@admin.register(ParseResult)
class ParseResultAdmin(admin.ModelAdmin):
    list_display = ('time', 'get_catalog', 'get_game', 'successful')
    list_filter = ('link__catalog', 'link__game', 'successful')
    date_hierarchy = 'time'
    readonly_fields = ('link', 'page_file', 'exception')

    def get_catalog(self, instance) -> str:
        return instance.link.catalog.name
    get_catalog.short_description = _('Catalog')

    def get_game(self, instance) -> str:
        return instance.link.game.name
    get_game.short_description = _('Game')