from rest_framework import serializers
from .models import Feed


class FeedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feed
        fields = [
            'id', 'url', 'title', 'description', 'link',
            'status', 'last_fetched_at', 'fetch_interval_minutes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['title', 'description', 'link', 'status', 'last_fetched_at']


class FeedCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feed
        fields = ['url', 'fetch_interval_minutes']


class FetchResponseSerializer(serializers.Serializer):
    task_id = serializers.CharField()
    status = serializers.CharField()