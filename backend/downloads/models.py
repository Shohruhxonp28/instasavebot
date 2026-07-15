from django.db import models

from users.models import BotUser


class Platform(models.TextChoices):
    TIKTOK = "tiktok", "TikTok"
    INSTAGRAM = "instagram", "Instagram"
    YOUTUBE = "youtube", "YouTube"
    FACEBOOK = "facebook", "Facebook"
    TWITTER = "twitter", "Twitter/X"
    UNKNOWN = "unknown", "Unknown"


class DownloadStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    DOWNLOADING = "downloading", "Downloading"
    RECOGNIZING = "recognizing", "Recognizing audio"
    DONE = "done", "Done"
    FAILED = "failed", "Failed"


class VideoDownload(models.Model):
    user = models.ForeignKey(BotUser, on_delete=models.CASCADE, related_name="downloads")
    platform = models.CharField(max_length=16, choices=Platform.choices, default=Platform.UNKNOWN)
    url = models.URLField(max_length=1000)
    file_path = models.CharField(max_length=500, blank=True, null=True)
    title = models.CharField(max_length=500, blank=True, null=True)
    duration_seconds = models.FloatField(blank=True, null=True)
    file_size_bytes = models.BigIntegerField(blank=True, null=True)
    status = models.CharField(max_length=16, choices=DownloadStatus.choices, default=DownloadStatus.PENDING)
    error_message = models.TextField(blank=True, null=True)

    celery_task_id = models.CharField(max_length=64, blank=True, null=True, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["platform"]),
            models.Index(fields=["status"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.platform} download #{self.pk} for {self.user}"


class MusicRecognition(models.Model):
    video = models.OneToOneField(VideoDownload, on_delete=models.CASCADE, related_name="recognition")
    found = models.BooleanField(default=False)
    song_name = models.CharField(max_length=300, blank=True, null=True)
    artist = models.CharField(max_length=300, blank=True, null=True)
    album = models.CharField(max_length=300, blank=True, null=True)
    confidence = models.PositiveSmallIntegerField(blank=True, null=True)

    youtube_url = models.URLField(blank=True, null=True)
    spotify_url = models.URLField(blank=True, null=True)
    apple_music_url = models.URLField(blank=True, null=True)

    raw_response = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.song_name or 'Not found'} — {self.artist or ''}"
