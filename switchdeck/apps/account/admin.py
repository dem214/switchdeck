from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User, Profile

class ProfileInline(admin.StackedInline):
    """Create profile inlines in user page."""

    model = Profile
    can_delete = False

# admin.site.unregister(User)
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """`User` admin pages with profile inlines."""

    inlines = (ProfileInline,)

