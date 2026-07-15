# Before you launch this for real

This scaffold implements every module from the spec end-to-end and will run
with `docker compose up`, but a handful of things are deliberately left as
extension points rather than fully certified for you, because they depend on
credentials, legal terms, or infra choices only you can make:

## Must do before production

1. **ACRCloud project** — sign up, create a Music Recognition project, and
   put real `ACRCLOUD_HOST` / `ACRCLOUD_ACCESS_KEY` / `ACRCLOUD_ACCESS_SECRET`
   in `.env`. The client in `services/music_recognition.py` follows their
   documented HMAC-SHA1 signing scheme.
2. **Platform ToS** — TikTok/Instagram/YouTube's terms restrict automated
   downloading; confirm your use case (personal archiving vs. redistribution)
   is compliant in your jurisdiction, and consider rate limits so you don't
   get the source IP blocked.
3. **Bot must be admin in required channels** — `getChatMember` only works if
   the bot itself is a member (ideally admin) of every channel in
   `RequiredChannel`.
4. **File storage growth** — downloaded videos accumulate in the
   `downloads_data` volume. Add a Celery beat schedule to delete files older
   than N hours once delivered (there's a natural hook in
   `downloads/tasks.py` after the video is sent, or as a periodic task).
5. **Payments** — `Advertisement`/premium fields are modeled and the
   `is_premium` flag is respected (HD quality, higher limits), but no payment
   provider is wired up. Telegram Payments is the fastest to add (a few
   handlers in `bot/handlers/`); Click/Payme/Stripe each need their own
   webhook endpoints in a new `payments` Django app.
6. **HTTPS + real domain** — `nginx.conf` is HTTP-only for local dev; add a
   TLS-terminating config (or put this behind Cloudflare/Caddy) before going
   live, since Telegram requires HTTPS for webhooks (not needed for polling
   mode, which is what `bot/main.py` uses by default).
7. **Secrets** — rotate `DJANGO_SECRET_KEY` and `DJANGO_INTERNAL_API_TOKEN`,
   and never commit a real `.env`.
8. **Horizontal scaling** — bot currently runs long-polling (`start_polling`),
   which only supports one instance. For multiple bot replicas, switch to
   webhook mode (aiogram supports this) behind nginx.
9. **Tests** — none are included in this scaffold; the cleanest seams to
   start with are `services/*.py` (pure functions/classes, no Django) and the
   DRF viewsets (`APITestCase` + `factory_boy`).
10. **Monitoring** — hook up Sentry (or similar) in both `backend/config/settings.py`
    and `bot/main.py`; the current logging setup is console-only.
