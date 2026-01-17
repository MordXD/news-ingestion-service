# План миграции: Perl → Python

---

## текущее состояние

Perl уже полностью работает

есть:
parser.pl — CLI
lib/Feed/ — вся логика
на выходе — нормализованный JSON

---

## этап 1 — через subprocess (MVP)

идея:
Django работает
Perl просто как внешний адаптер

что делаем:

legacy_parser.py
обёртка над parser.pl
читаем stdout/stderr
парсим JSON
таймауты + retry

модели:

Feed — источник (url, статус, когда тянули)
Article — статьи (с external_id чтобы не было дублей)

celery таска:

fetch_feed_task
дёргает Perl
сохраняет в БД
обновляет статус

пример:

```python
class LegacyParser:
    def parse(self, url: str) -> dict:
        cmd = ['perl', 'legacy/parser.pl', url]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return json.loads(result.stdout)
```

---

## этап 2 — параллельно Python

идея:
делаем новый парсер
и сравниваем

что делаем:

python_parser.py
requests — fetch
feedparser / xml — парсинг
перенос логики из Feed::Normalizer

feature flag:

если включён — Python
если нет — Perl

плюс метрики:

время
успешность
насколько совпадает результат

готовность:

Python проходит те же тесты
разница < 0.1%

---

## этап 3 — полный переход

идея:
убираем Perl

что делаем:

включаем Python по умолчанию
смотрим прод
удаляем legacy_parser.py
архивируем legacy/

---

## риски

несовпадение парсинга
→ решается тестами

производительность
→ бенчмарки

Perl зависимости
→ docker с обоими окружениями

---

## тесты

unit — каждый парсер отдельно
integration — полный цикл
regression — реальные фиды
contract — сравнение JSON

