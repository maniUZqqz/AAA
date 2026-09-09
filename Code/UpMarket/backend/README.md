# UpMarket Backend

Unified backend — merges the three legacy pieces (`API/` Flask ComfyUI prototype,
`json/` ComfyUI workflows, `Main/` Django project) into one Django project per
`../ROADMAP.md` and `../docs/`.

## What's inside

| Path | Purpose |
|---|---|
| `apps/accounts` | JWT auth (register / login / refresh / me) |
| `apps/stores` | Store + StoreProfile (brand voice, policies) — tenant boundary |
| `apps/products` | Category / Product / Variant / Attribute / Image CRUD |
| `apps/jobs` | Persistent job records + `/api/v1/jobs/` |
| `apps/ai` | AIRequest/AIResponse audit, ProductIntelligence, analyze pipeline (Celery) |
| `services/ai` | Ollama provider + task→model router + versioned prompts |
| `services/comfyui` | ComfyUI client (ported from Flask prototype) + versioned workflows |
| `services/video` | FFmpeg helpers: last-frame extraction, concat, audio mux, probe |

## Setup (both systems)

> **Easiest path:** run `..\start.bat` — it creates `.env`, installs packages,
> migrates, creates the admin user (admin/admin1234), launches everything and
> health-checks each service. The manual steps below are the equivalent.

```powershell
cd backend
pip install -r requirements.txt
copy .env.example .env      # then edit values
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 0.0.0.0:8000
```

- Swagger UI: http://localhost:8000/api/docs/
- Admin: http://localhost:8000/admin/

## Dev machine (no AI models installed)

Works out of the box with SQLite. AI endpoints return honest errors if Ollama
is unreachable. Run the test suite (all AI calls mocked, ffmpeg tests real):

```powershell
python manage.py test
```

## Main system (models installed)

1. Edit `.env`: set `OLLAMA_BASE_URL` and `COMFYUI_BASE_URL`. (Database is SQLite — nothing to configure.)
2. Start infra: `ollama serve`, ComfyUI, Redis.
3. Start the worker (Windows needs `--pool=solo`):
   ```powershell
   celery -A config worker -l info -Q celery,ai,gpu --pool=solo
   ```
   (No Redis? Set `CELERY_TASK_ALWAYS_EAGER=true` in `.env` for synchronous dev runs.)
4. Start Django: `python manage.py runserver 0.0.0.0:8000`

### Smoke test on the main system (real integration)

Easiest path: run `..\start.bat`, open http://localhost:5173 and walk the UI:

1. ثبت‌نام → ساخت فروشگاه → افزودن محصول → آپلود حداقل یک عکس
2. صفحه محصول → **تحلیل با هوش مصنوعی** (فاز ۵ — qwen3-vl + qwq)
3. **تحلیل بازار و رقبا** با چند خط اطلاعات واقعی رقبا (فاز ۶)
4. **استودیوی تصویر** (فاز ۹ — FLUX): پوستر تبلیغاتی / عکس اینستاگرامی / بهبود عکس
5. **تولید کپشن** برای سه پلتفرم (فاز ۱۰)
6. **استودیوی ویدیو** → تولید سناریو (فاز ۱۱) → 🎥 تولید ویدیو (فاز ۱۲ — Wan 2.2 واقعی،
   قطعه‌به‌قطعه با پیوستگی فریم آخر؛ پیشرفت قطعه i/N را نشان می‌دهد و آخرش پلیر ویدیو)
   → 🔊 صداگذاری (فاز ۱۳ — gTTS فارسی، نیازمند اینترنت)
7. صفحه فروشگاه → **💬 چت فروش** (فاز ۷): سؤال محصول، موجودی، «می‌خوامش» → سفارش
   پیش‌نویس، و «شکایت دارم» → ارجاع به انسان
8. صفحه فروشگاه → **📣 کمپین‌ها** (فاز ۱۴/۱۵): ساخت کمپین از محتوای تولیدشده →
   تأیید → 🚀 انتشار با n8n (نیازمند `N8N_WEBHOOK_URL` در `.env` و اجرای n8n)
9. صفحه فروشگاه → **📈 آمار** (فاز ۱۶): KPIها و روند ۱۴ روزه — همه از داده واقعی

## Production notes (Phase 17)

- Set `DJANGO_DEBUG=false` + a long random `DJANGO_SECRET_KEY` + explicit
  `DJANGO_ALLOWED_HOSTS` and `CORS_ALLOWED_ORIGINS`.
- Rate limits via `THROTTLE_ANON` / `THROTTLE_USER`; upload cap via `MAX_UPLOAD_MB`.
- Behind HTTPS enable `SECURE_SSL_REDIRECT` / `SESSION_COOKIE_SECURE` /
  `CSRF_COOKIE_SECURE` / `SECURE_HSTS_SECONDS` (see `.env.example`).
- Verify with: `python manage.py check --deploy` (remaining warnings are the
  SSL flags above — intentional on plain-HTTP LAN deployments).

> اگر ComfyUI روی گراف‌های FLUX خطای validation داد، راهنمای
> `services/comfyui/workflows/ui_reference/README.md` را ببین (خروجی API-format از خود ComfyUI).

API-level equivalent:

```powershell
# auth:    POST /api/v1/auth/register/  →  POST /api/v1/auth/login/
# store:   POST /api/v1/stores/          product: POST /api/v1/products/
# image:   POST /api/v1/products/{id}/images/        (multipart, field: image)
# AI:      POST /api/v1/products/{id}/analyze/        → GET /api/v1/jobs/{job_id}/
#          GET  /api/v1/products/{id}/intelligence/
# market:  POST /api/v1/products/{id}/market-analysis/ {research_inputs}
# image:   POST /api/v1/products/{id}/image-studio/ {kind: POSTER|PRODUCT_SHOT|ENHANCED}
# caption: POST /api/v1/products/{id}/captions/ {platforms, tone}
# script:  POST /api/v1/products/{id}/video-script/ {duration}
# video:   POST /api/v1/video-scripts/{id}/generate/   (needs ComfyUI + wan22 models)
# voice:   POST /api/v1/video-scripts/{id}/voice/      (after final video; needs internet for gTTS)
# chat:    POST /api/v1/stores/{id}/chat/ {message}
# campaign: POST /api/v1/campaigns/ → /approve/ → /publish/ {platforms:["instagram"]}
```

### ComfyUI workflows

- `services/comfyui/workflows/wan22_i2v_v1.json` — **proven** Wan 2.2 I2V graph
  (from the old Flask prototype). Patch inputs by name via
  `services.comfyui.workflows.load_workflow / patch_workflow`.
- FLUX workflows exist only as UI-format references — **export them as API format
  on the main system** (see `services/comfyui/workflows/ui_reference/README.md`).

Quick real ComfyUI check (Django shell on the main system):

```python
from services.comfyui.client import ComfyUIClient
from services.comfyui.workflows import load_workflow, patch_workflow
client = ComfyUIClient()
name = client.upload_image("path/to/test.jpg")
graph, manifest = load_workflow("wan22_i2v", "v1")
graph = patch_workflow(graph, manifest, image=name,
                       positive="cinematic natural movement", negative="blurry",
                       filename_prefix="upmarket/smoke")
print(client.generate(graph, "media/generated"))   # → local mp4 path
```

## Frontend

The React dashboard lives in `../frontend/` (see its README). In dev it proxies
`/api` and `/media` to this backend at `http://localhost:8000`.

## Known limitations (current phase)

- Real Ollama/ComfyUI integration is **not yet exercised on the dev machine**
  (models live on the main system) — the smoke tests above are the verification.
- Sales agent, image studio, video pipeline orchestration, campaigns, n8n:
  later phases per `../ROADMAP.md`.
