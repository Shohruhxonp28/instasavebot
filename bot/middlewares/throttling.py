"""Redis-backed throttling so a single user can't spam link after link."""
from __future__ import annotations

from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject
from redis.asyncio import Redis

from bot.config import config


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, redis: Redis, rate_seconds: float | None = None):
        self.redis = redis
        self.rate_seconds = rate_seconds or config.download_rate_limit_seconds

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        if not isinstance(event, Message) or not event.text:
            return await handler(event, data)

        key = f"throttle:{event.from_user.id}"
        is_set = await self.redis.set(key, "1", ex=int(self.rate_seconds) or 1, nx=True)
        if not is_set:
            return None  # silently drop; avoids spamming "slow down" replies

        return await handler(event, data)
