from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import BotUser
from .serializers import BotUserSerializer, RegisterOrTouchSerializer


class BotUserViewSet(viewsets.ModelViewSet):
    """
    Internal API consumed by the Telegram bot process (and by the admin
    dashboard for read-only reporting).
    """

    queryset = BotUser.objects.all()
    serializer_class = BotUserSerializer
    filterset_fields = ["language", "is_blocked", "is_premium"]
    search_fields = ["username", "telegram_id", "first_name"]

    @action(detail=False, methods=["post"], url_path="register-or-touch")
    def register_or_touch(self, request):
        """Idempotent upsert called on every user interaction with the bot."""
        serializer = RegisterOrTouchSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        user, created = BotUser.objects.get_or_create(
            telegram_id=data["telegram_id"],
            defaults={
                "username": data.get("username"),
                "first_name": data.get("first_name"),
                "language": data.get("language", "en"),
            },
        )
        if not created:
            user.username = data.get("username", user.username)
            user.first_name = data.get("first_name", user.first_name)
            if data.get("language"):
                user.language = data["language"]
            user.last_activity_at = timezone.now()
            user.save(update_fields=["username", "first_name", "language", "last_activity_at"])

        return Response(
            BotUserSerializer(user).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"])
    def block(self, request, pk=None):
        user = self.get_object()
        user.is_blocked = True
        user.save(update_fields=["is_blocked"])
        return Response(BotUserSerializer(user).data)

    @action(detail=True, methods=["post"])
    def unblock(self, request, pk=None):
        user = self.get_object()
        user.is_blocked = False
        user.save(update_fields=["is_blocked"])
        return Response(BotUserSerializer(user).data)
