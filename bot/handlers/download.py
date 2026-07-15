import asyncio
import os

from aiogram import Router
from aiogram.types import FSInputFile, Message

from bot.keyboards.inline import ad_keyboard, music_result_keyboard
from bot.locales import t
from bot.config import config
from bot.services.api_client import BackendAPIError, backend_client
from services.downloader import Platform, detect_platform, extract_url

router = Router(name="download")

_POLL_INTERVAL_SECONDS = 2
_POLL_TIMEOUT_SECONDS = 180


@router.message()
async def on_possible_link(message: Message, lang: str, bot_user: dict | None = None):
    text = message.text or message.caption or ""
    url = extract_url(text)
    if not url:
        await message.answer(t(lang, "invalid_url"))
        return

    if detect_platform(url) is Platform.UNKNOWN:
        await message.answer(t(lang, "unsupported_platform"))
        return

    await _maybe_show_ad(message, lang, placement="before_video", download_count=bot_user.get("download_count", 0) if bot_user else 0)

    progress = await message.answer(t(lang, "processing"))

    try:
        job = await backend_client.create_download_job(message.from_user.id, url)
    except BackendAPIError as exc:
        if exc.status == 429:
            limit = (exc.detail or {}).get("limit", "?")
            await progress.edit_text(t(lang, "daily_limit_reached", limit=limit))
        elif exc.status == 403:
            await progress.edit_text(t(lang, "blocked"))
        else:
            await progress.edit_text(t(lang, "generic_error"))
        return

    download = await _poll_until_done(job["id"])
    if download is None or download["status"] == "failed":
        await progress.edit_text(t(lang, "generic_error"))
        return

    await progress.edit_text(t(lang, "video_downloaded"))

    file_path = download.get("file_path")
    if file_path and os.path.exists(file_path):
        await message.answer_video(FSInputFile(file_path), caption=download.get("title") or "")
    else:
        await message.answer(t(lang, "file_too_large"))

    await message.answer(t(lang, "detecting_music"))
    await _send_recognition_result(message, lang, download)

    await _maybe_show_ad(
        message, lang, placement="every_n_downloads",
        download_count=(bot_user.get("download_count", 0) + 1) if bot_user else 1,
    )


async def _poll_until_done(download_id: int) -> dict | None:
    elapsed = 0
    while elapsed < _POLL_TIMEOUT_SECONDS:
        download = await backend_client.get_download(download_id)
        if download["status"] in ("done", "failed"):
            return download
        await asyncio.sleep(_POLL_INTERVAL_SECONDS)
        elapsed += _POLL_INTERVAL_SECONDS
    return None


async def _send_recognition_result(message: Message, lang: str, download: dict) -> None:
    recognition = download.get("recognition")
    if not recognition or not recognition.get("found"):
        await message.answer(t(lang, "music_not_found"))
        return

    lines = [
        t(lang, "music_found"),
        "",
        f"{t(lang, 'song_label')}: {recognition.get('song_name') or '—'}",
        f"{t(lang, 'artist_label')}: {recognition.get('artist') or '—'}",
        f"{t(lang, 'album_label')}: {recognition.get('album') or '—'}",
        f"{t(lang, 'confidence_label')}: {recognition.get('confidence') or 0}%",
    ]
    await message.answer("\n".join(lines), reply_markup=music_result_keyboard(recognition))


async def _maybe_show_ad(message: Message, lang: str, placement: str, download_count: int) -> None:
    ad = await backend_client.get_next_ad(placement, download_count)
    if not ad:
        return

    keyboard = ad_keyboard(ad, config.backend_base_url)
    if ad["type"] == "text":
        await message.answer(f"📢 {ad['content']}", reply_markup=keyboard)
    elif ad["type"] == "image" and ad.get("media_file"):
        await message.answer_photo(ad["media_file"], caption=ad["content"], reply_markup=keyboard)
    elif ad["type"] == "video" and ad.get("media_file"):
        await message.answer_video(ad["media_file"], caption=ad["content"], reply_markup=keyboard)
