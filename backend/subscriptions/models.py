from django.db import models


class RequiredChannel(models.Model):
    """A Telegram channel/group the user must join before using the bot."""

    name = models.CharField(max_length=200)
    username = models.CharField(
        max_length=100, blank=True, null=True,
        help_text="Public channel @username, without the @ (leave blank for private channels).",
    )
    chat_id = models.BigIntegerField(
        blank=True, null=True,
        help_text="Telegram chat_id, required for private channels so the bot can check membership via getChatMember.",
    )
    invite_link = models.URLField(help_text="Link shown to the user as the 'Subscribe' button.")
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["display_order", "id"]

    def __str__(self):
        return self.name
