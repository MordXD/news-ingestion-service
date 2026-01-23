from rest_framework import serializers
from .models import SyncLog


class SyncLogSerializer(serializers.ModelSerializer):
    feed_title = serializers.CharField(source='feed.title', read_only=True)
    duration_seconds = serializers.FloatField(read_only=True)

    class Meta:
        model = SyncLog
        fields = [
            'id', 'feed_id', 'feed_title', 'status',
            'started_at', 'finished_at', 'duration_seconds',
            'items_found', 'items_created', 'items_updated',
            'error_message', 'task_id'
        ]
        read_only_fields = fields