from rest_framework import serializers

from .models import Advertisement


class AdvertisementSerializer(serializers.ModelSerializer):
    ctr = serializers.ReadOnlyField()

    class Meta:
        model = Advertisement
        fields = [
            "id", "type", "title", "content", "media_file", "button_text",
            "button_url", "placement", "frequency", "start_date", "end_date",
            "active", "views", "clicks", "ctr", "created_at", "updated_at",
        ]
        read_only_fields = ["views", "clicks", "created_at", "updated_at"]
