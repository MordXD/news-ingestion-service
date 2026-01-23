from rest_framework.routers import DefaultRouter
from .views import FeedViewSet

router = DefaultRouter()
router.register('', FeedViewSet, basename='feed')

urlpatterns = router.urls