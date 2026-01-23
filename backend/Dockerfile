FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    perl \
    libxml-parser-perl \
    libwww-perl \
    ca-certificates \
    && update-ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml uv.lock ./

# Настройка pip для использования зеркала
RUN pip config set global.index-url http://mirrors.aliyun.com/pypi/simple/ && \
    pip config set global.trusted-host mirrors.aliyun.com && \
    pip install --no-cache-dir --upgrade pip setuptools wheel

# Установка зависимостей через uv с правильными параметрами
# uv не поддерживает timeout/retries, поэтому используем переменные окружения
ENV UV_HTTP_TIMEOUT=180
RUN uv sync --frozen --no-dev \
    --index-url http://mirrors.aliyun.com/pypi/simple/

COPY backend/ ./backend/
COPY legacy/ ./legacy/

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=config.settings.base
ENV PATH="/app/.venv/bin:$PATH"

WORKDIR /app/backend

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "config.wsgi:application"]