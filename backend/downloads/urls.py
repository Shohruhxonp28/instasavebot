from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import CreateDownloadJobView, VideoDownloadViewSet

router = DefaultRouter()
router.register("", VideoDownloadViewSet, basename="videodownload")

urlpatterns = [
    path("create-job/", CreateDownloadJobView.as_view(), name="download-create-job"),
] + router.urls
