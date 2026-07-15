"""
Celery pipeline: download video -> extract audio -> identify song -> persist
results. This is the async heart of the whole product; the bot only ever
enqueues `process_video_download` and later polls/receives the result via the
API (see bot/services/api_client.py and bot/handlers/download.py).
"""
import logging
import os
import sys

from celery import shared_task
from django.conf import settings

# In the Docker image `services/` is copied to /app/services (a sibling of
# this app, importable directly). For local/dev runs where the repo root
# (one level above `backend/`) is on disk instead, fall back to adding it to
# sys.path so `import services...` still resolves without needing to `pip
# install` the shared library separately.
try:
    import services  # noqa: F401
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from services.downloader import (  # noqa: E402
    DownloadError, FileTooLargeError, UnsupportedURLError, VideoDownloader,
)
from services.ffmpeg_service import FFmpegError, extract_audio_sample  # noqa: E402
from services.music_recognition import ACRCloudClient  # noqa: E402

from .models import DownloadStatus, MusicRecognition, VideoDownload  # noqa: E402

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=2, default_retry_delay=10)
def process_video_download(self, download_id: int):
    """
    Full pipeline for a single VideoDownload row:
      1. download the video with yt-dlp
      2. extract a short audio sample with ffmpeg
      3. identify the track via ACRCloud
      4. persist everything

    Designed to be safely retried: each step re-checks current DB state
    before doing expensive work again.
    """
    try:
        download = VideoDownload.objects.select_related("user").get(pk=download_id)
    except VideoDownload.DoesNotExist:
        logger.error("VideoDownload %s vanished before processing", download_id)
        return

    download.status = DownloadStatus.DOWNLOADING
    download.celery_task_id = self.request.id
    download.save(update_fields=["status", "celery_task_id"])

    downloader = VideoDownloader(
        download_dir=settings.DOWNLOAD_STORAGE_DIR,
        max_file_size_mb=settings.MAX_FILE_SIZE_MB,
        hd_quality=download.user.is_premium,
    )

    try:
        result = downloader.download(download.url)
    except UnsupportedURLError as exc:
        _fail(download, f"Unsupported URL: {exc}")
        return
    except FileTooLargeError as exc:
        _fail(download, f"File too large: {exc}")
        return
    except DownloadError as exc:
        logger.warning("Download failed for %s: %s", download.url, exc)
        raise self.retry(exc=exc)

    download.platform = result.platform.value
    download.file_path = result.file_path
    download.title = result.title
    download.duration_seconds = result.duration
    download.file_size_bytes = os.path.getsize(result.file_path)
    download.status = DownloadStatus.RECOGNIZING
    download.save(
        update_fields=[
            "platform", "file_path", "title", "duration_seconds",
            "file_size_bytes", "status",
        ]
    )

    _recognize_music(download)

    download.status = DownloadStatus.DONE
    download.save(update_fields=["status"])


def _recognize_music(download: VideoDownload) -> None:
    try:
        sample_path = extract_audio_sample(download.file_path, settings.DOWNLOAD_STORAGE_DIR)
    except FFmpegError as exc:
        logger.warning("FFmpeg extraction failed for download %s: %s", download.pk, exc)
        MusicRecognition.objects.update_or_create(
            video=download, defaults={"found": False, "raw_response": {"error": str(exc)}}
        )
        return

    client = ACRCloudClient(
        host=settings.ACRCLOUD_HOST,
        access_key=settings.ACRCLOUD_ACCESS_KEY,
        access_secret=settings.ACRCLOUD_ACCESS_SECRET,
    )
    recognition = client.identify(sample_path)

    MusicRecognition.objects.update_or_create(
        video=download,
        defaults={
            "found": recognition.found,
            "song_name": recognition.title,
            "artist": recognition.artist,
            "album": recognition.album,
            "confidence": recognition.confidence,
            "youtube_url": recognition.youtube_url,
            "spotify_url": recognition.spotify_url,
            "apple_music_url": recognition.apple_music_url,
            "raw_response": recognition.raw,
        },
    )

    # Sample file is only needed transiently.
    try:
        os.remove(sample_path)
    except OSError:
        pass


def _fail(download: VideoDownload, message: str) -> None:
    download.status = DownloadStatus.FAILED
    download.error_message = message[:2000]
    download.save(update_fields=["status", "error_message"])
