import pytest
from unittest.mock import patch, MagicMock
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from apps.feeds.models import Feed


@pytest.mark.django_db
class TestFeedViewSet:
    """Тесты API feeds."""

    @pytest.fixture
    def api_client(self):
        return APIClient()

    @pytest.fixture
    def feed(self):
        return Feed.objects.create(
            url='https://example.com/rss.xml',
            title='Test Feed'
        )

    def test_list_feeds(self, api_client, feed):
        """GET /api/feeds/ возвращает список фидов."""
        response = api_client.get('/api/feeds/')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['url'] == feed.url

    def test_create_feed(self, api_client):
        """POST /api/feeds/ создаёт новый фид."""
        data = {
            'url': 'https://example.com/new.xml',
            'fetch_interval_minutes': 30
        }
        response = api_client.post('/api/feeds/', data)

        assert response.status_code == status.HTTP_201_CREATED
        assert Feed.objects.count() == 1
        assert Feed.objects.first().url == 'https://example.com/new.xml'

    @patch('apps.feeds.views.fetch_feed_task')
    def test_sync_feed(self, mock_task, api_client, feed):
        """POST /api/feeds/{id}/sync/ запускает Celery задачу."""
        mock_task.delay.return_value = MagicMock(id='task-123')

        response = api_client.post(f'/api/feeds/{feed.id}/sync/')

        assert response.status_code == status.HTTP_202_ACCEPTED
        assert response.data['task_id'] == 'task-123'
        assert response.data['status'] == 'queued'
        mock_task.delay.assert_called_once()

    def test_sync_logs(self, api_client, feed):
        """GET /api/feeds/{id}/sync-logs/ возвращает логи синхронизации."""
        from apps.sync.models import SyncLog

        SyncLog.objects.create(
            feed=feed,
            status=SyncLog.Status.SUCCESS,
            items_found=10,
            items_created=5
        )

        response = api_client.get(f'/api/feeds/{feed.id}/sync_logs/')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
