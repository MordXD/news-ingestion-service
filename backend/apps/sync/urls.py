from rest_framework.routers import DefaultRouter
from .views import SyncLogViewSet

router = DefaultRouter()
router.register('logs', SyncLogViewSet, basename='synclog')

urlpatterns = router.urls