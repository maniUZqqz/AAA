from django.db import models

from apps.ai.models import AIRequest
from apps.common.models import TimeStampedModel
from apps.products.models import Product, ProductImage
from apps.stores.models import Store


class Caption(TimeStampedModel):
    """Platform-specific caption set for a product (Phase 10)."""

    class Platform(models.TextChoices):
        INSTAGRAM = "INSTAGRAM", "Instagram"
        TELEGRAM = "TELEGRAM", "Telegram"
        LINKEDIN = "LINKEDIN", "LinkedIn"

    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="captions")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="captions")
    platform = models.CharField(max_length=16, choices=Platform.choices)
    tone = models.CharField(max_length=100, blank=True)
    objective = models.CharField(max_length=200, blank=True)
    short_text = models.TextField(blank=True)
    medium_text = models.TextField(blank=True)
    long_text = models.TextField(blank=True)
    hashtags = models.JSONField(default=list, blank=True)
    cta = models.CharField(max_length=300, blank=True)
    # beter.md #11: a caption belongs to a specific piece of CONTENT (a generated
    # poster/photo or a video), not to the product in the abstract. Both empty =
    # legacy product-level caption.
    about_image = models.ForeignKey(
        "GeneratedImage", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="captions",
    )
    about_video = models.ForeignKey(
        "VideoScript", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="captions",
    )
    source_request = models.ForeignKey(
        AIRequest, on_delete=models.SET_NULL, null=True, blank=True, related_name="+"
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.platform} caption for {self.product.name}"


class GeneratedImage(TimeStampedModel):
    """AI-generated marketing image (Phase 9 — Image Studio)."""

    class Kind(models.TextChoices):
        POSTER = "POSTER", "Advertising poster"
        PRODUCT_SHOT = "PRODUCT_SHOT", "Instagram-ready product photo"
        ENHANCED = "ENHANCED", "Product-preserving enhancement"

    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="generated_images")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="generated_images")
    kind = models.CharField(max_length=16, choices=Kind.choices)
    concept = models.TextField(blank=True)
    prompt_en = models.TextField(blank=True)
    negative_en = models.TextField(blank=True)
    style = models.CharField(max_length=200, blank=True)
    instructions = models.TextField(blank=True)
    source_image = models.ForeignKey(
        ProductImage, on_delete=models.SET_NULL, null=True, blank=True, related_name="+"
    )
    image = models.FileField(upload_to="generated/images/")
    workflow_version = models.CharField(max_length=40, blank=True)
    source_request = models.ForeignKey(
        AIRequest, on_delete=models.SET_NULL, null=True, blank=True, related_name="+"
    )
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.kind} image for {self.product.name}"


class VideoScript(TimeStampedModel):
    """Machine-readable advertising video plan (Phase 11)."""

    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        GENERATING = "GENERATING", "Generating video"
        READY = "READY", "Video ready"
        FAILED = "FAILED", "Failed"

    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="video_scripts")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="video_scripts")
    concept = models.TextField(blank=True)
    objective = models.CharField(max_length=200, blank=True)
    cta = models.CharField(max_length=300, blank=True)
    total_duration = models.PositiveIntegerField(default=30)
    # narration + voice-over language ('fa' or 'en') — chosen in the UI
    narration_language = models.CharField(max_length=5, default="fa")
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.DRAFT)
    final_video = models.FileField(upload_to="generated/videos/", null=True, blank=True)
    voice_audio = models.FileField(upload_to="generated/audio/", null=True, blank=True)
    final_video_voiced = models.FileField(upload_to="generated/videos/", null=True, blank=True)
    raw = models.JSONField(default=dict, blank=True)
    source_request = models.ForeignKey(
        AIRequest, on_delete=models.SET_NULL, null=True, blank=True, related_name="+"
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Video script #{self.id} for {self.product.name}"


class VideoScene(models.Model):
    class Transition(models.TextChoices):
        CONTINUE = "CONTINUE", "Continue from last frame"
        TRANSITION = "TRANSITION", "Soft transition"
        NEW_SCENE = "NEW_SCENE", "New visual anchor"

    script = models.ForeignKey(VideoScript, on_delete=models.CASCADE, related_name="scenes")
    index = models.PositiveIntegerField()
    duration = models.PositiveIntegerField(default=5)
    visual_prompt = models.TextField()
    motion_prompt = models.TextField(blank=True)
    narration = models.TextField(blank=True)
    transition = models.CharField(
        max_length=12, choices=Transition.choices, default=Transition.CONTINUE
    )

    class Meta:
        ordering = ["index"]
        constraints = [
            models.UniqueConstraint(fields=["script", "index"], name="uniq_scene_index")
        ]

    def __str__(self):
        return f"Scene {self.index} of script #{self.script_id}"


class VideoSegment(TimeStampedModel):
    """One generated ~5s clip. Files live under MEDIA and are tracked here (Phase 12)."""

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        GENERATING = "GENERATING", "Generating"
        DONE = "DONE", "Done"
        FAILED = "FAILED", "Failed"

    script = models.ForeignKey(VideoScript, on_delete=models.CASCADE, related_name="segments")
    index = models.PositiveIntegerField()
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.PENDING)
    anchor_source = models.CharField(max_length=200, blank=True)
    video = models.FileField(upload_to="generated/videos/", null=True, blank=True)
    last_frame = models.FileField(upload_to="generated/frames/", null=True, blank=True)
    retry_count = models.PositiveIntegerField(default=0)
    error = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["index"]
        constraints = [
            models.UniqueConstraint(fields=["script", "index"], name="uniq_segment_index")
        ]

    def __str__(self):
        return f"Segment {self.index} of script #{self.script_id} [{self.status}]"
