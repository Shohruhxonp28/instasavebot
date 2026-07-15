from rest_framework.routers import DefaultRouter

from .views import RequiredChannelViewSet

router = DefaultRouter()
router.register("", RequiredChannelViewSet, basename="requiredchannel")

urlpatterns = router.urls
