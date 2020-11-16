"""Administration method and classes for `switchdeck` app."""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Game, Lot, Comment, Profile, Place, User


class ProfileInline(admin.StackedInline):
    """Create profile inlines in user page."""

    model = Profile
    can_delete = False

# admin.site.unregister(User)
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """`User` admin pages with profile inlines."""

    inlines = (ProfileInline,)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """`Comment` class admin pages."""

    fields = ['author', 'lot', 'text', 'timestamp']
    readonly_fields = ['author', 'lot']
    date_hierarchy = 'timestamp'
    list_display = ('author', 'text', 'timestamp', 'lot')
    list_display_links = ('text',)
    list_filter = ('author',)
    ordering = ('-timestamp', 'author', 'lot')
    search_fields = ('author__user__username', 'text')


def update_up_time(modeladmin, request, queryset):
    """
    Add method for `CommentAdmin`.

    Add additional button to update uptime of comment.
    """
    for gl in queryset:
        gl.update_up_time()


update_up_time.short_description = "Update all up_time to now"


@admin.register(Lot)
class LotAdmin(admin.ModelAdmin):
    """`Lot` class admin pages."""

    # readonly_fields = ['profile']
    # exclude = ['change_to']
    list_display_links = ['profile', 'prop', 'game']
    date_hierarchy = 'public_date'
    list_display = ['profile', 'prop', 'game', 'public_date', 'up_time',
                    'active']
    ordering = ['active', '-public_date', '-up_time', 'profile', 'game']
    list_filter = ['active', 'profile', 'game']
    actions = [update_up_time]
    radio_fields = {"prop": admin.HORIZONTAL}


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    """`Place` class admin pages."""

    list_display = ['popularity', 'name']
    list_display_links = ['name']
    search_fields = ['name']
    list_editable = ['popularity']


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    """`Game` class admin pages."""

    list_display = ['name']
    ordering = ['name']
    search_fields = ['name']
