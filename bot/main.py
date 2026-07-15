import asyncio
import logging
import sys
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from redis.asyncio import Redis

# Make the shared `services/` library importable both in Docker (copied to
# /app/services alongside this file) and in local dev (repo root).
sys.path.append(str(Path(__file__).resolve().parent.parent))

from bot.config import config  # noqa: E402
from bot.handlers import get_root_router  # noqa: E402
from bot.middlewares.subscription_check import SubscriptionMiddleware  # noqa: E402
from bot.middlewares.throttling import ThrottlingMiddleware  # noqa: E402
from bot.middlewares.user_context import UserContextMiddleware  # noqa: E402

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)


from aiohttp import web

async def health_check(request):
    return web.Response(text="Bot is running!")

async def main() -> None:
    if not config.bot_token:
        raise RuntimeError("BOT_TOKEN is not set")

    bot = Bot(token=config.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    redis = Redis(host=config.redis_host, port=config.redis_port, db=config.redis_db)

    dp.message.middleware(UserContextMiddleware())
    dp.callback_query.middleware(UserContextMiddleware())
    dp.message.middleware(ThrottlingMiddleware(redis))
    dp.message.middleware(SubscriptionMiddleware())
    dp.callback_query.middleware(SubscriptionMiddleware())

    dp.include_router(get_root_router())

    logger.info("Starting bot polling and dummy web server…")
    await bot.delete_webhook(drop_pending_updates=True)
    
    # Start dummy web server for Render health checks
    app = web.Application()
    app.router.add_get("/", health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    
    import os
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

