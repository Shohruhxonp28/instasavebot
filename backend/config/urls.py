from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/users/", include("users.urls")),
    path("api/downloads/", include("downloads.urls")),
    path("api/subscriptions/", include("subscriptions.urls")),
    path("api/ads/", include("advertisements.urls")),
    path("api/stats/", include("statistics.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
