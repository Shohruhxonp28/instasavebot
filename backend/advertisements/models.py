from django.db import models
from django.utils import timezone


class AdType(models.TextChoices):
    TEXT = "text", "Text"
    IMAGE = "image", "Image"
    VIDEO = "video", "Video"


class AdPlacement(models.TextChoices):
    ON_START = "on_start", "On /start"
    BEFORE_VIDEO = "before_video", "Before sending video"
    EVERY_N_DOWNLOADS = "every_n_downloads", "Every N downloads"


class Advertisement(models.Model):
    type = models.CharField(max_length=10, choices=AdType.choices, default=AdType.TEXT)
    title = models.CharField(max_length=200)
    content = models.TextField(help_text="Caption / body text shown with the ad.")
    media_file = models.FileField(upload_to="ads/", blank=True, null=True)
    button_text = models.CharField(max_length=64, blank=True, default="Learn more")
    button_url = models.URLField(blank=True, null=True)

    placement = models.CharField(max_length=20, choices=AdPlacement.choices, default=AdPlacement.BEFORE_VIDEO)
    frequency = models.PositiveIntegerField(
        default=5, help_text="Used with placement=every_n_downloads: show every N downloads.",
    )

    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(blank=True, null=True)
    active = models.BooleanField(default=True)

    views = models.PositiveIntegerField(default=0)
    clicks = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    @property
    def is_currently_running(self) -> bool:
        now = timezone.now()
        if not self.active:
            return False
        if self.start_date and now < self.start_date:
            return False
        if self.end_date and now > self.end_date:
            return False
        return True

    @property
    def ctr(self) -> float:
        return round((self.clicks / self.views) * 100, 2) if self.views else 0.0
