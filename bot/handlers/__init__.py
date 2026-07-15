from aiogram import Router

from . import download, start, subscription


def get_root_router() -> Router:
    root = Router(name="root")
    # Order matters: specific handlers (start, language, subscription-check)
    # must be included before the catch-all link handler.
    root.include_router(start.router)
    root.include_router(subscription.router)
    root.include_router(download.router)
    return root
