from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, Message

from bot.keyboards.inline import language_keyboard
from bot.locales import t
from bot.services.api_client import backend_client

router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(message: Message, lang: str, bot_user: dict | None = None):
    await message.answer(t(lang, "welcome"))
    await message.answer(t(lang, "choose_language"), reply_markup=language_keyboard())


@router.message(Command("language"))
async def cmd_language(message: Message, lang: str):
    await message.answer(t(lang, "choose_language"), reply_markup=language_keyboard())


@router.callback_query(F.data.startswith("lang:"))
async def on_language_selected(callback: CallbackQuery):
    lang_code = callback.data.split(":", 1)[1]
    await backend_client.register_or_touch_user(
        telegram_id=callback.from_user.id,
        username=callback.from_user.username,
        first_name=callback.from_user.first_name,
        language=lang_code,
    )
    await callback.message.edit_text(t(lang_code, "language_set"))
    await callback.answer()
