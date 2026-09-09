# UpMarket — Video Generation Pipeline

## 1. Overview

Ads longer than a single Wan 2.2 generation are built from **5-second segments** chained by last-frame anchoring, then concatenated and voiced.

```
Product intelligence (qwq)
 → video concept + script (qwq, structured)
 → scene plan: N scenes × ~5s, each with
   {index, duration, visual_prompt, motion_prompt, narration, transition}
 → segment loop (Celery, gpu queue):
     anchor image → Wan 2.2 I2V → 5s clip → extract last frame
 → FFmpeg concat → TTS narration → timing alignment → mix → final MP4
```

Segment duration and total length are configurable (`VIDEO_SEGMENT_DURATION`, default 5s); never hardcode 30s.

## 2. Continuity Model

Each scene declares a `transition` type (decided by QwQ during scene planning):

| Type | Anchor for this segment |
|---|---|
| `CONTINUE` | Last frame of previous segment (default) |
| `TRANSITION` | Last frame of previous segment + transition-aware motion prompt |
| `NEW_SCENE` | Fresh FLUX image (new visual anchor) — only when a hard cut is creatively required or the previous frame is unusable |

Rules:
- **Do not** run FLUX per segment by default — it destroys continuity.
- Segment 1's anchor: FLUX image generated from scene 1's visual prompt (optionally seeded by the real product photo via the img-edit workflow).
- Record for every segment exactly which image/frame was its anchor (auditability + resume).
- Preserve across segments: product appearance, colors, environment, camera perspective, lighting, style.

## 3. Proven Workflow (from repo)

`API/workflow_api.json` = working Wan 2.2 I2V graph, already produced `API/generated_videos/upmarket_df80806f….mp4`:

- Dual `UNETLoader`: `wan_2.2_i2v_high_noise_14B_fp8_scaled` + `wan_2.2_i2v_low_noise_14B_fp8_scaled`, each with `ModelSamplingSD3` and `lightx2v` LoRA (`LoraLoaderModelOnly`)
- `CLIPLoader` (umt5_xxl_fp8) + 2× `CLIPTextEncode` (pos/neg)
- `WanImageToVideo` ← `LoadImage` (node `1`)
- 2× `KSamplerAdvanced` (high-noise steps → low-noise steps)
- `VAEDecode` (wan_2.1_vae) → `CreateVideo` → `SaveVideo` (node `17`, filename_prefix)
- Patch points used by the Flask prototype: node `1` image, `10` positive, `11` negative, `17` filename_prefix

This graph becomes versioned template `wan22_i2v@v1`; patchable inputs declared in a manifest, not scattered node IDs.

## 4. Segment Data Model (target)

`VideoSegment`: campaign FK, index, duration, scene_description, visual_prompt, motion_prompt, narration_text, transition_type, source_image (Asset FK), source_frame (Asset FK), generated_video (Asset FK), final_frame (Asset FK), status, retry_count, workflow_version, generation_metadata (JSON), error_message, timestamps.

Status flow: `PENDING → GENERATING → EXTRACTING_FRAME → DONE | FAILED`.

## 5. Job Orchestration & Resume

- One `video_generation` parent job per campaign video; child steps: script → plan → segment[i] → concat → tts → mix → finalize.
- Runs on the `gpu` Celery queue (concurrency 1). GPU slot is held per segment, not per campaign.
- **Resume rule:** a failed segment retries alone (bounded retries); completed segments are never regenerated. Resume picks up from the first non-DONE step using persisted anchors/frames.
- Frontend states (polled from `GET /jobs/{id}/` every 2.5s — WebSockets are
  deferred, see docs/API.md §5): queued, analyzing, preparing, generating segment i/N, extracting frame, concatenating, generating voice, mixing audio, finalizing, completed, failed.
- Progress derives from real job state — no fake percentages.

## 6. Frame Extraction

FFmpeg (preferred over OpenCV — already required for concat):
```
ffmpeg -sseof -0.1 -i segment_i.mp4 -frames:v 1 -q:v 1 anchor_{i+1}.png
```
Stored as an Asset row linked to the segment.

## 7. Concatenation

Segments are generated with identical width/height/FPS/codec (enforced by workflow template), so concat uses the demuxer without re-encode:
```
ffmpeg -f concat -safe 0 -i list.txt -c copy combined.mp4
```
Fallback (mismatched params): filter_complex concat with re-encode. Record output metadata: width, height, fps, duration, video/audio codec, file size.

## 8. Voice-Over (timing-aware)

```
narration per scene → TTSProvider → per-scene audio
 → measure each duration (ffprobe)
 → align: audio_i must fit scene_i window
     too long → 1) qwq shortens narration, regenerate
                2) or atempo speed-up within 0.9–1.1 limit
                3) or stretch scene boundary if design allows
 → concat audio with padding to scene boundaries
 → mix: ffmpeg -i video -i audio -map 0:v -map 1:a -c:v copy
```
Never hard-cut narration mid-sentence; never overlay a single unsynced audio file.

TTS is a provider interface (`TTS_PROVIDER` env). Default: **edge-tts** (Microsoft neural voices — real Persian via `fa-IR-FaridNeural`, verified). gTTS remains as a fallback engine but does NOT support Persian and validates its language up front. Stronger local TTS / voice cloning can be added later without touching the pipeline.

## 9. Phase 0.5 Prototype (pre-SaaS validation)

Standalone script (reusing `API/app.py` logic — no Django):
```
1 real product photo
 → qwen3-vl describe → qwq 2-scene mini-script
 → FLUX anchor (or product photo directly)
 → Wan 5s → last frame → Wan 5s
 → ffmpeg concat → TTS line → mix
 → final ~10s ad
```
**Go/No-Go gate:** if output quality is not sellable, fix models/workflows before building the SaaS around them.
**Blocker:** ComfyUI models are downloaded but not yet installed on this machine.

## 10. Open Questions (answer during Phase 0.5)

- Wan 2.2 output resolution/FPS sweet spot on this GPU (480p distill LoRA vs quality).
- Real wall-clock time per 5s segment → sets user expectations and queue design.
- Whether Ollama 30B must be unloaded during ComfyUI runs (VRAM).
- Continuity quality after 4+ chained segments — how often NEW_SCENE re-anchoring is needed.
