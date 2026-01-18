from django.urls import path
from django.http import JsonResponse
from django.db import connections
from django.core.cache import cache
from django.conf import settings


def health_check(request):
    status = {'status': 'ok'}
    status_code = 200

    try:
        connections['default'].cursor()
        status['database'] = 'connected'
    except Exception as e:
        status['database'] = f'error: {str(e)}'
        status['status'] = 'error'
        status_code = 503

    try:
        from celery import current_app
        current_app.connection().ensure_connection(max_retries=1)
        status['redis'] = 'connected'
    except Exception as e:
        status['redis'] = f'error: {str(e)}'

    status['parser'] = 'python' if settings.USE_PYTHON_PARSER else 'legacy'

    return JsonResponse(status, status=status_code)


urlpatterns = [
    path('', health_check),
]