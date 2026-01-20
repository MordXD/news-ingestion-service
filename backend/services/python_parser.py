import logging
from dataclasses import dataclass, field
from typing import Optional

import requests
import feedparser

from .normalizers import normalize_feed, normalize_item

logger = logging.getLogger(__name__)


class PythonParserError(Exception):
    pass


@dataclass
class ParsedFeed:
    type: str
    feed: dict
    items: list[dict] = field(default_factory=list)


class PythonParser:

    def __init__(self, timeout: int = 30, user_agent: str = 'NewsIngestion/1.0'):
        self.timeout = timeout
        self.user_agent = user_agent
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': user_agent})

    def parse(self, url: str) -> dict:
        xml_content, _ = self._fetch(url)
        parsed = feedparser.parse(xml_content)

        if parsed.bozo and hasattr(parsed, 'bozo_exception'):
            logger.warning(f"Feed parse warning for {url}: {parsed.bozo_exception}")

        result = {
            'type': self._detect_type(parsed),
            'feed': normalize_feed(parsed.feed),
            'items': [normalize_item(entry) for entry in parsed.entries]
        }

        logger.info(f"Python parser: {len(result['items'])} items from {url}")
        return result

    def _fetch(self, url: str) -> tuple[str, str]:
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.text, response.url
        except requests.Timeout as exc:
            raise PythonParserError(f"Request timeout after {self.timeout}s") from exc
        except requests.RequestException as exc:
            raise PythonParserError(f"HTTP error: {exc}") from exc

    def _detect_type(self, parsed) -> str:
        version = parsed.get('version', '')
        return 'atom' if 'atom' in version.lower() else 'rss'
