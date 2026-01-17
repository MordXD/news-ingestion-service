# News Ingestion Service

бекенд для обработки RSS/Atom
с миграцией с Perl на Python/Django

---

## stack

Python 3.12 + Django + DRF

PostgreSQL — данные
Redis — брокер

Celery — асинхронные таски

uv — зависимости

---

## структура

```
news_project/
├── legacy/              # старый Perl парсер
├── backend/
│   ├── apps/
│   │   ├── feeds/       # фиды
│   │   ├── articles/    # статьи
│   │   └── sync/        # логи синка
│   ├── services/        # логика + парсеры
│   └── config/          # настройки
├── docs/
├── docker-compose.yml
└── pyproject.toml
```

---

## запуск (локально)

```bash
# зависимости
uv sync --frozen

# инфраструктура
docker-compose up -d db redis

# миграции
cd backend
uv run python manage.py migrate

# сервер
uv run python manage.py runserver
```

или просто всё в docker:

```bash
docker-compose up --build
```

---

## переключение парсера

Perl:

```bash
USE_PYTHON_PARSER=false docker-compose up
```

Python:

```bash
USE_PYTHON_PARSER=true docker-compose up
```

---

## API

health
`GET /api/health/`

фиды
`GET /api/feeds/`
`POST /api/feeds/`

запустить синк
`POST /api/feeds/{id}/sync/`

логи синка
`GET /api/feeds/{id}/sync_logs/`
`GET /api/sync/logs/`

статьи
`GET /api/articles/`

фильтры:
feed_id
search
published_after

---

## тесты

```bash
cd backend
uv run pytest -v
```

покрытие:

модели (feed/article)
pipeline инжеста
идемпотентность (без дублей)
переключение парсеров
