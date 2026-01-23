from django.contrib import admin
from .models import Feed


@admin.register(Feed)
class FeedAdmin(admin.ModelAdmin):
    list_display = ['url', 'title', 'status', 'last_fetched_at', 'fetch_interval_minutes']
    list_filter = ['status', 'created_at']
    search_fields = ['url', 'title']
    readonly_fields = ['last_fetched_at', 'created_at', 'updated_at']