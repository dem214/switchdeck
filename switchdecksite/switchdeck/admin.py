from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils import timezone

from .models import Game, GameList, Comment, Profile, Place, User


class ProfileInline(admin.StackedInline):
    model=Profile
    can_delete=False

#admin.site.unregister(User)
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    fields = ['author', 'game_instance', 'text', 'timestamp']
    readonly_fields = ['author', 'game_instance']
    date_hierarchy = 'timestamp'
    list_display = ('author', 'text', 'timestamp', 'game_instance')
    list_display_links = ('text',)
    list_filter = ('author',)
    ordering = ('-timestamp', 'author', 'game_instance')
    search_fields = ('author__user__username', 'text')


def update_up_time(modeladmin, request, queryset):
    for gl in queryset:
        gl.update_up_time()
update_up_time.short_description = "Update all up_time to now"

@admin.register(GameList)
class GamelistAdmin(admin.ModelAdmin):
    readonly_fields = ['profile',]
    exclude = ['change_to']
    date_hierarchy = 'public_date'
    list_display = ['profile', 'prop', 'game', 'public_date', 'up_time',
        'active']
    ordering = ['active', '-public_date', '-up_time', 'profile', 'game']
    list_filter = ['active', 'profile', 'game']
    actions = [update_up_time]
    radio_fields = {"prop": admin.HORIZONTAL}

@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ['pk', 'name']
    ordering = ['pk']
    list_display_links = list_display
    search_fields = ['name']

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ['name']
    ordering = ['name']
    search_fields = ['name']
