# API

базовый URL
`/api/v1/`

---

## Feeds

список фидов
`GET /api/feeds/`

ответ:
count + список фидов
(id, url, title, статус, когда тянули, интервал)

создать фид
`POST /api/feeds/`

передаёшь:
url + fetch_interval_minutes

триггернуть fetch
`POST /api/feeds/{id}/fetch/`

в ответ:
task_id + статус (queued)

---

## Articles

список статей
`GET /api/articles/`

можно фильтровать:
feed — по id фида
search — поиск по тексту
from_date / to_date — по датам

ответ:
count + список статей
(id, feed_id, title, link, summary, content, даты)

получить одну статью
`GET /api/articles/{id}/`

---

## Admin

health check
`GET /api/health/`

показывает:
статус
база
redis
парсер (python или legacy)

метрики
`GET /metrics/`
