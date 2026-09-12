"""Celery tasks for the content domain.

Caption/script tasks run on the `ai` queue; video generation runs on the `gpu`
queue with concurrency 1 (see settings.CELERY_TASK_ROUTES).
"""
import logging
import random
from pathlib import Path

from celery import shared_task
from django.conf import settings

from apps.ai.models import AIRequest, ProductIntelligence
from apps.ai.services import recorded_json_call
from apps.jobs.models import Job
from apps.products.models import Product
from services import gpu
from apps.billing import services as billing
from apps.billing.models import Usage
from services.ai import providers
from services.ai.gateway import text_provider
from services.ai.prompts import captions as caption_prompts
from services.ai.prompts import image_studio as image_prompts
from services.ai.prompts import video_script as script_prompts
from services.ai.router import TASK_REASONING, models_for
from services.audio.tts import get_tts_provider
from services.comfyui.client import ComfyUIClient
from services.comfyui.workflows import load_workflow, patch_workflow
from services.imaging.preprocess import prepare_source_image
from services.video.ffmpeg import (
    concat_audio,
    concat_videos,
    extract_last_frame,
    fit_audio,
    make_silence,
    mix_audio,
    probe_duration,
)

from .models import Caption, GeneratedImage, VideoScene, VideoScript, VideoSegment

logger = logging.getLogger(__name__)

NEGATIVE_PROMPT = (
    "blurry, low quality, distorted, deformed, text, letters, words, writing, "
    "typography, captions, arabic script, gibberish letters, watermark, logo overlay"
)
WAN_FPS = 16


def _media_rel(path: Path) -> str:
    """Path under MEDIA_ROOT → relative name usable in a FileField."""
    return str(Path(path).resolve().relative_to(Path(settings.MEDIA_ROOT).resolve())).replace(
        "\\", "/"
    )


def _caption_subject(product, image_id, video_script_id):
    """Resolve the content item this caption is about (beter.md #11)."""
    about_image = about_video = None
    subject = None
    if image_id:
        about_image = GeneratedImage.objects.filter(product=product, id=image_id).first()
        if about_image:
            subject = {
                "type": "image",
                "kind": about_image.kind,
                "concept": about_image.concept,
                "style": about_image.style,
                "instructions": about_image.instructions,
            }
    elif video_script_id:
        about_video = (
            VideoScript.objects.filter(product=product, id=video_script_id)
            .prefetch_related("scenes")
            .first()
        )
        if about_video:
            subject = {
                "type": "video",
                "concept": about_video.concept,
                "cta": about_video.cta,
                "duration": about_video.total_duration,
                "narrations": [
                    s.narration for s in about_video.scenes.all() if s.narration.strip()
                ],
            }
    return about_image, about_video, subject


@shared_task(bind=True)
def generate_captions_task(
    self, job_id, product_id, platforms, tone="", objective="", image_id=None, video_script_id=None
):
    job = Job.objects.get(id=job_id)
    try:
        product = (
            Product.objects.select_related("store").prefetch_related("attributes").get(id=product_id)
        )
        intelligence = ProductIntelligence.objects.filter(product=product).first()
        requested = [p for p in (platforms or []) if p in caption_prompts.PLATFORMS] or [
            "INSTAGRAM",
            "TELEGRAM",
            "LINKEDIN",
        ]
        about_image, about_video, subject = _caption_subject(product, image_id, video_script_id)
        job.total_steps = 1
        job.mark_running("در حال نوشتن کپشن‌ها")
        reasoning_models = models_for(TASK_REASONING)
        gpu.before_ollama_work(reasoning_models[0])

        provider = text_provider(product.store)
        parsed, request_row = recorded_json_call(
            job=job,
            store=product.store,
            task_type=AIRequest.TaskType.REASONING,
            prompt_id=caption_prompts.CAPTIONS_PROMPT_ID,
            prompt_version=caption_prompts.CAPTIONS_PROMPT_VERSION,
            provider=provider,
            models=reasoning_models,
            prompt=caption_prompts.build_captions_prompt(
                product, intelligence, requested, tone, objective, subject
            ),
            system=caption_prompts.CAPTIONS_SYSTEM,
            # validated inside the call: an incomplete answer moves on to the
            # next installed model instead of failing the job
            validate=lambda parsed: caption_prompts.validate_captions(parsed, set(requested)),
            validation_message="خروجی کپشن ناقص بود",
        )

        created_ids = []
        for item in parsed["captions"]:
            caption = Caption.objects.create(
                store=product.store,
                product=product,
                platform=item["platform"],
                tone=tone,
                objective=objective,
                short_text=item["short"],
                medium_text=item["medium"],
                long_text=item["long"],
                hashtags=item["hashtags"],
                cta=item["cta"],
                about_image=about_image,
                about_video=about_video,
                source_request=request_row,
            )
            created_ids.append(caption.id)

        if created_ids:
            billing.commit(
                billing.reserve(
                    product.store, Usage.Metric.CAPTIONS, len(created_ids), job=job,
                    detail=f"product {product.id}",
                    external=not providers.uses_own_gpu(providers.TEXT),
                )
            )

        job.mark_progress(1, "")
        job.mark_completed({"caption_ids": created_ids})
        return {"caption_ids": created_ids}
    except Exception as exc:  # noqa: BLE001
        logger.exception("Caption job %s failed", job_id)
        job.mark_failed(exc)
        return {"error": str(exc)}


@shared_task(bind=True)
def generate_video_script_task(self, job_id, product_id, total_duration=30, objective="", language="fa"):
    job = Job.objects.get(id=job_id)
    try:
        product = (
            Product.objects.select_related("store").prefetch_related("attributes").get(id=product_id)
        )
        intelligence = ProductIntelligence.objects.filter(product=product).first()
        segment_duration = settings.UPMARKET_AI["VIDEO_SEGMENT_DURATION"]
        job.total_steps = 1
        job.mark_running("در حال نوشتن سناریوی ویدیو")
        reasoning_models = models_for(TASK_REASONING)
        gpu.before_ollama_work(reasoning_models[0])

        provider = text_provider(product.store)
        parsed, request_row = recorded_json_call(
            job=job,
            store=product.store,
            task_type=AIRequest.TaskType.REASONING,
            prompt_id=script_prompts.VIDEO_SCRIPT_PROMPT_ID,
            prompt_version=script_prompts.VIDEO_SCRIPT_PROMPT_VERSION,
            provider=provider,
            models=reasoning_models,
            prompt=script_prompts.build_video_script_prompt(
                product, intelligence, int(total_duration), segment_duration, objective, language
            ),
            system=script_prompts.VIDEO_SCRIPT_SYSTEM,
            validate=lambda parsed: script_prompts.validate_video_script(
                parsed, segment_duration
            ),
            validation_message="سناریوی ویدیو ناقص بود",
        )

        script = VideoScript.objects.create(
            store=product.store,
            product=product,
            concept=str(parsed.get("concept", "")),
            objective=objective,
            cta=str(parsed.get("cta", "")),
            total_duration=sum(s["duration"] for s in parsed["scenes"]),
            narration_language=language if language in {"fa", "en"} else "fa",
            raw=parsed,
            source_request=request_row,
        )
        for scene in parsed["scenes"]:
            VideoScene.objects.create(script=script, **scene)

        job.mark_progress(1, "")
        job.mark_completed({"script_id": script.id, "scene_count": len(parsed["scenes"])})
        return {"script_id": script.id}
    except Exception as exc:  # noqa: BLE001
        logger.exception("Video script job %s failed", job_id)
        job.mark_failed(exc)
        return {"error": str(exc)}


IMAGE_DIMENSIONS = {
    "POSTER": (832, 1216),  # portrait 2:3-ish for feed/poster
    "PRODUCT_SHOT": (1024, 1024),
    "ENHANCED": (1024, 1024),
}
# All kinds edit the REAL product photo when one exists (beter.md #4: the
# generated product must be OUR product, not an invented one). POSTER keeps a
# higher denoise for creative composition while the product stays anchored.
EDIT_DENOISE = {"ENHANCED": 0.45, "PRODUCT_SHOT": 0.7, "POSTER": 0.75}


@shared_task(bind=True)
def generate_image_task(self, job_id, product_id, kind, style="", instructions="", source_image_id=None):
    """Image Studio (Phase 9): QwQ creative direction → FLUX via ComfyUI."""
    job = Job.objects.get(id=job_id)
    try:
        product = (
            Product.objects.select_related("store")
            .prefetch_related("attributes", "images")
            .get(id=product_id)
        )
        if kind not in GeneratedImage.Kind.values:
            raise RuntimeError(f"نوع تصویر نامعتبر: {kind}")
        intelligence = ProductIntelligence.objects.filter(product=product).first()
        job.total_steps = 2
        job.mark_running("در حال طراحی کانسپت تصویر")
        reasoning_models = models_for(TASK_REASONING)
        gpu.before_ollama_work(reasoning_models[0])

        provider = text_provider(product.store)
        parsed, request_row = recorded_json_call(
            job=job,
            store=product.store,
            task_type=AIRequest.TaskType.REASONING,
            prompt_id=image_prompts.IMAGE_PROMPT_ID,
            prompt_version=image_prompts.IMAGE_PROMPT_VERSION,
            provider=provider,
            models=reasoning_models,
            prompt=image_prompts.build_image_prompt(product, intelligence, kind, style, instructions),
            system=image_prompts.IMAGE_SYSTEM,
            validate=image_prompts.validate_image,
            validation_message="طراحی کانسپت تصویر ناقص بود",
        )

        source_image = None
        if source_image_id:
            source_image = product.images.filter(id=source_image_id).first()
        if source_image is None and kind in EDIT_DENOISE:
            source_image = product.images.first()
        use_edit = kind in EDIT_DENOISE and source_image is not None

        job.mark_progress(1, "در حال تولید تصویر با FLUX")
        # reserved now, committed only if a file actually lands on disk
        quota = billing.reserve(
            product.store, Usage.Metric.IMAGES, 1, job=job,
            detail=f"{kind} · product {product.id}",
            external=not providers.uses_own_gpu(providers.IMAGE),
        )
        gpu.before_comfyui_work()  # evict Ollama models so FLUX has the VRAM
        client = ComfyUIClient()
        out_dir = Path(settings.MEDIA_ROOT) / "generated" / "images"
        width, height = IMAGE_DIMENSIONS[kind]
        # the model's negatives PLUS our hard text ban (Persian text is drawn by code)
        negative = ", ".join(
            part for part in [parsed["negative_en"], NEGATIVE_PROMPT] if part
        )
        seed = random.randint(1, 2**31)
        prefix = f"upmarket/images/product_{product.id}"

        if use_edit:
            graph, manifest = load_workflow("flux_img_edit", "v1")
            # img2img inherits the input's quality, so the owner's phone photo
            # is upscaled/normalised first instead of being blown up by the
            # sampler (beter.md v2 #4)
            prepared = prepare_source_image(
                source_image.image.path,
                Path(settings.MEDIA_ROOT) / "generated" / "sources"
                / f"product_{product.id}_src_{source_image.id}_{width}x{height}.png",
                width,
                height,
            )
            uploaded = client.upload_image(prepared)
            patched = patch_workflow(
                graph,
                manifest,
                image=uploaded,
                positive=parsed["prompt_en"],
                negative=negative,
                seed=seed,
                denoise=EDIT_DENOISE[kind],
                width=width,
                height=height,
                filename_prefix=prefix,
            )
            workflow_version = "flux_img_edit@v1"
        else:
            graph, manifest = load_workflow("flux_txt2img", "v1")
            patched = patch_workflow(
                graph,
                manifest,
                positive=parsed["prompt_en"],
                negative=negative,
                seed=seed,
                width=width,
                height=height,
                filename_prefix=prefix,
            )
            workflow_version = "flux_txt2img@v1"

        image_path = client.generate(patched, out_dir)

        # beter.md #4b: Persian text is NEVER left to the diffusion model —
        # for posters the real headline/price is drawn by code (Pillow + RTL).
        overlay_meta = {}
        if kind == GeneratedImage.Kind.POSTER:
            headline = parsed.get("headline_fa") or product.name
            subline = parsed.get("subline_fa") or ""
            try:
                from services.imaging.text_overlay import add_poster_text, format_price_fa

                badge = format_price_fa(product.price, product.currency)

                overlaid = Path(image_path).with_name(Path(image_path).stem + "_text.png")
                add_poster_text(image_path, overlaid, headline, subline, badge)
                image_path = overlaid
                overlay_meta = {
                    "text_overlay": {"headline": headline, "subline": subline, "badge": badge}
                }
            except Exception as exc:  # the poster is still usable without text
                logger.warning("Poster text overlay failed: %s", exc)
                overlay_meta = {"text_overlay_error": str(exc)[:300]}

        generated = GeneratedImage.objects.create(
            store=product.store,
            product=product,
            kind=kind,
            concept=parsed["concept_fa"],
            prompt_en=parsed["prompt_en"],
            negative_en=negative,
            style=style,
            instructions=instructions,
            source_image=source_image if use_edit else None,
            workflow_version=workflow_version,
            source_request=request_row,
            metadata={"seed": seed, "width": width, "height": height, **overlay_meta},
        )
        generated.image.name = _media_rel(image_path)
        generated.save()

        billing.commit(quota)  # a real file exists — now it counts
        job.mark_progress(2, "")
        job.mark_completed({"image_id": generated.id, "image_url": generated.image.url})
        return {"image_id": generated.id}
    except Exception as exc:  # noqa: BLE001
        logger.exception("Image generation job %s failed", job_id)
        billing.release(locals().get("quota"), reason=type(exc).__name__)
        job.mark_failed(exc)
        return {"error": str(exc)}


@shared_task(bind=True)
def generate_voice_task(self, job_id, script_id):
    """Voice-over (Phase 13): per-scene TTS → timing-aware alignment → mix onto video."""
    job = Job.objects.get(id=job_id)
    try:
        script = VideoScript.objects.select_related("product", "store").get(id=script_id)
        if not script.final_video:
            raise RuntimeError("اول باید ویدیوی نهایی تولید شده باشد.")
        scenes = list(script.scenes.all())
        if not any(scene.narration.strip() for scene in scenes):
            raise RuntimeError("هیچ‌کدام از صحنه‌ها نریشن ندارند.")
        # align narration to the ACTUAL generated segment durations (Wan produces
        # duration + 1/16s per segment), so audio never drifts or truncates video
        done_segments = {
            s.index: s for s in script.segments.filter(status=VideoSegment.Status.DONE)
        }

        # the voice must match the language the narration was written in, and
        # the store must allow the narration text to reach an external voice
        tts = get_tts_provider(
            language=script.narration_language or "fa", store=script.store,
        )
        out_dir = Path(settings.MEDIA_ROOT) / "generated" / "audio" / f"script_{script.id}"
        out_dir.mkdir(parents=True, exist_ok=True)
        job.total_steps = len(scenes) + 2
        job.mark_running("در حال تولید صدا")

        warnings = []
        scene_clips = []
        for step, scene in enumerate(scenes, start=1):
            job.mark_progress(step, f"صداگذاری صحنه {scene.index} از {len(scenes)}")
            fitted = out_dir / f"scene_{scene.index}.m4a"
            segment = done_segments.get(scene.index)
            target_duration = scene.duration
            if segment is not None and segment.video:
                try:
                    target_duration = probe_duration(segment.video.path)
                except Exception:  # fall back to the planned duration
                    target_duration = scene.duration
            if scene.narration.strip():
                raw_clip = tts.synthesize(scene.narration, out_dir / f"scene_{scene.index}_raw.mp3")
                raw_duration = probe_duration(raw_clip)
                if raw_duration > target_duration * 1.25:
                    warnings.append(
                        f"نریشن صحنه {scene.index} ({raw_duration:.1f}s) از پنجره صحنه بلندتر است و کوتاه شد"
                    )
                fit_audio(raw_clip, fitted, target_duration)
            else:
                make_silence(target_duration, fitted)
            scene_clips.append(fitted)

        job.mark_progress(len(scenes) + 1, "در حال ترکیب صدا با ویدیو")
        voice_path = concat_audio(scene_clips, out_dir / "voice.m4a")
        voiced_path = mix_audio(
            Path(script.final_video.path), voice_path, out_dir.parent.parent / "videos" /
            f"script_{script.id}" / "final_voiced.mp4"
        )

        script.voice_audio.name = _media_rel(voice_path)
        script.final_video_voiced.name = _media_rel(voiced_path)
        script.save(update_fields=["voice_audio", "final_video_voiced", "updated_at"])

        job.mark_progress(len(scenes) + 2, "")
        job.mark_completed(
            {
                "script_id": script.id,
                "voiced_video": script.final_video_voiced.url,
                "warnings": warnings,
            }
        )
        return {"script_id": script.id, "warnings": warnings}
    except Exception as exc:  # noqa: BLE001
        logger.exception("Voice job %s failed", job_id)
        job.mark_failed(exc)
        return {"error": str(exc)}


def _flux_anchor(client, scene, out_dir):
    """Generate a fresh FLUX anchor image for a NEW_SCENE cut (video resolution)."""
    graph, manifest = load_workflow("flux_txt2img", "v1")
    patched = patch_workflow(
        graph,
        manifest,
        positive=scene.visual_prompt,
        negative=NEGATIVE_PROMPT,
        seed=random.randint(1, 2**31),
        width=832,
        height=480,
        filename_prefix=f"upmarket/anchors/scene_{scene.index}",
    )
    return client.generate(patched, out_dir, filename=f"anchor_{scene.index}.png")


def _anchor_for_segment(scene, previous_frame_path, product_image_path, segment, client, out_dir):
    """Choose the real anchor image for a segment, recording its origin."""
    if scene.index == 1 or previous_frame_path is None:
        segment.anchor_source = "product_image"
        return product_image_path
    if scene.transition == VideoScene.Transition.NEW_SCENE:
        try:
            anchor = _flux_anchor(client, scene, out_dir)
            segment.anchor_source = "flux_new_scene"
            return anchor
        except Exception as exc:  # degrade honestly, keep the pipeline going
            logger.warning("NEW_SCENE FLUX anchor failed, using previous frame: %s", exc)
            segment.anchor_source = "previous_frame (NEW_SCENE degraded)"
            segment.metadata = {**segment.metadata, "new_scene_degraded": str(exc)[:300]}
            return previous_frame_path
    segment.anchor_source = "previous_frame"
    return previous_frame_path


@shared_task(bind=True)
def generate_video_task(self, job_id, script_id):
    """Segment-by-segment Wan 2.2 generation with last-frame continuity (Phase 12)."""
    job = Job.objects.get(id=job_id)
    script = None
    try:
        script = VideoScript.objects.select_related("product", "store").get(id=script_id)
        scenes = list(script.scenes.all())
        if not scenes:
            raise RuntimeError("سناریو هیچ صحنه‌ای ندارد.")
        product_image = script.product.images.first()
        if product_image is None:
            raise RuntimeError("برای تولید ویدیو حداقل یک عکس محصول لازم است.")
        product_image_path = Path(product_image.image.path)

        # one segment row per scene; completed segments are never regenerated
        for scene in scenes:
            VideoSegment.objects.get_or_create(script=script, index=scene.index)
        segments = {s.index: s for s in script.segments.all()}

        script.status = VideoScript.Status.GENERATING
        script.save(update_fields=["status", "updated_at"])
        job.total_steps = len(scenes) + 1
        job.mark_running("آماده‌سازی تولید ویدیو")

        # only bill for what still has to render — a resumed run must not
        # charge again for segments that finished last time
        todo_seconds = sum(
            scene.duration for scene in scenes
            if segments[scene.index].status != VideoSegment.Status.DONE
        )
        quota = (
            billing.reserve(
                script.store, Usage.Metric.VIDEO_SECONDS, int(todo_seconds), job=job,
                detail=f"script {script.id}",
                external=not providers.uses_own_gpu(providers.VIDEO),
            )
            if todo_seconds else None
        )

        out_dir = Path(settings.MEDIA_ROOT) / "generated" / "videos" / f"script_{script.id}"
        out_dir.mkdir(parents=True, exist_ok=True)
        gpu.before_comfyui_work()  # evict Ollama models so Wan 2.2 has the VRAM
        client = ComfyUIClient()
        graph_template, manifest = load_workflow("wan22_i2v", "v1")

        previous_frame_path = None
        for step, scene in enumerate(scenes, start=1):
            segment = segments[scene.index]
            if segment.status == VideoSegment.Status.DONE and segment.last_frame:
                previous_frame_path = Path(segment.last_frame.path)
                job.mark_progress(step, f"قطعه {scene.index} از قبل آماده است")
                continue

            job.mark_progress(step, f"در حال تولید قطعه {scene.index} از {len(scenes)}")
            segment.status = VideoSegment.Status.GENERATING
            segment.error = ""
            anchor_path = _anchor_for_segment(
                scene, previous_frame_path, product_image_path, segment, client, out_dir
            )
            segment.save()
            try:
                uploaded_name = client.upload_image(anchor_path)
                positive = scene.visual_prompt
                if scene.motion_prompt:
                    positive = f"{positive}. Motion: {scene.motion_prompt}"
                patched = patch_workflow(
                    graph_template,
                    manifest,
                    image=uploaded_name,
                    positive=positive,
                    negative=NEGATIVE_PROMPT,
                    length=scene.duration * WAN_FPS + 1,
                    seed=random.randint(1, 2**31),
                    filename_prefix=f"upmarket/script_{script.id}/segment_{scene.index}",
                )
                video_path = client.generate(
                    patched, out_dir, filename=f"segment_{scene.index}.mp4"
                )
                frame_path = extract_last_frame(
                    video_path, out_dir / f"segment_{scene.index}_last.png"
                )
                segment.video.name = _media_rel(video_path)
                segment.last_frame.name = _media_rel(frame_path)
                segment.status = VideoSegment.Status.DONE
                segment.metadata = {
                    **segment.metadata,
                    "workflow": "wan22_i2v@v1",
                    "positive": positive,
                    "duration": scene.duration,
                }
                segment.save()
                previous_frame_path = frame_path
            except Exception as exc:
                segment.status = VideoSegment.Status.FAILED
                segment.retry_count += 1
                segment.error = str(exc)[:2000]
                segment.save()
                raise

        job.mark_progress(len(scenes) + 1, "در حال اتصال قطعات ویدیو")
        done_segments = [segments[s.index] for s in scenes]
        final_path = concat_videos(
            [Path(seg.video.path) for seg in done_segments], out_dir / "final.mp4"
        )
        script.final_video.name = _media_rel(final_path)
        script.status = VideoScript.Status.READY
        script.save()

        billing.commit(quota)  # the final file exists — now it counts
        job.mark_completed(
            {"script_id": script.id, "final_video": script.final_video.url}
        )
        return {"script_id": script.id}
    except Exception as exc:  # noqa: BLE001
        logger.exception("Video generation job %s failed", job_id)
        billing.release(locals().get("quota"), reason=type(exc).__name__)
        job.mark_failed(exc)  # job reaches a terminal state no matter what
        if script is not None:
            try:
                script.status = VideoScript.Status.FAILED
                script.save(update_fields=["status", "updated_at"])
            except Exception:  # script row may be gone — job is already FAILED
                logger.warning("Could not mark script %s FAILED", script_id)
        return {"error": str(exc)}
