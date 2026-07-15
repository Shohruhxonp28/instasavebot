"""
Platform-agnostic video downloader built on top of yt-dlp.

This module has zero framework dependencies (no Django, no Aiogram) so it can
be imported from Celery tasks, management commands, or tests alike.
"""
from __future__ import annotations

import logging
import os
import re
import uuid
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional

import yt_dlp

logger = logging.getLogger(__name__)


class Platform(str, Enum):
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    YOUTUBE = "youtube"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    UNKNOWN = "unknown"


_PLATFORM_PATTERNS = {
    Platform.TIKTOK: re.compile(r"(tiktok\.com|vm\.tiktok\.com)", re.I),
    Platform.INSTAGRAM: re.compile(r"instagram\.com", re.I),
    Platform.YOUTUBE: re.compile(r"(youtube\.com|youtu\.be)", re.I),
    Platform.FACEBOOK: re.compile(r"(facebook\.com|fb\.watch)", re.I),
    Platform.TWITTER: re.compile(r"(twitter\.com|x\.com)", re.I),
}

_URL_RE = re.compile(r"https?://\S+", re.I)


class DownloadError(Exception):
    """Raised when a download cannot be completed."""


class UnsupportedURLError(DownloadError):
    """Raised when the URL doesn't match any supported platform."""


class FileTooLargeError(DownloadError):
    """Raised when the downloaded file exceeds the configured limit."""


@dataclass
class DownloadResult:
    file_path: str
    platform: Platform
    title: Optional[str]
    duration: Optional[float]
    thumbnail_url: Optional[str]
    source_url: str


def extract_url(text: str) -> Optional[str]:
    """Pull the first http(s) URL out of an arbitrary user message."""
    match = _URL_RE.search(text or "")
    return match.group(0) if match else None


def detect_platform(url: str) -> Platform:
    for platform, pattern in _PLATFORM_PATTERNS.items():
        if pattern.search(url):
            return platform
    return Platform.UNKNOWN


class VideoDownloader:
    """Thin, testable wrapper around yt-dlp."""

    def __init__(self, download_dir: str = "/tmp/downloads", max_file_size_mb: int = 200,
                 hd_quality: bool = False):
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(parents=True, exist_ok=True)
        self.max_file_size_bytes = max_file_size_mb * 1024 * 1024
        self.hd_quality = hd_quality

    def _format_selector(self) -> str:
        if self.hd_quality:
            return "bestvideo[ext=mp4][height<=1080]+bestaudio[ext=m4a]/best[ext=mp4]/best"
        return "bestvideo[ext=mp4][height<=720]+bestaudio[ext=m4a]/best[ext=mp4]/best"

    def download(self, url: str) -> DownloadResult:
        platform = detect_platform(url)
        if platform is Platform.UNKNOWN:
            raise UnsupportedURLError(f"URL not recognized as a supported platform: {url}")

        job_id = uuid.uuid4().hex
        output_template = str(self.download_dir / f"{job_id}.%(ext)s")

        ydl_opts = {
            "format": self._format_selector(),
            "outtmpl": output_template,
            "merge_output_format": "mp4",
            "noplaylist": True,
            "quiet": True,
            "no_warnings": True,
            "max_filesize": self.max_file_size_bytes,
            "retries": 3,
            "socket_timeout": 30,
            # Some platforms need a browser-like UA to avoid being blocked.
            "http_headers": {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
                )
            },
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
        except yt_dlp.utils.DownloadError as exc:
            logger.exception("yt-dlp failed for %s", url)
            raise DownloadError(str(exc)) from exc

        file_path = self._resolve_output_path(job_id, info)
        if not file_path or not os.path.exists(file_path):
            raise DownloadError("Download finished but output file was not found.")

        size = os.path.getsize(file_path)
        if size > self.max_file_size_bytes:
            os.remove(file_path)
            raise FileTooLargeError(
                f"File is {size / (1024 * 1024):.1f}MB, exceeds limit "
                f"{self.max_file_size_bytes / (1024 * 1024):.0f}MB"
            )

        return DownloadResult(
            file_path=file_path,
            platform=platform,
            title=info.get("title"),
            duration=info.get("duration"),
            thumbnail_url=info.get("thumbnail"),
            source_url=url,
        )

    def _resolve_output_path(self, job_id: str, info: dict) -> Optional[str]:
        # yt-dlp may merge into a different extension than requested; scan for it.
        for f in self.download_dir.glob(f"{job_id}.*"):
            return str(f)
        # fallback: requested_downloads metadata (present on newer yt-dlp)
        rd = info.get("requested_downloads") or []
        if rd and "filepath" in rd[0]:
            return rd[0]["filepath"]
        return None
