from django.contrib import admin

from .models import MusicRecognition, VideoDownload


class MusicRecognitionInline(admin.StackedInline):
    model = MusicRecognition
    extra = 0
    readonly_fields = [f.name for f in MusicRecognition._meta.fields]
    can_delete = False


@admin.register(VideoDownload)
class VideoDownloadAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "platform", "status", "title", "created_at")
    list_filter = ("platform", "status", "created_at")
    search_fields = ("url", "user__telegram_id", "user__username", "title")
    readonly_fields = ("created_at", "updated_at", "celery_task_id")
    inlines = [MusicRecognitionInline]


@admin.register(MusicRecognition)
class MusicRecognitionAdmin(admin.ModelAdmin):
    list_display = ("id", "video", "found", "song_name", "artist", "confidence", "created_at")
    list_filter = ("found",)
    search_fields = ("song_name", "artist", "album")
