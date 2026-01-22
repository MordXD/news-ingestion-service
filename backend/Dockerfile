FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    perl \
    libxml-parser-perl \
    libwww-perl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml uv.lock ./

COPY backend/ ./backend/

COPY legacy/ ./legacy/

RUN uv sync --frozen --no-dev

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=config.settings.base
ENV PATH="/app/.venv/bin:$PATH"

WORKDIR /app/backend

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "config.wsgi:application"]