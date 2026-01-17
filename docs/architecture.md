# Архитектура News Ingestion Service

общая идея

постепенно переносим legacy Perl парсер
на Python/Django

сервис:
сохраняет новости в PostgreSQL
и отдаёт через REST API

---

## Legacy (Perl)

старый монолит

полный цикл:
parser.pl → Fetch → Parse → Normalize → JSON

по сути:
забрал → распарсил → привёл к норме → отдал

модули:
Feed::App — точка входа
Feed::Fetcher — HTTP
Feed::Parser — выбор RSS/Atom
Feed::Parser::RSS — RSS
Feed::Parser::Atom — Atom
Feed::Normalizer — нормализация
Feed::JSONWriter — JSON
Feed::Util — утилиты

---

## Django backend

2 основных приложения:

feeds — управление фидами
articles — статьи + API

миграция идёт по этапам:

phase 1
через subprocess дёргаем Perl

phase 2
гибрид через feature flag

phase 3
полностью Python

ключевые сервисы:

legacy_parser.py — вызывает Perl
python_parser.py — новый парсер
feed_ingestion.py — вся логика
normalizers.py — нормализация

---

## Инфраструктура

nginx → django (gunicorn) → postgres

плюс:

celery — воркеры
redis — брокер

и отдельно:
legacy parser (parser.pl)

---

## Поток данных

инжест:

celery beat
→ таска
→ ingest

дальше:

phase 1 — Perl
phase 2 — выбор через флаг
phase 3 — Python

→ потом всё в БД

API:

GET /api/articles/
→ Django
→ postgres
→ ответ

---

## Формат данных

на выходе всё приводим к одному виду

type — rss или atom

feed:
title, link, description

items:
id, title, link
summary, content
published

---

## Этапы миграции

1 — Django просто вызывает Perl
2 — можно переключать парсер
3 — полностью Python

смысл:
чтобы поведение совпадало

---

## Безопасность

SQL injection — ORM
XSS — сериалайзеры
CSRF — стандарт DRF
инпут — валидируем (особенно URL)
