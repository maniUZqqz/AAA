"""Publishing tasks (Phase 15) — deliver approved campaign packages to n8n."""
import logging

from celery import shared_task
from django.conf import settings
from django.utils import timezone

from apps.jobs.models import Job
from services.publishing import novinhub
from services.publishing.n8n import PublishError, send_to_n8n

from .models import Campaign, PublishJob

logger = logging.getLogger(__name__)


def _absolute_media_url(filefield) -> str | None:
    if not filefield:
        return None
    base = settings.UPMARKET_PUBLISHING["PUBLIC_BASE_URL"]
    return f"{base}{filefield.url}"


def build_payload(campaign: Campaign, platform: str) -> dict:
    """Content package for n8n. Only real, stored data — nothing invented."""
    store = campaign.store
    product = campaign.product
    caption = campaign.caption
    video = campaign.video_script
    video_url = None
    if video is not None:
        video_url = _absolute_media_url(video.final_video_voiced) or _absolute_media_url(
            video.final_video
        )
    return {
        "platform": platform,
        "store": {
            "id": store.id,
            "name": store.name,
            "business_type": store.business_type,
            "social_links": store.social_links,
        },
        "campaign": {
            "id": campaign.id,
            "name": campaign.name,
            "goal": campaign.goal,
            "audience": campaign.audience,
        },
        "product": {
            "id": product.id,
            "name": product.name,
            "price": str(product.price),
            "currency": product.currency,
        },
        "content": {
            "caption": (
                {
                    "short": caption.short_text,
                    "medium": caption.medium_text,
                    "long": caption.long_text,
                    "hashtags": caption.hashtags,
                    "cta": caption.cta,
                }
                if caption
                else None
            ),
            "poster_url": _absolute_media_url(campaign.poster.image) if campaign.poster else None,
            "product_image_url": (
                _absolute_media_url(campaign.product_image.image)
                if campaign.product_image
                else None
            ),
            "video_url": video_url,
        },
    }


def _deliver(campaign, publish_job, payload: dict) -> dict:
    """Send one platform out, through NovinHub when it can carry it.

    Instagram goes through NovinHub whenever a token and at least one account
    id are configured, because that publishes for real. Everything else — and
    Instagram with no token — keeps going to the n8n webhook the owner wires
    up themselves, so an unconfigured install still works exactly as before.
    """
    if publish_job.platform.upper() == "INSTAGRAM":
        profile = getattr(campaign.store, "profile", None)
        account_ids = list(getattr(profile, "novinhub_account_ids", None) or [])
        shared = settings.UPMARKET_PUBLISHING.get("NOVINHUB_TOKEN", "")
        has_token = bool(getattr(profile, "novinhub_token", "") or shared)
        if account_ids and has_token:
            logger.info("campaign %s → NovinHub", campaign.id)
            return novinhub.publish_campaign(campaign, account_ids=account_ids)
        logger.info(
            "campaign %s → n8n (NovinHub not configured: token=%s accounts=%s)",
            campaign.id, has_token, len(account_ids),
        )
    return send_to_n8n(payload)


@shared_task(bind=True)
def publish_campaign_task(self, job_id, campaign_id, publish_job_ids):
    job = Job.objects.get(id=job_id)
    try:
        campaign = Campaign.objects.select_related("store", "product").get(id=campaign_id)
        # scoped to THIS campaign — foreign ids are ignored, never delivered
        publish_jobs = list(
            PublishJob.objects.filter(campaign=campaign, id__in=publish_job_ids)
        )
        if not publish_jobs:
            raise RuntimeError("هیچ PublishJob معتبری برای این کمپین یافت نشد.")
        job.total_steps = len(publish_jobs)
        job.mark_running("در حال انتشار")

        failures = []
        for step, publish_job in enumerate(publish_jobs, start=1):
            job.mark_progress(step, f"ارسال به {publish_job.platform}")
            payload = build_payload(campaign, publish_job.platform)
            publish_job.payload = payload
            publish_job.attempts += 1
            try:
                response = _deliver(campaign, publish_job, payload)
                publish_job.status = PublishJob.Status.SENT
                publish_job.response = response
                publish_job.published_at = timezone.now()
                publish_job.last_error = ""
            except (PublishError, novinhub.NovinHubError) as exc:
                publish_job.status = PublishJob.Status.FAILED
                publish_job.last_error = str(exc)
                failures.append(f"{publish_job.platform}: {exc}")
            publish_job.save()

        sent = [p.platform for p in publish_jobs if p.status == PublishJob.Status.SENT]
        # SENT rows are final — a later retry re-dispatches only failed/new
        # platforms (the view skips SENT ones), so nothing is ever posted twice.
        if sent:
            campaign.approval_state = Campaign.ApprovalState.PUBLISHED
            campaign.save(update_fields=["approval_state", "updated_at"])
        if failures:
            job.mark_failed(
                "ارسال ناموفق برای: " + "; ".join(failures)
                + (f" (ارسال‌شده: {', '.join(sent)})" if sent else "")
            )
            return {"published": len(sent), "failed": len(failures)}
        job.mark_completed({"campaign_id": campaign.id, "published": len(sent)})
        return {"published": len(sent)}
    except Exception as exc:  # noqa: BLE001
        logger.exception("Publish job %s failed", job_id)
        job.mark_failed(exc)
        return {"error": str(exc)}
