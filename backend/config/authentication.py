"""
Simple shared-secret authentication used by the Telegram bot process when it
calls the internal REST API. Not intended for public/browser clients.
"""
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from rest_framework import authentication, exceptions


class InternalServiceUser(AnonymousUser):
    """A stand-in principal representing the bot service, not a real DB user."""

    is_authenticated = True

    def __str__(self):
        return "internal-bot-service"


class InternalTokenAuthentication(authentication.BaseAuthentication):
    keyword = "Bearer"

    def authenticate(self, request):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith(f"{self.keyword} "):
            return None

        token = auth_header.split(" ", 1)[1].strip()
        if token != settings.INTERNAL_API_TOKEN:
            raise exceptions.AuthenticationFailed("Invalid internal API token.")

        return (InternalServiceUser(), token)
