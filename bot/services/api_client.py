"""
Thin async HTTP client the bot uses to talk to the Django backend. The bot
process never touches Postgres/Redis/ACRCloud directly — this is the only
door between them, which keeps the bot horizontally scalable and lets the
backend be reused by other clients later (web dashboard, mobile app, etc).
"""
from __future__ import annotations

from typing import Any, Optional

import aiohttp

from bot.config import config


class BackendAPIError(Exception):
    def __init__(self, status: int, detail: Any):
        self.status = status
        self.detail = detail
        super().__init__(f"Backend API error {status}: {detail}")


class BackendClient:
    def __init__(self):
        self.base_url = config.backend_base_url.rstrip("/")
        self._headers = {"Authorization": f"Bearer {config.internal_api_token}"}

    async def _request(self, method: str, path: str, **kwargs) -> Optional[dict]:
        url = f"{self.base_url}{path}"
        async with aiohttp.ClientSession(headers=self._headers) as session:
            async with session.request(method, url, timeout=aiohttp.ClientTimeout(total=30), **kwargs) as resp:
                if resp.status == 204:
                    return None
                data = await resp.json(content_type=None)
                if resp.status >= 400:
                    raise BackendAPIError(resp.status, data)
                return data

    # ---------------------------------------------------------------- users
    async def register_or_touch_user(self, telegram_id: int, username: str | None,
                                      first_name: str | None, language: str | None = None) -> dict:
        payload = {"telegram_id": telegram_id, "username": username, "first_name": first_name}
        if language:
            payload["language"] = language
        return await self._request("POST", "/api/users/register-or-touch/", json=payload)

    # ------------------------------------------------------------ downloads
    async def create_download_job(self, telegram_id: int, url: str) -> dict:
        return await self._request(
            "POST", "/api/downloads/create-job/", json={"telegram_id": telegram_id, "url": url}
        )

    async def get_download(self, download_id: int) -> dict:
        return await self._request("GET", f"/api/downloads/{download_id}/")

    # --------------------------------------------------------- subscriptions
    async def get_active_channels(self) -> list[dict]:
        data = await self._request("GET", "/api/subscriptions/?is_active=true")
        return data.get("results", data) if isinstance(data, dict) else data

    # --------------------------------------------------------------- ads
    async def get_next_ad(self, placement: str, download_count: int = 0) -> Optional[dict]:
        try:
            return await self._request(
                "GET", f"/api/ads/next/?placement={placement}&download_count={download_count}"
            )
        except BackendAPIError:
            return None

    async def register_ad_click(self, ad_id: int) -> None:
        await self._request("POST", f"/api/ads/{ad_id}/register_click/")


backend_client = BackendClient()
