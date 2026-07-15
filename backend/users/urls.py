from rest_framework.routers import DefaultRouter

from .views import BotUserViewSet

router = DefaultRouter()
router.register("", BotUserViewSet, basename="botuser")

urlpatterns = router.urls
