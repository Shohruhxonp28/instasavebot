from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import AdRedirectView, AdvertisementViewSet, NextAdView

router = DefaultRouter()
router.register("", AdvertisementViewSet, basename="advertisement")

urlpatterns = [
    path("next/", NextAdView.as_view(), name="ad-next"),
    path("<int:pk>/redirect/", AdRedirectView.as_view(), name="ad-redirect"),
] + router.urls
