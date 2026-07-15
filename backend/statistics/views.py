from datetime import timedelta

from django.db.models import Count
from django.db.models.functions import TruncDate
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView

from downloads.models import MusicRecognition, VideoDownload
from users.models import BotUser


class DashboardSummaryView(APIView):
    """
    GET /api/stats/dashboard/
    Single call that feeds the whole admin dashboard landing page: user
    counts, download counts (today/week/month), per-platform breakdown,
    and music-recognition success rate.
    """

    def get(self, request):
        now = timezone.now()
        today = timezone.localdate()
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)

        users_qs = BotUser.objects.all()
        downloads_qs = VideoDownload.objects.all()
        recognitions_qs = MusicRecognition.objects.all()

        data = {
            "users": {
                "total": users_qs.count(),
                "active_today": users_qs.filter(last_activity_at__date=today).count(),
                "new_today": users_qs.filter(created_at__date=today).count(),
                "blocked": users_qs.filter(is_blocked=True).count(),
                "premium": users_qs.filter(is_premium=True).count(),
            },
            "downloads": {
                "total": downloads_qs.count(),
                "today": downloads_qs.filter(created_at__date=today).count(),
                "this_week": downloads_qs.filter(created_at__gte=week_ago).count(),
                "this_month": downloads_qs.filter(created_at__gte=month_ago).count(),
                "failed": downloads_qs.filter(status="failed").count(),
            },
            "platforms": list(
                downloads_qs.values("platform").annotate(count=Count("id")).order_by("-count")
            ),
            "music": {
                "total_detected": recognitions_qs.filter(found=True).count(),
                "failed_recognition": recognitions_qs.filter(found=False).count(),
                "most_recognized": list(
                    recognitions_qs.filter(found=True)
                    .values("song_name", "artist")
                    .annotate(count=Count("id"))
                    .order_by("-count")[:10]
                ),
            },
        }
        return Response(data)


class DownloadTimeSeriesView(APIView):
    """GET /api/stats/downloads-timeseries/?days=30 — for the download chart."""

    def get(self, request):
        days = int(request.query_params.get("days", 30))
        since = timezone.now() - timedelta(days=days)

        series = (
            VideoDownload.objects.filter(created_at__gte=since)
            .annotate(day=TruncDate("created_at"))
            .values("day")
            .annotate(count=Count("id"))
            .order_by("day")
        )
        return Response(list(series))


class UserGrowthTimeSeriesView(APIView):
    """GET /api/stats/user-growth/?days=30 — for the user growth chart."""

    def get(self, request):
        days = int(request.query_params.get("days", 30))
        since = timezone.now() - timedelta(days=days)

        series = (
            BotUser.objects.filter(created_at__gte=since)
            .annotate(day=TruncDate("created_at"))
            .values("day")
            .annotate(count=Count("id"))
            .order_by("day")
        )
        return Response(list(series))
