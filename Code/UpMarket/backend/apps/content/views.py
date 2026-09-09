from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response

from apps.billing import guards
from rest_framework.views import APIView

from apps.jobs import staleness
from apps.jobs.models import Job
from apps.jobs.serializers import JobSerializer
from apps.jobs.services import (
    QUEUE_SETUP_HINT,
    dispatch_job,
    queue_is_available,
    queue_unavailable_response,
)
from apps.products.models import Product

from .models import Caption, GeneratedImage, VideoScript
from .serializers import CaptionSerializer, GeneratedImageSerializer, VideoScriptSerializer
from .tasks import (
    generate_captions_task,
    generate_image_task,
    generate_video_script_task,
    generate_video_task,
    generate_voice_task,
)


def _owned_product(request, pk) -> Product:
    return get_object_or_404(
        Product.objects.filter(store__owner=request.user).select_related("store"), pk=pk
    )


def _active_script_job(script, job_type):
    """Live QUEUED/RUNNING job of `job_type` for this script, or None.

    Dead rows are reaped first (apps.jobs.staleness), so a worker that died
    mid-task can never deadlock the next run.
    """
    active = Job.objects.filter(
        store=script.store,
        type=job_type,
        context__script_id=script.id,
    )
    staleness.reap(active)
    return active.filter(state__in=staleness.ACTIVE_STATES).first()


def _already_running_response(job):
    return Response(
        {
            "error": {
                "code": "already_running",
                "message": "همین عملیات برای این سناریو در حال اجراست؛ صبر کنید تا تمام شود.",
            },
            "job": JobSerializer(job).data,
        },
        status=status.HTTP_409_CONFLICT,
    )


class CaptionView(APIView):
    """GET = captions of a product; POST = generate new ones (202 + job).

    beter.md #11: a caption is written for a specific CONTENT item — pass
    `image_id` (a GeneratedImage of this product) or `video_script_id`
    (a VideoScript of this product); neither = product-level caption.
    """

    def get(self, request, pk):
        product = _owned_product(request, pk)
        captions = Caption.objects.filter(product=product).select_related(
            "about_image", "about_video"
        )[:30]
        return Response(
            CaptionSerializer(captions, many=True, context={"request": request}).data
        )

    def post(self, request, pk):
        product = _owned_product(request, pk)
        platforms = request.data.get("platforms") or ["INSTAGRAM", "TELEGRAM", "LINKEDIN"]
        if not isinstance(platforms, list):
            platforms = [str(platforms)]
        platforms = [str(p).upper() for p in platforms]
        tone = str(request.data.get("tone", "") or "")
        objective = str(request.data.get("objective", "") or "")

        image_id = request.data.get("image_id")
        video_script_id = request.data.get("video_script_id")
        if image_id and not GeneratedImage.objects.filter(
            product=product, id=image_id
        ).exists():
            return Response(
                {
                    "error": {
                        "code": "invalid_subject",
                        "message": "تصویر انتخاب‌شده متعلق به این محصول نیست.",
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        if video_script_id and not VideoScript.objects.filter(
            product=product, id=video_script_id
        ).exists():
            return Response(
                {
                    "error": {
                        "code": "invalid_subject",
                        "message": "ویدیوی انتخاب‌شده متعلق به این محصول نیست.",
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        denied = guards.check(product.store, guards.CAPTIONS, len(platforms))
        if denied is not None:
            return denied

        job = Job.objects.create(
            store=product.store,
            type=Job.Type.CAPTION_GENERATION,
            context={
                "product_id": product.id,
                "platforms": platforms,
                "image_id": image_id,
                "video_script_id": video_script_id,
            },
        )
        error = dispatch_job(
            job,
            generate_captions_task,
            job.id,
            product.id,
            platforms,
            tone,
            objective,
            image_id,
            video_script_id,
        )
        if error is not None:
            return error
        job.refresh_from_db()
        return Response(
            {"job_id": job.id, "job": JobSerializer(job).data}, status=status.HTTP_202_ACCEPTED
        )


class VideoScriptView(APIView):
    """GET = latest script (scenes + segments + final video); POST = generate script."""

    def get(self, request, pk):
        product = _owned_product(request, pk)
        script = (
            VideoScript.objects.filter(product=product)
            .prefetch_related("scenes", "segments")
            .first()
        )
        if script is None:
            # 200 + null: "no script yet" is a normal state, not an error —
            # a 404 here spammed the browser console on every product page load
            return Response(None)
        return Response(VideoScriptSerializer(script, context={"request": request}).data)

    def post(self, request, pk):
        product = _owned_product(request, pk)
        try:
            total_duration = int(request.data.get("duration") or 30)
        except (TypeError, ValueError):
            total_duration = 30
        total_duration = max(5, min(60, total_duration))
        objective = str(request.data.get("objective", "") or "")
        language = str(request.data.get("language", "") or "fa").lower()
        if language not in {"fa", "en"}:
            language = "fa"
        job = Job.objects.create(
            store=product.store,
            type=Job.Type.VIDEO_SCRIPT,
            context={"product_id": product.id, "duration": total_duration, "language": language},
        )
        error = dispatch_job(
            job, generate_video_script_task, job.id, product.id, total_duration, objective, language
        )
        if error is not None:
            return error
        job.refresh_from_db()
        return Response(
            {"job_id": job.id, "job": JobSerializer(job).data}, status=status.HTTP_202_ACCEPTED
        )


class ImageStudioView(APIView):
    """GET = generated images of a product; POST = generate a new one (202 + job)."""

    def get(self, request, pk):
        product = _owned_product(request, pk)
        images = GeneratedImage.objects.filter(product=product)[:30]
        return Response(
            GeneratedImageSerializer(images, many=True, context={"request": request}).data
        )

    def post(self, request, pk):
        product = _owned_product(request, pk)
        kind = str(request.data.get("kind", "") or "").upper()
        if kind not in GeneratedImage.Kind.values:
            return Response(
                {
                    "error": {
                        "code": "invalid_kind",
                        "message": f"kind must be one of {list(GeneratedImage.Kind.values)}",
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        if kind == GeneratedImage.Kind.ENHANCED and not product.images.exists():
            return Response(
                {
                    "error": {
                        "code": "no_product_image",
                        "message": "برای بهبود عکس، اول یک عکس محصول آپلود کنید.",
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        style = str(request.data.get("style", "") or "")
        instructions = str(request.data.get("instructions", "") or "")
        source_image_id = request.data.get("source_image_id")
        denied = guards.check(product.store, guards.IMAGES, 1)
        if denied is not None:
            return denied

        job = Job.objects.create(
            store=product.store,
            type=Job.Type.IMAGE_GENERATION,
            context={"product_id": product.id, "kind": kind},
        )
        error = dispatch_job(
            job, generate_image_task, job.id, product.id, kind, style, instructions, source_image_id
        )
        if error is not None:
            return error
        job.refresh_from_db()
        return Response(
            {"job_id": job.id, "job": JobSerializer(job).data}, status=status.HTTP_202_ACCEPTED
        )


class VoiceGenerateView(APIView):
    """POST /api/v1/video-scripts/{id}/voice/ — TTS + timing-aware mix."""

    def post(self, request, pk):
        script = get_object_or_404(
            VideoScript.objects.filter(store__owner=request.user), pk=pk
        )
        if not script.final_video:
            return Response(
                {
                    "error": {
                        "code": "no_final_video",
                        "message": "اول باید ویدیوی نهایی تولید شود.",
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        active = _active_script_job(script, Job.Type.VOICE_GENERATION)
        if active is not None:
            return _already_running_response(active)
        job = Job.objects.create(
            store=script.store,
            type=Job.Type.VOICE_GENERATION,
            context={"script_id": script.id},
        )
        error = dispatch_job(job, generate_voice_task, job.id, script.id)
        if error is not None:
            return error
        job.refresh_from_db()
        return Response(
            {"job_id": job.id, "job": JobSerializer(job).data}, status=status.HTTP_202_ACCEPTED
        )


class VideoGenerateView(APIView):
    """POST /api/v1/video-scripts/{id}/generate/ — run the Wan 2.2 segment pipeline."""

    def post(self, request, pk):
        script = get_object_or_404(
            VideoScript.objects.filter(store__owner=request.user).select_related("product", "store"),
            pk=pk,
        )
        if not script.product.images.exists():
            return Response(
                {
                    "error": {
                        "code": "no_product_image",
                        "message": "برای تولید ویدیو حداقل یک عکس محصول لازم است.",
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        # A real Wan 2.2 run takes many minutes — inside a synchronous HTTP
        # request it would time out; require the queue (except in tests).
        # The mode is detected at runtime (Redis up = queue mode), so nothing
        # here has to be switched by hand in .env (beter.md v2 #5).
        if not queue_is_available() and not settings.IS_TEST:
            return queue_unavailable_response(
                message="تولید ویدیو حتماً به صف پردازش نیاز دارد (هر کلیپ چند دقیقه طول "
                "می‌کشد و داخل یک درخواست وب جا نمی‌شود). Redis روشن نیست. "
                + QUEUE_SETUP_HINT
            )
        active = _active_script_job(script, Job.Type.VIDEO_GENERATION)
        if active is not None:
            return _already_running_response(active)
        seconds = sum(scene.duration for scene in script.scenes.all()) or script.total_duration
        denied = guards.check(script.store, guards.VIDEO_SECONDS, int(seconds))
        if denied is not None:
            return denied

        job = Job.objects.create(
            store=script.store,
            type=Job.Type.VIDEO_GENERATION,
            context={"script_id": script.id, "product_id": script.product_id},
        )
        error = dispatch_job(job, generate_video_task, job.id, script.id)
        if error is not None:
            return error
        job.refresh_from_db()
        return Response(
            {"job_id": job.id, "job": JobSerializer(job).data}, status=status.HTTP_202_ACCEPTED
        )
