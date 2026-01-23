from rest_framework import viewsets, status, pagination
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from apps.sync.models import SyncLog
from apps.sync.serializers import SyncLogSerializer
from .models import Feed
from .serializers import FeedSerializer, FeedCreateSerializer
from .tasks import fetch_feed_task


class FeedViewSet(viewsets.ModelViewSet):
    queryset = Feed.objects.all()
    serializer_class = FeedSerializer

    def get_serializer_class(self):
        if self.action == 'create':
            return FeedCreateSerializer
        return FeedSerializer

    @action(detail=True, methods=['post'])
    def sync(self, request, pk=None):
        feed = get_object_or_404(Feed, pk=pk)

        sync_log = SyncLog.objects.create(
            feed=feed,
            status=SyncLog.Status.PENDING
        )

        task = fetch_feed_task.delay(feed.id, sync_log_id=sync_log.id)

        sync_log.task_id = task.id
        sync_log.save(update_fields=['task_id'])

        return Response({
            'sync_log_id': sync_log.id,
            'task_id': task.id,
            'status': 'queued',
            'message': f'Sync started for feed: {feed.url}'
        }, status=status.HTTP_202_ACCEPTED)

    @action(detail=True, methods=['get'])
    def sync_logs(self, request, pk=None):
        feed = get_object_or_404(Feed, pk=pk)
        logs = SyncLog.objects.filter(feed=feed).select_related('feed')

        paginator = pagination.PageNumberPagination()
        paginator.page_size = 20
        page = paginator.paginate_queryset(logs, request)
        serializer = SyncLogSerializer(page, many=True)

        return paginator.get_paginated_response(serializer.data)
