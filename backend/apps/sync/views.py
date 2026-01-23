from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.utils import timezone

from apps.feeds.models import Feed
from apps.feeds.tasks import fetch_feed_task
from .models import SyncLog
from .serializers import SyncLogSerializer


class SyncLogViewSet(viewsets.ReadOnlyModelViewSet):
    """API для просмотра логов синхронизации."""

    queryset = SyncLog.objects.select_related('feed')
    serializer_class = SyncLogSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['feed', 'status']

    def get_queryset(self):
        queryset = super().get_queryset()

        from_date = self.request.query_params.get('from_date')
        to_date = self.request.query_params.get('to_date')

        if from_date:
            queryset = queryset.filter(started_at__gte=from_date)
        if to_date:
            queryset = queryset.filter(started_at__lte=to_date)

        return queryset

    @action(detail=False, methods=['post'], url_path='trigger/(?P<feed_id>[^/.]+)')
    def trigger(self, request, feed_id=None):
        """Ручной запуск синхронизации фида."""
        feed = get_object_or_404(Feed, pk=feed_id)

        log = SyncLog.objects.create(
            feed=feed,
            status=SyncLog.Status.PENDING
        )

        task = fetch_feed_task.delay(feed.id, sync_log_id=log.id)

        log.task_id = task.id
        log.save(update_fields=['task_id'])

        return Response({
            'sync_log_id': log.id,
            'task_id': task.id,
            'status': 'queued'
        }, status=status.HTTP_202_ACCEPTED)