import logging
from celery import shared_task
from django.db import transaction
from django.utils import timezone

from apps.sync.models import SyncLog
from .models import Feed
from services.feed_ingestion import FeedIngestionService

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def fetch_feed_task(self, feed_id: int, sync_log_id: int | None = None) -> dict:
    """Celery таска для загрузки фида с отслеживанием через SyncLog"""
    try:
        feed = Feed.objects.get(pk=feed_id)
    except Feed.DoesNotExist:
        logger.error(f"Feed {feed_id} not found")
        return {'status': 'error', 'error': 'Feed not found'}

    if sync_log_id:
        try:
            sync_log = SyncLog.objects.get(pk=sync_log_id)
        except SyncLog.DoesNotExist:
            sync_log = SyncLog.objects.create(
                feed=feed,
                task_id=self.request.id,
                status=SyncLog.Status.PENDING
            )
    else:
        sync_log = SyncLog.objects.create(
            feed=feed,
            task_id=self.request.id,
            status=SyncLog.Status.PENDING
        )

    service = FeedIngestionService(sync_log=sync_log)

    try:
        result = service.ingest(feed)

        with transaction.atomic():
            feed.status = Feed.Status.ACTIVE
            feed.last_error = ''
            feed.save(update_fields=['status', 'last_error'])

            sync_log.status = SyncLog.Status.SUCCESS
            sync_log.finished_at = timezone.now()
            sync_log.items_found = result.get('items_found', 0)
            sync_log.items_created = result.get('items_created', 0)
            sync_log.items_updated = result.get('items_updated', 0)
            sync_log.save()

        return {
            'status': 'success',
            'feed_id': feed_id,
            'sync_log_id': sync_log.id,
            'articles_count': result.get('items_created', 0) + result.get('items_updated', 0)
        }

    except Exception as exc:
        logger.exception(f"Failed to fetch feed {feed_id}")

        sync_log.status = SyncLog.Status.FAILED
        sync_log.finished_at = timezone.now()
        sync_log.error_message = str(exc)[:2000]
        sync_log.save()

        feed.status = Feed.Status.ERROR
        feed.last_error = str(exc)
        feed.save(update_fields=['status', 'last_error'])

        raise self.retry(exc=exc, countdown=60 * (self.request.retries + 1))
