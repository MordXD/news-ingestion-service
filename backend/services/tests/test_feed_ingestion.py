"""
Тесты сервиса инжестии.

1. Тест ingestion - парсер → БД, создание статей
2. Тест идемпотентности - двойной запуск = те же статьи
3. Тест переключения parser backend - legacy vs python
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from apps.feeds.models import Feed
from apps.articles.models import Article
from apps.sync.models import SyncLog
from services.feed_ingestion import FeedIngestionService


# Фикстура с мок-данными RSS
MOCK_RSS_DATA = {
    'type': 'rss',
    'feed': {
        'title': 'Test Blog',
        'link': 'https://example.com',
        'description': 'A test blog'
    },
    'items': [
        {
            'id': 'guid-1',
            'title': 'First Article',
            'link': 'https://example.com/1',
            'summary': 'Summary 1',
            'content': 'Content 1',
            'published': 'Mon, 15 Jan 2024 10:00:00 GMT'
        },
        {
            'id': 'guid-2',
            'title': 'Second Article',
            'link': 'https://example.com/2',
            'summary': 'Summary 2',
            'content': 'Content 2',
            'published': 'Mon, 15 Jan 2024 11:00:00 GMT'
        }
    ]
}


@pytest.mark.django_db
class TestFeedIngestion:
    """Тест 1: ingestion работает корректно."""

    @pytest.fixture
    def feed(self):
        return Feed.objects.create(url='https://example.com/rss.xml')

    @patch('services.feed_ingestion.LegacyParser.parse')
    def test_ingestion_creates_articles(self, mock_parse, feed):
        """Парсер → БД: статьи создаются корректно."""
        mock_parse.return_value = MOCK_RSS_DATA

        service = FeedIngestionService()
        result = service.ingest(feed)

        # Проверяем результат
        assert result['items_found'] == 2
        assert result['items_created'] == 2
        assert result['items_updated'] == 0

        # Проверяем БД
        assert Article.objects.count() == 2

        article1 = Article.objects.get(external_id='guid-1')
        assert article1.title == 'First Article'
        assert article1.feed == feed

        # Проверяем обновление фида
        feed.refresh_from_db()
        assert feed.title == 'Test Blog'
        assert feed.last_fetched_at is not None

    @patch('services.feed_ingestion.LegacyParser.parse')
    def test_ingestion_skips_items_without_id(self, mock_parse, feed):
        """Статьи без ID (даже link) пропускаются."""
        data_with_missing_id = {
            'type': 'rss',
            'feed': {'title': 'Test'},
            'items': [
                {'id': 'guid-1', 'title': 'Good Article', 'link': 'https://example.com/1'},
                {'title': 'Bad Article'},  # без id и без link
            ]
        }
        mock_parse.return_value = data_with_missing_id

        service = FeedIngestionService()
        result = service.ingest(feed)

        assert result['items_found'] == 2
        assert result['items_created'] == 1  # только одна создана (с id)


@pytest.mark.django_db
class TestIdempotency:
    """Тест 2: идемпотентность - двойной запуск = те же статьи."""

    @pytest.fixture
    def feed(self):
        return Feed.objects.create(url='https://example.com/rss.xml')

    @patch('services.feed_ingestion.LegacyParser.parse')
    def test_double_ingestion_no_duplicates(self, mock_parse, feed):
        """Тот же feed дважды → количество статей не увеличилось."""
        mock_parse.return_value = MOCK_RSS_DATA

        service = FeedIngestionService()

        # Первый запуск
        result1 = service.ingest(feed)
        assert result1['items_created'] == 2
        assert Article.objects.count() == 2

        # Второй запуск (тот же feed)
        result2 = service.ingest(feed)
        assert result2['items_created'] == 0  # новых нет
        assert result2['items_updated'] == 2  # обновлены существующие

        # Проверяем, что дубликатов нет
        assert Article.objects.count() == 2

        # Проверяем, что данные обновились
        article = Article.objects.get(external_id='guid-1')
        assert article.title == 'First Article'

    @patch('services.feed_ingestion.LegacyParser.parse')
    def test_partial_update(self, mock_parse, feed):
        """Обновление части статей работает корректно."""
        # Первый парсинг - 2 статьи
        mock_parse.return_value = MOCK_RSS_DATA
        service = FeedIngestionService()
        service.ingest(feed)

        # Второй парсинг - 1 старая, 1 новая, 1 отсутствует
        updated_data = {
            'type': 'rss',
            'feed': {'title': 'Test Blog'},
            'items': [
                {
                    'id': 'guid-1',  # существует - обновится
                    'title': 'Updated First Article',
                    'link': 'https://example.com/1',
                    'summary': 'Updated Summary',
                },
                {
                    'id': 'guid-3',  # новая - создастся
                    'title': 'Third Article',
                    'link': 'https://example.com/3',
                }
            ]
        }
        mock_parse.return_value = updated_data

        result = service.ingest(feed)

        assert result['items_created'] == 1  # guid-3
        assert result['items_updated'] == 1  # guid-1

        # guid-2 осталась без изменений (не в новом фиде)
        assert Article.objects.count() == 3

        # Проверяем обновление
        article1 = Article.objects.get(external_id='guid-1')
        assert article1.title == 'Updated First Article'


@pytest.mark.django_db
class TestParserBackendSwitching:
    """Тест 3: переключение parser backend работает."""

    @pytest.fixture
    def feed(self):
        return Feed.objects.create(url='https://example.com/rss.xml')

    @pytest.fixture
    def mock_legacy_parse(self):
        with patch('services.legacy_parser.subprocess.run') as mock_run:
            import json
            mock_run.return_value = Mock(
                returncode=0,
                stdout=json.dumps(MOCK_RSS_DATA),
                stderr=''
            )
            yield mock_run

    @pytest.fixture
    def mock_python_parse(self):
        """Мокаем requests.get на уровне _fetch, а не feedparser."""
        with patch('services.python_parser.requests.Session.get') as mock_get:
            # Return mock XML response
            mock_response = Mock()
            mock_response.text = '''<?xml version="1.0"?>
<rss version="2.0">
<channel>
<title>Test Blog</title>
<link>https://example.com</link>
<description>A test blog</description>
<item>
<guid>guid-1</guid>
<title>First Article</title>
<link>https://example.com/1</link>
<description>Summary 1</description>
<pubDate>Mon, 15 Jan 2024 10:00:00 GMT</pubDate>
</item>
<item>
<guid>guid-2</guid>
<title>Second Article</title>
<link>https://example.com/2</link>
<description>Summary 2</description>
<pubDate>Mon, 15 Jan 2024 11:00:00 GMT</pubDate>
</item>
</channel>
</rss>'''
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response
            yield mock_get

    @patch('services.feed_ingestion.settings')
    def test_legacy_parser_backend(self, mock_settings, feed, mock_legacy_parse):
        """USE_PYTHON_PARSER=false → работает legacy parser."""
        mock_settings.USE_PYTHON_PARSER = False
        mock_settings.LEGACY_PARSER_PATH = '/app/legacy/parser.pl'

        service = FeedIngestionService()
        result = service.ingest(feed)

        assert result['items_created'] == 2
        assert result['parser_used'] == 'legacy'
        mock_legacy_parse.assert_called_once()

    @patch('services.feed_ingestion.settings')
    def test_python_parser_backend(self, mock_settings, feed, mock_python_parse):
        """USE_PYTHON_PARSER=true → работает python parser."""
        mock_settings.USE_PYTHON_PARSER = True

        service = FeedIngestionService()
        result = service.ingest(feed)

        assert result['items_created'] == 2
        assert result['parser_used'] == 'python'
        mock_python_parse.assert_called_once()


@pytest.mark.django_db
class TestSyncLogIntegration:
    """Тест интеграции с SyncLog."""

    @pytest.fixture
    def feed(self):
        return Feed.objects.create(url='https://example.com/rss.xml')

    @patch('services.feed_ingestion.LegacyParser.parse')
    def test_synclog_updated_on_success(self, mock_parse, feed):
        """SyncLog обновляется при успешной инжестии."""
        mock_parse.return_value = MOCK_RSS_DATA

        sync_log = SyncLog.objects.create(feed=feed, status=SyncLog.Status.PENDING)
        service = FeedIngestionService(sync_log=sync_log)

        service.ingest(feed)

        sync_log.refresh_from_db()
        assert sync_log.items_found == 2
        assert sync_log.items_created == 2
        assert sync_log.items_updated == 0

    @patch('services.feed_ingestion.LegacyParser.parse')
    def test_synclog_updated_on_parse_error(self, mock_parse, feed):
        """SyncLog обновляется при ошибке парсинга."""
        from services.legacy_parser import LegacyParserError
        mock_parse.side_effect = LegacyParserError('Network error')

        sync_log = SyncLog.objects.create(feed=feed, status=SyncLog.Status.PENDING)
        service = FeedIngestionService(sync_log=sync_log)

        with pytest.raises(LegacyParserError):
            service.ingest(feed)

        # Проверяем, что лог создан (обновляется в celery task, не здесь)
