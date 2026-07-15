from django.db import models


class Language(models.TextChoices):
    UZBEK = "uz", "O'zbekcha"
    RUSSIAN = "ru", "Русский"
    ENGLISH = "en", "English"


class BotUser(models.Model):
    """A Telegram end-user. Deliberately not django.contrib.auth.User —
    these people never log into anything, they only talk through the bot."""

    telegram_id = models.BigIntegerField(unique=True, db_index=True)
    username = models.CharField(max_length=64, blank=True, null=True)
    first_name = models.CharField(max_length=128, blank=True, null=True)
    language = models.CharField(max_length=2, choices=Language.choices, default=Language.ENGLISH)

    is_active = models.BooleanField(default=True)
    is_blocked = models.BooleanField(default=False)
    is_premium = models.BooleanField(default=False)
    premium_expires_at = models.DateTimeField(blank=True, null=True)

    last_activity_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["telegram_id"])]

    def __str__(self):
        return f"@{self.username or self.telegram_id}"

    @property
    def download_count(self) -> int:
        return self.downloads.count()
