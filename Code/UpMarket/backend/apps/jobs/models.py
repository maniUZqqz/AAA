from django.db import models

from apps.common.models import TimeStampedModel
from apps.stores.models import Store


class Job(TimeStampedModel):
    """Persistent record of every background AI/generation job."""

    class Type(models.TextChoices):
        PRODUCT_ANALYSIS = "product_analysis", "Product analysis"
        MARKET_ANALYSIS = "market_analysis", "Market / competitor analysis"
        CAPTION_GENERATION = "caption_generation", "Caption generation"
        IMAGE_GENERATION = "image_generation", "Image generation"
        VIDEO_GENERATION = "video_generation", "Video generation"
        VIDEO_SCRIPT = "video_script_generation", "Video script generation"
        VIDEO_SEGMENT = "video_segment_generation", "Video segment generation"
        VIDEO_CONCAT = "video_concatenation", "Video concatenation"
        VOICE_GENERATION = "voice_generation", "Voice generation"
        PUBLISHING = "publishing", "Publishing"
        EMBEDDING_BUILD = "embedding_build", "Product embeddings build"

    class State(models.TextChoices):
        QUEUED = "QUEUED", "Queued"
        RUNNING = "RUNNING", "Running"
        COMPLETED = "COMPLETED", "Completed"
        FAILED = "FAILED", "Failed"
        CANCELLED = "CANCELLED", "Cancelled"

    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="jobs")
    type = models.CharField(max_length=40, choices=Type.choices)
    state = models.CharField(max_length=16, choices=State.choices, default=State.QUEUED)
    progress_step = models.PositiveIntegerField(default=0)
    total_steps = models.PositiveIntegerField(default=0)
    current_step_label = models.CharField(max_length=200, blank=True)
    retry_count = models.PositiveIntegerField(default=0)
    error = models.TextField(blank=True)
    context = models.JSONField(default=dict, blank=True)
    result = models.JSONField(default=dict, blank=True)
    celery_task_id = models.CharField(max_length=64, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["state"]), models.Index(fields=["store", "created_at"])]

    def __str__(self):
        return f"{self.type} #{self.id} [{self.state}]"

    def mark_running(self, label=""):
        self.state = self.State.RUNNING
        self.current_step_label = label
        # tasks set total_steps just before calling this — persist it too
        self.save(update_fields=["state", "current_step_label", "total_steps", "updated_at"])

    def mark_progress(self, step, label=""):
        self.progress_step = step
        if label:
            self.current_step_label = label
        self.save(update_fields=["progress_step", "current_step_label", "updated_at"])

    def mark_completed(self, result=None):
        self.state = self.State.COMPLETED
        self.result = result or {}
        self.current_step_label = ""
        self.save(update_fields=["state", "result", "current_step_label", "updated_at"])

    def mark_failed(self, error):
        self.state = self.State.FAILED
        self.error = str(error)[:4000]
        self.save(update_fields=["state", "error", "updated_at"])
