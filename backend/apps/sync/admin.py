from django.contrib import admin
from .models import SyncLog


@admin.register(SyncLog)
class SyncLogAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'feed', 'status', 'started_at',
        'duration_seconds', 'items_created', 'items_updated'
    ]
    list_filter = ['status', 'started_at', 'feed']
    search_fields = ['feed__url', 'error_message', 'task_id']
    readonly_fields = [
        'started_at', 'finished_at', 'task_id',
        'duration_seconds', 'items_found', 'items_created', 'items_updated'
    ]
    date_hierarchy = 'started_at'