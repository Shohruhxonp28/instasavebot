"""
ACRCloud music-recognition client.

Implements ACRCloud's HTTP identification API signature scheme directly
(HMAC-SHA1 over a canonical string), so this module has no dependency beyond
`requests` and the stdlib.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import logging
import time
from dataclasses import dataclass
from typing import Optional

import requests

logger = logging.getLogger(__name__)


@dataclass
class RecognitionResult:
    found: bool
    title: Optional[str] = None
    artist: Optional[str] = None
    album: Optional[str] = None
    confidence: Optional[int] = None
    youtube_url: Optional[str] = None
    spotify_url: Optional[str] = None
    apple_music_url: Optional[str] = None
    raw: Optional[dict] = None


class ACRCloudClient:
    def __init__(self, host: str, access_key: str, access_secret: str, timeout: int = 15):
        self.host = host
        self.access_key = access_key
        self.access_secret = access_secret
        self.timeout = timeout
        self.endpoint = f"https://{host}/v1/identify"

    def _signature(self, string_to_sign: str) -> str:
        digest = hmac.new(
            self.access_secret.encode("utf-8"),
            string_to_sign.encode("utf-8"),
            hashlib.sha1,
        ).digest()
        return base64.b64encode(digest).decode("utf-8")

    def identify(self, audio_file_path: str) -> RecognitionResult:
        with open(audio_file_path, "rb") as f:
            sample_bytes = f.read()

        http_method = "POST"
        http_uri = "/v1/identify"
        data_type = "audio"
        signature_version = "1"
        timestamp = str(int(time.time()))

        string_to_sign = "\n".join(
            [http_method, http_uri, self.access_key, data_type, signature_version, timestamp]
        )
        signature = self._signature(string_to_sign)

        files = {"sample": ("sample.mp3", sample_bytes, "audio/mpeg")}
        data = {
            "access_key": self.access_key,
            "sample_bytes": str(len(sample_bytes)),
            "timestamp": timestamp,
            "signature": signature,
            "data_type": data_type,
            "signature_version": signature_version,
        }

        try:
            response = requests.post(
                self.endpoint, files=files, data=data, timeout=self.timeout
            )
            response.raise_for_status()
            payload = response.json()
        except requests.RequestException as exc:
            logger.exception("ACRCloud request failed")
            return RecognitionResult(found=False, raw={"error": str(exc)})

        return self._parse(payload)

    @staticmethod
    def _parse(payload: dict) -> RecognitionResult:
        status = payload.get("status", {})
        if status.get("code") != 0:
            # code 1001 = no result found; anything else = error
            return RecognitionResult(found=False, raw=payload)

        music_matches = (payload.get("metadata") or {}).get("music") or []
        if not music_matches:
            return RecognitionResult(found=False, raw=payload)

        match = music_matches[0]
        artists = match.get("artists") or []
        artist_name = ", ".join(a.get("name", "") for a in artists if a.get("name"))
        album = (match.get("album") or {}).get("name")

        external = match.get("external_metadata") or {}
        youtube_url = None
        spotify_url = None
        apple_music_url = None

        if "youtube" in external and external["youtube"].get("vid"):
            youtube_url = f"https://www.youtube.com/watch?v={external['youtube']['vid']}"
        if "spotify" in external:
            track_id = (external["spotify"].get("track") or {}).get("id")
            if track_id:
                spotify_url = f"https://open.spotify.com/track/{track_id}"
        if "applemusic" in external or "apple_music" in external:
            am = external.get("applemusic") or external.get("apple_music") or {}
            apple_music_url = am.get("url") or None

        return RecognitionResult(
            found=True,
            title=match.get("title"),
            artist=artist_name or None,
            album=album,
            confidence=match.get("score"),
            youtube_url=youtube_url,
            spotify_url=spotify_url,
            apple_music_url=apple_music_url,
            raw=payload,
        )
