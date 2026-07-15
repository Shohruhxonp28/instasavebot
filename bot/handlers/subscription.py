from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.exceptions import TelegramBadRequest

from bot.keyboards.inline import subscription_keyboard
from bot.locales import t
from bot.services.api_client import backend_client

router = Router(name="subscription")


@router.callback_query(F.data == "check_subscription")
async def on_check_subscription(callback: CallbackQuery, lang: str):
    bot = callback.bot
    channels = await backend_client.get_active_channels()

    not_subscribed = []
    for channel in channels:
        chat_ref = channel.get("chat_id") or (
            f"@{channel['username']}" if channel.get("username") else None
        )
        if not chat_ref:
            continue
        try:
            member = await bot.get_chat_member(chat_id=chat_ref, user_id=callback.from_user.id)
            if member.status in ("left", "kicked"):
                not_subscribed.append(channel)
        except TelegramBadRequest:
            continue

    if not_subscribed:
        await callback.answer(t(lang, "still_not_subscribed"), show_alert=True)
        await callback.message.edit_reply_markup(
            reply_markup=subscription_keyboard(not_subscribed, t(lang, "check_subscription"))
        )
        return

    await callback.message.edit_text(t(lang, "subscription_ok"))
    await callback.answer()
