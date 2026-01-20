from rest_framework import viewsets, pagination
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend

from .models import Article
from .serializers import ArticleSerializer


class ArticlePagination(pagination.PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 200


class ArticleViewSet(viewsets.ReadOnlyModelViewSet):
    """Articles API with filtering and pagination."""

    queryset = Article.objects.select_related('feed')
    serializer_class = ArticleSerializer
    pagination_class = ArticlePagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['feed']
    search_fields = ['title', 'summary', 'content']

    def get_queryset(self):
        queryset = super().get_queryset()

        published_after = self.request.query_params.get('published_after')
        published_before = self.request.query_params.get('published_before')

        if published_after:
            queryset = queryset.filter(published_at__gte=published_after)
        if published_before:
            queryset = queryset.filter(published_at__lte=published_before)

        feed_id = self.request.query_params.get('feed_id')
        if feed_id:
            queryset = queryset.filter(feed_id=feed_id)

        return queryset
