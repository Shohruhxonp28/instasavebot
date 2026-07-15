from rest_framework import viewsets

from .models import RequiredChannel
from .serializers import RequiredChannelSerializer


class RequiredChannelViewSet(viewsets.ModelViewSet):
    """
    CRUD used by the admin dashboard; the bot only ever calls the read-only
    `active` list (filtered client-side) to build the "please subscribe"
    keyboard, then checks real membership itself via Bot API `getChatMember`
    (see bot/middlewares/subscription_check.py) since Telegram membership
    can't be verified from the Django side without the bot token.
    """

    queryset = RequiredChannel.objects.all()
    serializer_class = RequiredChannelSerializer
    filterset_fields = ["is_active"]
