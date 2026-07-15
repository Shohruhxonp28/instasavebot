from __future__ import annotations

from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject

from bot.services.api_client import backend_client


class UserContextMiddleware(BaseMiddleware):
    """
    Upserts the BotUser on every update and stashes their language + record
    in `data`, so downstream handlers/middlewares don't each need to call the
    backend separately.
    """

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        tg_user = None
        if isinstance(event, Message):
            tg_user = event.from_user
        elif isinstance(event, CallbackQuery):
            tg_user = event.from_user

        if tg_user is not None:
            try:
                bot_user = await backend_client.register_or_touch_user(
                    telegram_id=tg_user.id,
                    username=tg_user.username,
                    first_name=tg_user.first_name,
                )
                data["bot_user"] = bot_user
                data["lang"] = bot_user.get("language", "en")
            except Exception:
                # Backend hiccup shouldn't take the whole bot down — fall
                # back to English and let the handler try again.
                data["lang"] = "en"

        return await handler(event, data)
