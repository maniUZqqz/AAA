# UpMarket — AI Architecture

## 1. Provider Abstraction

All AI access goes through one orchestration layer. Nothing else in the codebase may call Ollama or ComfyUI directly.

```
AIOrchestrator
 ├── LLMProvider        (text generation)
 │     └── OllamaProvider
 ├── VisionProvider     (image understanding)
 │     └── OllamaProvider (qwen3-vl)
 ├── ImageProvider      (image generation/edit)
 │     └── ComfyUIProvider (FLUX workflows)
 ├── VideoProvider      (image-to-video)
 │     └── ComfyUIProvider (Wan 2.2 workflows)
 └── TTSProvider        (speech)
       └── pluggable (default: edge-tts Persian neural voice; gTTS fallback — no Persian)
```

Providers are configured, not hardcoded — swapping a model or adding a cloud provider must not touch business logic.

## 2. Model Routing

| Task type | Model | Notes |
|---|---|---|
| REASONING / strategy / scripts / scene planning / objection handling | `qwq:32b` | The "brain". Wrap outputs in strict JSON schemas — QwQ emits `<think>` blocks that must be stripped before parsing |
| VISION / product photo analysis / generated-image validation | `qwen3-vl:30b` | |
| CODE / internal tooling | `qwen3-coder:30b` | Not for marketing text |
| Lightweight code tasks (optional) | `deepseek-coder:6.7b` | |
| IMAGE generation / edit | FLUX.1-dev FP8 via ComfyUI | |
| VIDEO i2v segments | Wan 2.2 (high-noise start / low-noise continuation) + lightx2v LoRA via ComfyUI | |

> **Known defect in current code:** `Main/myproject/Analysis/utils.py` sends marketing/script/caption prompts to `qwen3-coder:30b`. Phase 4 replaces this with the router above.

Config (env): `OLLAMA_BASE_URL`, `OLLAMA_MODEL_REASONING`, `OLLAMA_MODEL_VISION`, `OLLAMA_MODEL_CODER`, `COMFYUI_BASE_URL`, `TTS_PROVIDER`.

## 3. Request Lifecycle

```
caller → orchestrator.run(task_type, prompt_id, inputs)
  → resolve prompt version + model from registry
  → render prompt
  → provider call (timeout, retries w/ backoff)
  → strip reasoning artifacts (<think>…</think>)
  → parse JSON → validate against schema
      on failure: 1 controlled repair attempt → 1 structured retry → FAILED
  → persist AIRequest + AIResponse rows (model, prompt version, latency, outcome)
  → return typed result
```

- Ollama endpoint: `POST {OLLAMA_BASE_URL}/api/generate` (or `/api/chat`), `format: "json"` where schema output is required.
- Timeouts: text 120s default, configurable per task. Retries: 2, exponential backoff.
- Context budget: keep prompts within `OLLAMA_CONTEXT_LENGTH` (8192 default on this hardware); orchestrator truncates/summarizes inputs, never silently overflows.

## 4. Prompt Registry

Every capability has a versioned prompt record: `id`, `version`, `system`, `template`, `expected_schema`, `model`, `params (temperature…)`, `metadata`. Stored in code (`services/ai/prompts/`) with version constants; every AIRequest row records which version ran. Prompt edits = new version.

## 5. Core AI Pipelines

### Product analysis (Phase 5)
```
product data + images
 → qwen3-vl: visual analysis (per image, structured)
 → qwq: strategy synthesis
 → ProductIntelligence JSON:
   {summary, target_audience[], selling_points[], weaknesses[], objections[],
    marketing_angles[], recommended_tone, content_ideas[], use_cases[]}
```
User-provided facts, AI inferences, and external research are stored and labeled separately.

### Sales agent (Phase 7)
```
customer message → intent detection (qwq, structured)
 → retrieve store/product/inventory rows (DB, not model memory)
 → qwq response grounded ONLY in retrieved data
 → action: answer | recommend | handle_objection | create_order | escalate_to_human
```
Hard rule: prices, stock, shipping, policies always come from the database. The model formats; it never invents. Confidence below threshold or policy-sensitive → human handoff state.

### Image studio (Phase 9)
```
product + reference image → qwen3-vl analysis → qwq creative direction
 → prompt → ComfyUI (FLUX workflow, versioned) → output
 → optional qwen3-vl validation (product preserved? logo intact?)
 → Asset row
```
Two distinct task modes: **product-preserving edit** vs **creative composition** — different workflows, different validation strictness.

### Video (Phases 11–13) — see `VIDEO_PIPELINE.md`.

## 6. ComfyUI Integration Layer

`services/comfyui/`:
- `client.py` — upload image, submit workflow (`POST /prompt`), track by polling `/history/{id}` (a ComfyUI WebSocket was not needed: a render takes minutes, so a 2s poll costs nothing and removes a dependency), fetch outputs (`GET /view`), timeout + retry + typed errors including `ComfyUIUnavailable` when the renderer is simply not running. (Port of proven logic in `API/app.py`.)
- `workflows/` — versioned JSON templates: `wan22_i2v@v1` (from `API/workflow_api.json`), `flux_txt2img@v1`, `flux_img_edit@v1` (from `json/`). Each template ships a manifest naming its **patchable inputs** (image, positive, negative, filename_prefix, seed, dimensions) so node IDs live in exactly one place.
- Every submission records: workflow id+version, patched inputs, prompt_id, timing, output files.

## 7. GPU Resource Management

- Single Celery queue `gpu` with worker concurrency = `GPU_CONCURRENCY_LIMIT` (default 1).
- Ollama-only jobs run on a separate `ai` queue (CPU/VRAM-lighter, may allow 2 via `OLLAMA_NUM_PARALLEL`).
- Long pipelines (video) hold the GPU slot per-segment, not for the whole campaign, so smaller jobs can interleave.
- If VRAM pressure appears between Ollama 30B models and ComfyUI: unload Ollama model (`keep_alive: 0`) before heavy ComfyUI stages — decide empirically in Phase 0.5.

## 8. Failure Tracking

`AIRequest` rows carry: task type, model, prompt version, status (OK / TIMEOUT / MALFORMED_OUTPUT / PROVIDER_ERROR / VALIDATION_FAILED), attempt count, latency, error detail. This is the dataset for tuning prompts and spotting flaky capabilities.
