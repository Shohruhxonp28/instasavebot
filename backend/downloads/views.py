from django.conf import settings
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import BotUser

from .models import VideoDownload
from .serializers import VideoDownloadCreateSerializer, VideoDownloadSerializer
from .tasks import process_video_download


class VideoDownloadViewSet(viewsets.ReadOnlyModelViewSet):
    """Read/list endpoint used by the admin dashboard and by the bot when
    polling for a job's status."""

    queryset = VideoDownload.objects.select_related("user", "recognition").all()
    serializer_class = VideoDownloadSerializer
    filterset_fields = ["platform", "status", "user"]


class CreateDownloadJobView(APIView):
    """
    POST /api/downloads/create-job/
    Called by the bot the instant a user pastes a supported link. Enforces
    daily limits, then enqueues the Celery pipeline and returns immediately
    with a task id the bot can poll or wait on.
    """

    throttle_scope = "download-create"

    def post(self, request):
        serializer = VideoDownloadCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            user = BotUser.objects.get(telegram_id=data["telegram_id"])
        except BotUser.DoesNotExist:
            return Response({"detail": "Unknown user; call register-or-touch first."},
                             status=status.HTTP_404_NOT_FOUND)

        if user.is_blocked:
            return Response({"detail": "User is blocked."}, status=status.HTTP_403_FORBIDDEN)

        limit = settings.PREMIUM_DAILY_DOWNLOAD_LIMIT if user.is_premium else settings.FREE_DAILY_DOWNLOAD_LIMIT
        today_count = user.downloads.filter(created_at__date=timezone.localdate()).count()
        if today_count >= limit:
            return Response(
                {"detail": "Daily download limit reached.", "limit": limit},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        download = VideoDownload.objects.create(user=user, url=data["url"])
        async_result = process_video_download.delay(download.pk)
        download.celery_task_id = async_result.id
        download.save(update_fields=["celery_task_id"])

        return Response(
            VideoDownloadSerializer(download).data,
            status=status.HTTP_202_ACCEPTED,
        )
