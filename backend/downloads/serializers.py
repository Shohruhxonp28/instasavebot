from rest_framework import serializers

from .models import MusicRecognition, VideoDownload


class MusicRecognitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MusicRecognition
        fields = [
            "found", "song_name", "artist", "album", "confidence",
            "youtube_url", "spotify_url", "apple_music_url", "created_at",
        ]


class VideoDownloadSerializer(serializers.ModelSerializer):
    recognition = MusicRecognitionSerializer(read_only=True)

    class Meta:
        model = VideoDownload
        fields = [
            "id", "user", "platform", "url", "file_path", "title",
            "duration_seconds", "file_size_bytes", "status", "error_message",
            "celery_task_id", "recognition", "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "platform", "file_path", "title", "duration_seconds",
            "file_size_bytes", "status", "error_message", "celery_task_id",
            "recognition", "created_at", "updated_at",
        ]


class VideoDownloadCreateSerializer(serializers.Serializer):
    """What the bot sends when a user pastes a link."""
    telegram_id = serializers.IntegerField()
    url = serializers.URLField()
