from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def language_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="lang:uz"),
                InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang:ru"),
                InlineKeyboardButton(text="🇬🇧 English", callback_data="lang:en"),
            ]
        ]
    )


def subscription_keyboard(channels: list[dict], check_text: str) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text=f"📢 {ch['name']}", url=ch["invite_link"])]
        for ch in channels
    ]
    rows.append([InlineKeyboardButton(text=check_text, callback_data="check_subscription")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def music_result_keyboard(recognition: dict) -> InlineKeyboardMarkup:
    row = []
    if recognition.get("youtube_url"):
        row.append(InlineKeyboardButton(text="▶ YouTube", url=recognition["youtube_url"]))
    if recognition.get("spotify_url"):
        row.append(InlineKeyboardButton(text="🎧 Spotify", url=recognition["spotify_url"]))
    if recognition.get("apple_music_url"):
        row.append(InlineKeyboardButton(text="🍎 Apple Music", url=recognition["apple_music_url"]))
    return InlineKeyboardMarkup(inline_keyboard=[row] if row else [])


def ad_keyboard(ad: dict, backend_base_url: str) -> InlineKeyboardMarkup | None:
    if not ad.get("button_url"):
        return None
    text = ad.get("button_text") or "Learn more"
    # Route through the backend's redirect endpoint so the click gets counted
    # server-side, then 302s the user on to the real destination.
    redirect_url = f"{backend_base_url}/api/ads/{ad['id']}/redirect/"
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=text, url=redirect_url)]])
