from rest_framework import serializers

from .models import RequiredChannel


class RequiredChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequiredChannel
        fields = [
            "id", "name", "username", "chat_id", "invite_link",
            "is_active", "display_order",
        ]
