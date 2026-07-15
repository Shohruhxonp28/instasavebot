from rest_framework import serializers

from .models import BotUser


class BotUserSerializer(serializers.ModelSerializer):
    download_count = serializers.ReadOnlyField()

    class Meta:
        model = BotUser
        fields = [
            "id", "telegram_id", "username", "first_name", "language",
            "is_active", "is_blocked", "is_premium", "premium_expires_at",
            "download_count", "last_activity_at", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "last_activity_at"]


class RegisterOrTouchSerializer(serializers.Serializer):
    """Used by the bot on every /start or incoming message: upsert the user
    and bump last_activity_at in one call."""

    telegram_id = serializers.IntegerField()
    username = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    first_name = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    language = serializers.ChoiceField(choices=["uz", "ru", "en"], required=False)
