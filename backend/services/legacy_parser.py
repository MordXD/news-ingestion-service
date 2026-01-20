import json
import logging
import subprocess
from pathlib import Path
from typing import Optional
from dataclasses import dataclass

from django.conf import settings

logger = logging.getLogger(__name__)


@dataclass
class ParseResult:
    type: str
    feed: dict
    items: list


class LegacyParserError(Exception):
    pass


class LegacyParser:
    def __init__(self, parser_path: Optional[Path] = None, timeout: int = 60):
        self.parser_path = parser_path or settings.LEGACY_PARSER_PATH
        self.timeout = timeout

    def parse(self, url: str) -> dict:
        cmd = ['perl', str(self.parser_path), url]
        logger.debug(f"Calling legacy parser: {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                encoding='utf-8'
            )
        except subprocess.TimeoutExpired as exc:
            logger.error(f"Legacy parser timeout for {url}")
            raise LegacyParserError(f"Parser timeout after {self.timeout}s") from exc
        except FileNotFoundError as exc:
            logger.error(f"Perl not found: {exc}")
            raise LegacyParserError("Perl interpreter not found") from exc

        if result.returncode != 0:
            stderr = result.stderr.strip()
            logger.error(f"Legacy parser error: {stderr}")
            raise LegacyParserError(f"Parser failed: {stderr}")

        try:
            data = json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            logger.error(f"Invalid JSON from parser: {result.stdout[:200]}")
            raise LegacyParserError("Parser returned invalid JSON") from exc

        if 'feed' not in data or 'items' not in data:
            raise LegacyParserError("Parser output missing required fields")

        logger.info(f"Legacy parser: {len(data.get('items', []))} items from {url}")
        return data

    def is_available(self) -> bool:
        return self.parser_path.exists() and self._check_perl()

    def _check_perl(self) -> bool:
        try:
            subprocess.run(['perl', '-v'], capture_output=True, timeout=5)
            return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
