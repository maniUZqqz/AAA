# UpMarket — System Architecture

> Phase 0 deliverable. Source of truth for system-level decisions. See `../ROADMAP.md` for the full product spec and phase plan.
>
> **Status update 2026-08-27:** the legacy audit in §2 is historical — `API/`, `json/`, `Main/` were merged into `backend/` and deleted; every gap in §5 has since been closed (JWT auth, tenancy, Celery jobs, model routing, versioned workflows, env config, 85 tests). Current per-phase status lives in `../ROADMAP.md` §۵.

## 1. What UpMarket Is

An **AI Sales & Marketing Employee** for online stores: store + product catalog → AI product/market intelligence → AI sales chat → AI content generation (posters, product photos, captions, segmented video with voice-over) → approval → publishing via n8n → analytics.

## 2. Current Repository State (audited 2026-08-27)

| Location | What it is | Verdict |
|---|---|---|
| `API/app.py` | Flask service that drives ComfyUI Wan 2.2 I2V: upload image → patch workflow JSON → queue → poll `/history` → download video. **Produced a real video** (`API/generated_videos/upmarket_*.mp4`). | **Proven integration logic — port into Django service layer (Phase 8). Keep as reference.** |
| `API/workflow_api.json`, `json/wan22_14B_i2v_simple (1).json` | Working Wan 2.2 I2V ComfyUI workflow (dual UNET high/low noise, lightx2v LoRA, umt5 CLIP, wan2.1 VAE, WanImageToVideo, 2× KSamplerAdvanced, CreateVideo/SaveVideo). Patch points: node `1` (LoadImage), `10`/`11` (pos/neg prompts), `17` (filename prefix). | **Seed for the versioned workflow system.** |
| `json/First image (3).json`, `json/First_image_edit_with_input (1).json` | FLUX text-to-image and image-edit workflows (KSampler, FluxGuidance, LoadImage+VAEEncode for img2img). | **Seed workflows for Image Studio (Phase 9).** |
| `API/Analysis/StartAnalysis.py` | Flask prototype UI (store/post forms, **simulated/mock** processing). | Superseded. Reference only — contains no real AI calls. |
| `Main/myproject/` | Django project. `Analysis` app has real models (`Store`, `Product`, `ProductFeature`, `ProductImage`, `ProductAnalysis`), DRF viewsets, and a working synchronous Ollama call (`utils.ask_ollama`). `SupportChat`, `ContentProduction`, `HomePage` are empty scaffolds. | Models/serializers are a useful starting point. Must be restructured (see §5 gaps). |
| `Main/myproject/front/SaveData.html` | Static HTML test frontend. | Superseded by React (Phase 1). |

## 3. Target Architecture

```
React (Vite + TS + Tailwind)  ──────── REST ────────►  Django + DRF
        (job progress is polled; see docs/API.md §5)
                                                          │
                              ┌────────────── service layer (no logic in views)
                              │
        ┌──────────┬──────────┼──────────────┬───────────────┐
        ▼          ▼          ▼              ▼               ▼
   SQLite       Redis      Celery       AI Orchestrator   Media Storage
                             │               │              (local → S3-ready)
                     GPU job queue     ┌─────┴─────┐
                     (concurrency=1)   ▼           ▼
                                    Ollama      ComfyUI
                                 qwq / vl /   FLUX / Wan 2.2
                                  coder            │
                                              FFmpeg / TTS
                                                   │
                                              n8n webhooks → social platforms
```

### Service boundaries (Django apps / domains)

- `accounts` — users, JWT auth, profiles
- `stores` — Store, StoreProfile, brand voice, policies (tenant boundary)
- `products` — Product, Category, Variant, Image, inventory, pricing
- `customers` — customers, conversations, messages, orders/cart (sales agent domain)
- `ai` — providers, router, prompt registry, AIRequest/AIResponse records
- `content` — generated assets (image, caption, script, video segment, final video, audio)
- `campaigns` — campaign grouping + approval state machine
- `jobs` — generic job records (state, progress, retry, resume)
- `publishing` — n8n webhook delivery, status, retries
- `analytics` — (late phase) performance data

Cross-cutting `services/` layer: `services/ai/` (Ollama), `services/comfyui/`, `services/video/` (FFmpeg, frame extraction), `services/audio/` (TTS), `services/publishing/`.

## 4. Key Architectural Rules

1. **No business logic in views** — views validate/authorize, services do work.
2. **All AI calls go through the orchestrator** — no direct `requests.post` to Ollama/ComfyUI in app code.
3. **All heavy generation runs in Celery** — HTTP requests never block on GPU work.
4. **GPU is a scarce resource** — dedicated Celery queue with concurrency 1 (configurable via `GPU_CONCURRENCY_LIMIT`).
5. **Everything generated is an Asset row** — no orphan files on disk.
6. **Tenant isolation enforced in querysets/permissions** — never frontend-only.
7. **Configuration via environment** — `OLLAMA_BASE_URL`, `COMFYUI_BASE_URL`, `DATABASE_URL`, `REDIS_URL`, `N8N_WEBHOOK_URL`, `GPU_CONCURRENCY_LIMIT`, `VIDEO_SEGMENT_DURATION`, `TTS_PROVIDER`, model names.
8. **Structured AI output** — JSON schema per capability, validate + repair + retry, never parse free prose for machine steps.

## 5. Gaps Between Current Code and Target

| Gap | Current | Target |
|---|---|---|
| Auth | `AllowAny` everywhere; auto-creates `testuser/123456` | JWT (SimpleJWT), per-store permissions |
| Tenancy | Any client sees all stores | Owner-scoped querysets |
| AI routing | `qwen3-coder:30b` used for marketing/scripts/captions (wrong model) | `qwq:32b` reasoning, `qwen3-vl:30b` vision, coder only for code tasks |
| AI calls | Synchronous inside HTTP request (`ProductAnalysisView`) | Celery jobs + polled job progress (WebSockets deferred — docs/API.md §5) |
| AI output | Free-text `TextField`s | Structured JSON, validated, versioned prompts |
| ComfyUI | Flask script, blocking poll loop, hardcoded node IDs | Django service, versioned workflows, job tracking |
| Secrets | `SECRET_KEY` in source, `CORS_ALLOW_ALL_ORIGINS=True` | `.env`, explicit CORS |
| Tests | None | Per-phase test requirement (see DEVELOPMENT_RULES.md) |
| Frontend | Static HTML | React + Vite + TS + Tailwind |

## 6. Error Handling Strategy

- Every external service (Ollama, ComfyUI, Redis, n8n, TTS, storage) gets: timeout, bounded retries with backoff, typed exceptions, job `FAILED` state with stored error, user-facing plain-language error.
- Video segment failure → retry that segment only; campaign resumes from failed step (see VIDEO_PIPELINE.md).
- No infinite retries; no silent fallbacks to fake data.

## 7. Logging / Observability

Structured logs (JSON in production) with: request id, user id, store id, job id, model, workflow version, duration, outcome. AIRequest/AIResponse tables store every AI call (prompt version, model, latency, token counts where available, success/failure). Never log secrets.

## 8. Testing Strategy

- Backend: pytest + pytest-django. Unit tests for services (AI mocked), API tests for permissions/tenancy, integration tests against real local Ollama/ComfyUI marked `@integration` (run manually when services are up).
- Frontend: vitest + testing-library for critical flows; `npm run build` must pass.
- A phase is complete only when its real integration was exercised at least once (see DEVELOPMENT_RULES.md).

## 9. Security Baseline

JWT auth, per-object permission checks, upload validation (type/size/name), safe generated filenames (UUID), media served per-tenant, `.env` secrets, explicit CORS origins, rate limiting on AI endpoints, n8n webhook signed/secret-token.

## 10. Architectural Decisions Requiring Approval (before Phase 1)

| # | Decision | Recommendation |
|---|---|---|
| D1 | Rebuild backend fresh in `backend/` (new Django project, proper config/env/service layout), porting the existing `Analysis` models — vs. refactoring `Main/myproject` in place | **Fresh `backend/`**; current project has structural debt (naming, empty apps, settings) that costs more to unwind than to port |
| D2 | Database | **SQLite (Django default)** — revised 2026-08-27 per owner decision: zero-setup on both machines; ORM stays engine-agnostic so PostgreSQL can be swapped in later if concurrent load demands it |
| D3 | Auth | **JWT via djangorestframework-simplejwt** |
| D4 | Frontend | **New React + Vite + TypeScript + Tailwind app in `frontend/`** |
| D5 | Model routing | **qwq:32b = reasoning/strategy/scripts, qwen3-vl:30b = vision, qwen3-coder:30b = code-only tasks** (fixes current misuse) |
| D6 | Flask `API/` | Keep as read-only reference; port ComfyUI client logic to Django in Phase 8; retire Flask after |
| D7 | Video continuity | Last-frame anchoring by default; FLUX re-anchor only on `NEW_SCENE` decided by QwQ |
| D8 | GPU concurrency | **1** heavy job at a time initially, configurable |
| D9 | Phase 0.5 prototype | Standalone script reusing `API/app.py` logic + Ollama; **blocked until ComfyUI models are installed on this machine** |
| D10 | Content language | Persian-first UI and generated content, architecture language-agnostic |

## 11. Top Risks

1. **ComfyUI models not present on this machine yet** — blocks Phase 0.5 and Phases 8–13. Highest-priority logistics item.
2. **Output quality** — whether Wan 2.2 + FLUX on this hardware produce sellable content; that is exactly what Phase 0.5 answers before major investment.
3. **GPU contention** — Ollama 30B models and ComfyUI generation competing for VRAM; mitigate with job queue + model unloading between stages if needed.
4. **Long generation times** — a 30s video = 6 segments; UX must communicate honestly via job states.
5. **Continuity quality** — last-frame anchoring degrades over many segments; QwQ scene planner must know when to re-anchor.
6. **QwQ structured output reliability** — reasoning models can ramble; enforce JSON schema + repair + retry.
