from django.contrib import admin

from .models import PageView


@admin.register(PageView)
class PageViewAdmin(admin.ModelAdmin):
    """Raw log of page views (read-only). The summary lives on the dashboard."""

    list_display = ("created_at", "path", "source", "device")
    list_filter = ("day", "device", "source")
    search_fields = ("path", "source")
    date_hierarchy = "created_at"
    list_per_page = 100

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
