import os
from dataclasses import dataclass, field
from typing import List


def _split_ids(raw: str) -> List[int]:
    return [int(x) for x in raw.split(",") if x.strip()]


@dataclass
class Config:
    bot_token: str = os.getenv("BOT_TOKEN", "")
    admin_ids: List[int] = field(default_factory=lambda: _split_ids(os.getenv("BOT_ADMIN_IDS", "")))

    backend_base_url: str = os.getenv("BACKEND_BASE_URL", "http://django_backend:8000")
    internal_api_token: str = os.getenv("DJANGO_INTERNAL_API_TOKEN", "change-me")

    redis_host: str = os.getenv("REDIS_HOST", "redis")
    redis_port: int = int(os.getenv("REDIS_PORT", "6379"))
    redis_db: int = int(os.getenv("REDIS_DB", "0"))

    max_file_size_mb: int = int(os.getenv("MAX_FILE_SIZE_MB", "200"))
    download_rate_limit_seconds: float = float(os.getenv("DOWNLOAD_RATE_LIMIT_SECONDS", "3"))

    default_language: str = "en"


config = Config()
