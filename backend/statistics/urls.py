from django.urls import path

from .views import DashboardSummaryView, DownloadTimeSeriesView, UserGrowthTimeSeriesView

urlpatterns = [
    path("dashboard/", DashboardSummaryView.as_view(), name="stats-dashboard"),
    path("downloads-timeseries/", DownloadTimeSeriesView.as_view(), name="stats-downloads-timeseries"),
    path("user-growth/", UserGrowthTimeSeriesView.as_view(), name="stats-user-growth"),
]
