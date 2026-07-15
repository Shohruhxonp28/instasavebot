"""
Mandatory-subscription gate.

Real Telegram membership can only be checked with the Bot API's
`getChatMember`, which requires bot_token + chat_id — so unlike everything
else, this middleware talks to Telegram directly rather than through the
Django backend. The *list* of required channels still comes from Django
(admin-managed), only the membership check itself is done here.
"""
from __future__ import annotations

from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject
from aiogram.exceptions import TelegramBadRequest

from bot.keyboards.inline import subscription_keyboard
from bot.locales import t
from bot.services.api_client import backend_client

# /start, language selection, and the "check subscription" button itself must
# always be allowed through, or a not-yet-subscribed user could never escape.
_ALWAYS_ALLOWED_COMMANDS = {"/start", "/help", "/language"}
_ALWAYS_ALLOWED_CALLBACKS_PREFIXES = ("lang:", "check_subscription")


class SubscriptionMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        bot = data["bot"]
        lang = data.get("lang", "en")

        if isinstance(event, Message):
            text = (event.text or "").strip()
            if text in _ALWAYS_ALLOWED_COMMANDS:
                return await handler(event, data)
            user_id = event.from_user.id
        elif isinstance(event, CallbackQuery):
            if event.data and event.data.startswith(_ALWAYS_ALLOWED_CALLBACKS_PREFIXES):
                return await handler(event, data)
            user_id = event.from_user.id
        else:
            return await handler(event, data)

        channels = await backend_client.get_active_channels()
        if not channels:
            return await handler(event, data)  # no gate configured

        not_subscribed = []
        for channel in channels:
            chat_ref = channel.get("chat_id") or (
                f"@{channel['username']}" if channel.get("username") else None
            )
            if not chat_ref:
                continue
            try:
                member = await bot.get_chat_member(chat_id=chat_ref, user_id=user_id)
                if member.status in ("left", "kicked"):
                    not_subscribed.append(channel)
            except TelegramBadRequest:
                # Bot isn't admin in that channel / channel unreachable — skip
                # rather than block every user because of a misconfiguration.
                continue

        if not_subscribed:
            markup = subscription_keyboard(not_subscribed, t(lang, "check_subscription"))
            target = event.message if isinstance(event, CallbackQuery) else event
            await target.answer(t(lang, "must_subscribe"), reply_markup=markup)
            return None

        return await handler(event, data)
