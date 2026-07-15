"""Minimal i18n dictionary. Swap for gettext/.po files if the string set grows a lot."""

STRINGS = {
    "en": {
        "welcome": (
            "👋 Send a video link from TikTok, Instagram, YouTube and I will "
            "download it and identify the music.\n\n"
            "Supported: TikTok, Instagram Reels, YouTube Shorts/videos, "
            "Facebook, Twitter/X."
        ),
        "choose_language": "🌐 Please choose your language:",
        "language_set": "Language set to English ✅",
        "must_subscribe": "🔒 You must subscribe to these channels before using the bot:",
        "check_subscription": "✅ Check subscription",
        "still_not_subscribed": "⚠️ You still haven't joined all the required channels.",
        "subscription_ok": "✅ Thanks! You can now send a video link.",
        "invalid_url": "❌ I couldn't find a valid link in your message.",
        "unsupported_platform": "❌ This platform isn't supported yet.",
        "processing": "⏳ Downloading your video…",
        "video_downloaded": "✅ Video downloaded",
        "detecting_music": "🎵 Detecting music…",
        "music_found": "🎵 Music Found:",
        "music_not_found": "😕 Couldn't identify the music in this video.",
        "song_label": "Song",
        "artist_label": "Artist",
        "album_label": "Album",
        "confidence_label": "Confidence",
        "daily_limit_reached": "🚫 You've reached your daily download limit ({limit}). Try again tomorrow or upgrade to Premium.",
        "blocked": "🚫 Your account has been blocked from using this bot.",
        "generic_error": "⚠️ Something went wrong while processing your video. Please try again later.",
        "file_too_large": "⚠️ This video is too large to send via Telegram.",
    },
    "ru": {
        "welcome": (
            "👋 Отправьте ссылку на видео из TikTok, Instagram, YouTube — я "
            "скачаю его и определю музыку.\n\n"
            "Поддерживаются: TikTok, Instagram Reels, YouTube Shorts/видео, "
            "Facebook, Twitter/X."
        ),
        "choose_language": "🌐 Выберите язык:",
        "language_set": "Язык изменён на русский ✅",
        "must_subscribe": "🔒 Чтобы пользоваться ботом, подпишитесь на каналы:",
        "check_subscription": "✅ Проверить подписку",
        "still_not_subscribed": "⚠️ Вы ещё не подписались на все каналы.",
        "subscription_ok": "✅ Спасибо! Теперь отправьте ссылку на видео.",
        "invalid_url": "❌ Не удалось найти ссылку в сообщении.",
        "unsupported_platform": "❌ Эта платформа пока не поддерживается.",
        "processing": "⏳ Скачиваю видео…",
        "video_downloaded": "✅ Видео скачано",
        "detecting_music": "🎵 Определяю музыку…",
        "music_found": "🎵 Музыка найдена:",
        "music_not_found": "😕 Не удалось определить музыку в этом видео.",
        "song_label": "Трек",
        "artist_label": "Исполнитель",
        "album_label": "Альбом",
        "confidence_label": "Точность",
        "daily_limit_reached": "🚫 Вы достигли дневного лимита ({limit}). Попробуйте завтра или оформите Premium.",
        "blocked": "🚫 Ваш аккаунт заблокирован.",
        "generic_error": "⚠️ Не удалось обработать видео. Попробуйте позже.",
        "file_too_large": "⚠️ Видео слишком большое для отправки через Telegram.",
    },
    "uz": {
        "welcome": (
            "👋 TikTok, Instagram yoki YouTube'dan video havolasini yuboring — "
            "men uni yuklab beraman va musiqasini aniqlayman.\n\n"
            "Qo'llab-quvvatlanadi: TikTok, Instagram Reels, YouTube Shorts/"
            "videolar, Facebook, Twitter/X."
        ),
        "choose_language": "🌐 Tilni tanlang:",
        "language_set": "Til o'zbekchaga o'zgartirildi ✅",
        "must_subscribe": "🔒 Botdan foydalanish uchun quyidagi kanallarga obuna bo'ling:",
        "check_subscription": "✅ Obunani tekshirish",
        "still_not_subscribed": "⚠️ Siz hali barcha kanallarga obuna bo'lmadingiz.",
        "subscription_ok": "✅ Rahmat! Endi video havolasini yuborishingiz mumkin.",
        "invalid_url": "❌ Xabaringizda to'g'ri havola topilmadi.",
        "unsupported_platform": "❌ Bu platforma hali qo'llab-quvvatlanmaydi.",
        "processing": "⏳ Video yuklanmoqda…",
        "video_downloaded": "✅ Video yuklab olindi",
        "detecting_music": "🎵 Musiqa aniqlanmoqda…",
        "music_found": "🎵 Musiqa topildi:",
        "music_not_found": "😕 Ushbu videodagi musiqani aniqlab bo'lmadi.",
        "song_label": "Qo'shiq",
        "artist_label": "Ijrochi",
        "album_label": "Albom",
        "confidence_label": "Ishonch",
        "daily_limit_reached": "🚫 Kunlik limitga yetdingiz ({limit}). Ertaga urinib ko'ring yoki Premium sotib oling.",
        "blocked": "🚫 Hisobingiz botdan foydalanishdan bloklangan.",
        "generic_error": "⚠️ Videoni qayta ishlashda xatolik yuz berdi. Keyinroq urinib ko'ring.",
        "file_too_large": "⚠️ Video Telegram orqali yuborish uchun juda katta.",
    },
}


def t(lang: str, key: str, **kwargs) -> str:
    lang = lang if lang in STRINGS else "en"
    text = STRINGS[lang].get(key) or STRINGS["en"].get(key, key)
    return text.format(**kwargs) if kwargs else text
