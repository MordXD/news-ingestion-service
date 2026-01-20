from rest_framework import serializers
from .models import Article


class ArticleSerializer(serializers.ModelSerializer):
    """Serializer с пагинацией и полным набором полей."""

    feed_title = serializers.CharField(source='feed.title', read_only=True)

    class Meta:
        model = Article
        fields = [
            'id', 'external_id', 'feed_id', 'feed_title',
            'title', 'link', 'summary', 'content',
            'published_at', 'fetched_at', 'updated_at'
        ]
        read_only_fields = fields