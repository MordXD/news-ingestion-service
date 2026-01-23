from django.contrib import admin
from .models import Article


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'feed', 'published_at', 'fetched_at']
    list_filter = ['feed', 'published_at', 'fetched_at']
    search_fields = ['title', 'summary', 'content']
    readonly_fields = ['fetched_at']