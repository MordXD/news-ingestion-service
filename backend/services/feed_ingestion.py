import logging
from typing import Optional
from datetime import datetime, timezone as dt_timezone

from django.conf import settings
from django.db import transaction

from apps.feeds.models import Feed
from apps.articles.models import Article
from apps.sync.models import SyncLog
from .legacy_parser import LegacyParser, LegacyParserError
from .python_parser import PythonParser, PythonParserError

logger = logging.getLogger(__name__)


class FeedIngestionService:
    """Бизнес логика для загрузки фида с идемпотентностью"""

    def __init__(self, sync_log: Optional[SyncLog] = None):
        self._legacy_parser: Optional[LegacyParser] = None
        self._python_parser: Optional[PythonParser] = None
        self.sync_log = sync_log

    @property
    def parser(self):
        """Возвращает активный парсер в зависимости от USE_PYTHON_PARSER"""
        if settings.USE_PYTHON_PARSER:
            if self._python_parser is None:
                self._python_parser = PythonParser()
            return self._python_parser
        else:
            if self._legacy_parser is None:
                self._legacy_parser = LegacyParser()
            return self._legacy_parser

    def ingest(self, feed: Feed) -> dict:
        """Полный цикл загрузки забрать распарсить сохранить"""
        logger.info(f"Ingesting feed {feed.id}: {feed.url}")
        logger.info(f"Parser: {'python' if settings.USE_PYTHON_PARSER else 'legacy'}")

        data = self.parser.parse(feed.url)

        feed_meta = data.get('feed', {})
        feed.title = feed_meta.get('title', feed.title)
        feed.description = feed_meta.get('description', feed.description)
        feed.link = feed_meta.get('link', feed.link)
        feed.last_fetched_at = datetime.now(dt_timezone.utc)

        items = data.get('items', [])
        stats = self._save_articles(feed, items)
        feed.save()

        if self.sync_log:
            self.sync_log.items_found = stats['items_found']
            self.sync_log.items_created = stats['items_created']
            self.sync_log.items_updated = stats['items_updated']
            self.sync_log.save(update_fields=['items_found', 'items_created', 'items_updated'])

        return {
            'feed_id': feed.id,
            'items_found': stats['items_found'],
            'items_created': stats['items_created'],
            'items_updated': stats['items_updated'],
            'parser_used': 'python' if settings.USE_PYTHON_PARSER else 'legacy'
        }

    @transaction.atomic
    def _save_articles(self, feed: Feed, items: list) -> dict:
        """Сохраняет статьи без дублей через (feed, external_id)"""
        created_count = 0
        updated_count = 0

        for item in items:
            external_id = item.get('id') or item.get('guid') or item.get('link')
            if not external_id:
                logger.warning(f"Skipping article without ID: {item.get('title', 'unknown')}")
                continue

            article, created = Article.objects.update_or_create(
                feed=feed,
                external_id=external_id[:500],
                defaults={
                    'title': (item.get('title') or '')[:1000],
                    'link': item.get('link') or '',
                    'summary': item.get('summary') or '',
                    'content': item.get('content') or item.get('description') or '',
                    'published_at': self._parse_date(item.get('published')),
                }
            )

            if created:
                created_count += 1
            else:
                updated_count += 1

        return {
            'items_found': len(items),
            'items_created': created_count,
            'items_updated': updated_count,
        }

    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        if not date_str:
            return None
        from dateutil import parser as date_parser
        try:
            return date_parser.parse(date_str)
        except (ValueError, TypeError):
            return None

    def compare_parsers(self, url: str) -> dict:
        """Сравнивает оба парсера для миграции"""
        legacy = LegacyParser()
        python = PythonParser()

        legacy_result = legacy.parse(url)
        python_result = python.parse(url)

        return {
            'legacy': {
                'type': legacy_result.get('type'),
                'feed_title': legacy_result.get('feed', {}).get('title'),
                'items_count': len(legacy_result.get('items', [])),
            },
            'python': {
                'type': python_result.get('type'),
                'feed_title': python_result.get('feed', {}).get('title'),
                'items_count': len(python_result.get('items', [])),
            },
            'match': self._compare_results(legacy_result, python_result)
        }

    def _compare_results(self, legacy: dict, python: dict) -> bool:
        legacy_items = {i.get('id'): i for i in legacy.get('items', [])}
        python_items = {i.get('id'): i for i in python.get('items', [])}
        return set(legacy_items.keys()) == set(python_items.keys())
