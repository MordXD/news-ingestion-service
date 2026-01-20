"""
Нормализация данных фидов

Python версия логики Feed::Normalizer
берёт сырые данные из feedparser
и приводит к нормальному виду

чтобы формат был такой же
как у Perl парсера
"""

import re
from datetime import datetime
from typing import Optional

from dateutil import parser as date_parser


def trim(s: Optional[str]) -> Optional[str]:
    """Удаляет whitespace с концов строки."""
    if s is None:
        return None
    return s.strip() or None


def first_non_empty(*values: Optional[str]) -> Optional[str]:
    """Возвращает первое непустое значение."""
    for v in values:
        trimmed = trim(v)
        if trimmed:
            return trimmed
    return None


def parse_date(date_str: Optional[str]) -> Optional[str]:
    """
    Парсит дату в разных форматах (RFC 2822, ISO 8601).
    Возвращает ISO 8601 строку.
    """
    if not date_str:
        return None
    try:
        dt = date_parser.parse(date_str)
        return dt.isoformat()
    except (ValueError, TypeError):
        return trim(date_str)


def clean_html(html: Optional[str]) -> Optional[str]:
    """Базовая очистка HTML (strip tags)."""
    if not html:
        return None
    # супер простая отчистка
    text = re.sub(r'<[^>]+>', '', html)
    text = re.sub(r'\s+', ' ', text)
    return trim(text)


def normalize_feed(feed_data: dict) -> dict:
    """
    Нормализует метаданные фида.

    Соответствует _normalize_feed в Feed::Normalizer
    """
    return {
        'title': trim(feed_data.get('title')),
        'link': trim(feed_data.get('link')),
        'description': trim(feed_data.get('subtitle') or feed_data.get('description')),
    }


def normalize_item(entry: dict) -> dict:
    """
    Нормализует отдельную статью.

    Соответствует _normalize_item в Feed::Normalizer.
    """

    item_id = first_non_empty(
        entry.get('guid'),
        entry.get('id'),
        entry.get('link')
    )
    content = entry.get('content', [{}])[0].get('value') if entry.get('content') else None
    summary = first_non_empty(
        entry.get('summary'),
        entry.get('description')
    )

    return {
        'id': item_id,
        'title': trim(entry.get('title')),
        'link': trim(entry.get('link')),
        'summary': clean_html(summary),
        'content': clean_html(content),
        'published': parse_date(
            entry.get('published') or entry.get('updated')
        ),
    }