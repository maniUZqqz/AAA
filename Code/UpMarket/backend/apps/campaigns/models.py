from django.db import models

from apps.common.models import TimeStampedModel
from apps.content.models import Caption, GeneratedImage, VideoScript
from apps.products.models import Product
from apps.stores.models import Store


class Campaign(TimeStampedModel):
    """Groups approved marketing content for one product (Phase 14)."""

    class ApprovalState(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"
        PUBLISHED = "PUBLISHED", "Published"
        ARCHIVED = "ARCHIVED", "Archived"

    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="campaigns")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="campaigns")
    name = models.CharField(max_length=200)
    goal = models.CharField(max_length=200, blank=True)
    audience = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)
    poster = models.ForeignKey(
        GeneratedImage, on_delete=models.SET_NULL, null=True, blank=True, related_name="+"
    )
    product_image = models.ForeignKey(
        GeneratedImage, on_delete=models.SET_NULL, null=True, blank=True, related_name="+"
    )
    caption = models.ForeignKey(
        Caption, on_delete=models.SET_NULL, null=True, blank=True, related_name="+"
    )
    video_script = models.ForeignKey(
        VideoScript, on_delete=models.SET_NULL, null=True, blank=True, related_name="+"
    )
    approval_state = models.CharField(
        max_length=12, choices=ApprovalState.choices, default=ApprovalState.DRAFT
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.store.name})"


class PublishJob(TimeStampedModel):
    """One delivery attempt of a campaign package to n8n for one platform."""

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        SENT = "SENT", "Sent"
        FAILED = "FAILED", "Failed"

    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="publish_jobs")
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name="publish_jobs")
    platform = models.CharField(max_length=32)
    payload = models.JSONField(default=dict, blank=True)
    response = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.PENDING)
    attempts = models.PositiveIntegerField(default=0)
    last_error = models.TextField(blank=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Publish {self.platform} for campaign #{self.campaign_id} [{self.status}]"
