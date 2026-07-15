# Internal API Reference

All endpoints are served by the Django backend at `BACKEND_BASE_URL`
(default `http://django_backend:8000`). Every endpoint below (except the ad
redirect) requires:

```
Authorization: Bearer <DJANGO_INTERNAL_API_TOKEN>
```

This is a shared secret between the bot process and the backend — it is
**not** a per-user token and should never be exposed to end users.

## Users

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/users/register-or-touch/` | Upsert a Telegram user, bump `last_activity_at`. Called on every update. |
| GET | `/api/users/` | List/search users (admin dashboard). |
| POST | `/api/users/{id}/block/` | Block a user. |
| POST | `/api/users/{id}/unblock/` | Unblock a user. |

## Downloads

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/downloads/create-job/` | Enforces daily limits, creates a `VideoDownload`, enqueues the Celery pipeline. Returns `202` with the row (status=`pending`/`downloading`). |
| GET | `/api/downloads/{id}/` | Poll status. Terminal states: `done`, `failed`. Includes nested `recognition` once available. |
| GET | `/api/downloads/` | List (admin dashboard), filterable by `platform`, `status`, `user`. |

## Subscriptions (mandatory channel gate)

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/subscriptions/?is_active=true` | Channels the bot should show in the "please subscribe" keyboard. |
| POST/PUT/DELETE | `/api/subscriptions/{id}/` | Admin CRUD. |

Real membership is checked bot-side via Telegram's `getChatMember`, since
that requires the bot token and can't be done from Django.

## Advertisements

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/ads/next/?placement=before_video&download_count=N` | Returns the best currently-running ad for that slot (or `204`), and atomically increments its view counter. |
| GET | `/api/ads/{id}/redirect/` | **Public, unauthenticated.** This is the literal URL used as the Telegram inline button; increments `clicks` then 302s to the real `button_url`. |
| CRUD | `/api/ads/` | Admin management. |

## Statistics

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/stats/dashboard/` | Single aggregate payload: user counts, download counts (today/week/month), per-platform breakdown, music-recognition success rate. |
| GET | `/api/stats/downloads-timeseries/?days=30` | Daily download counts for the chart. |
| GET | `/api/stats/user-growth/?days=30` | Daily new-user counts for the chart. |

## Download pipeline status values

`pending` → `downloading` → `recognizing` → `done` (or `failed` at any point,
with `error_message` populated).
