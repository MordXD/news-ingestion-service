from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/feeds/', include('apps.feeds.urls')),
    path('api/articles/', include('apps.articles.urls')),
    path('api/sync/', include('apps.sync.urls')),
    path('api/health/', include('config.health_urls')),
]