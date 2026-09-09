from django.db import models

from apps.common.models import TimeStampedModel
from apps.jobs.models import Job
from apps.products.models import Product
from apps.stores.models import Store


class AIRequest(TimeStampedModel):
    """Audit record of every call made through the AI orchestration layer."""

    class TaskType(models.TextChoices):
        REASONING = "REASONING", "Reasoning"
        VISION = "VISION", "Vision"
        CODE = "CODE", "Code"

    class Status(models.TextChoices):
        OK = "OK", "OK"
        TIMEOUT = "TIMEOUT", "Timeout"
        PROVIDER_ERROR = "PROVIDER_ERROR", "Provider error"
        MALFORMED_OUTPUT = "MALFORMED_OUTPUT", "Malformed output"
        VALIDATION_FAILED = "VALIDATION_FAILED", "Validation failed"

    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="ai_requests")
    job = models.ForeignKey(Job, on_delete=models.SET_NULL, null=True, blank=True, related_name="ai_requests")
    task_type = models.CharField(max_length=16, choices=TaskType.choices)
    model = models.CharField(max_length=64)
    prompt_id = models.CharField(max_length=64)
    prompt_version = models.CharField(max_length=16)
    status = models.CharField(max_length=24, choices=Status.choices, default=Status.OK)
    attempts = models.PositiveIntegerField(default=1)
    latency_ms = models.PositiveIntegerField(null=True, blank=True)
    error = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.task_type} {self.model} [{self.status}]"


class AIResponse(models.Model):
    request = models.OneToOneField(AIRequest, on_delete=models.CASCADE, related_name="response")
    raw_output = models.TextField(blank=True)
    parsed = models.JSONField(null=True, blank=True)
    valid = models.BooleanField(default=False)


class ProductIntelligence(TimeStampedModel):
    """Structured AI understanding of a product (replaces legacy free-text ProductAnalysis)."""

    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name="intelligence")
    summary = models.TextField(blank=True)
    target_audience = models.JSONField(default=list, blank=True)
    selling_points = models.JSONField(default=list, blank=True)
    weaknesses = models.JSONField(default=list, blank=True)
    objections = models.JSONField(default=list, blank=True)
    marketing_angles = models.JSONField(default=list, blank=True)
    positioning = models.TextField(blank=True)
    recommended_tone = models.CharField(max_length=100, blank=True)
    content_ideas = models.JSONField(default=list, blank=True)
    use_cases = models.JSONField(default=list, blank=True)
    visual_analysis = models.JSONField(default=list, blank=True)
    source_request = models.ForeignKey(
        AIRequest, on_delete=models.SET_NULL, null=True, blank=True, related_name="+"
    )

    class Meta:
        verbose_name_plural = "product intelligence"

    def __str__(self):
        return f"Intelligence for {self.product.name}"


class ProductEmbedding(TimeStampedModel):
    """Vector embedding of a product's text, for semantic catalog search.

    Only written when EMBEDDINGS_ENABLED=true and an embedding model is
    installed on the Ollama host; the sales agent transparently falls back to
    keyword search when rows are missing.
    """

    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name="embedding")
    vector = models.JSONField(default=list)
    model = models.CharField(max_length=64)
    # hash of the embedded text — unchanged products are not re-embedded
    source_hash = models.CharField(max_length=40)

    def __str__(self):
        return f"Embedding for {self.product.name} ({self.model})"


class MarketResearch(TimeStampedModel):
    """Structured market/competitor analysis for a product.

    `research_inputs` holds real user-provided material (competitor names,
    prices, links, notes). `observations` are facts extracted ONLY from those
    inputs; `conclusions` are AI strategic reasoning, kept clearly separate so
    fabricated competitor data can never masquerade as fact.
    """

    class Confidence(models.TextChoices):
        LOW = "LOW", "Low"
        MEDIUM = "MEDIUM", "Medium"
        HIGH = "HIGH", "High"

    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="market_research")
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="market_research"
    )
    research_inputs = models.TextField(blank=True)
    web_results = models.JSONField(default=dict, blank=True)
    observations = models.JSONField(default=list, blank=True)
    conclusions = models.JSONField(default=dict, blank=True)
    confidence = models.CharField(
        max_length=8, choices=Confidence.choices, default=Confidence.LOW
    )
    source_request = models.ForeignKey(
        AIRequest, on_delete=models.SET_NULL, null=True, blank=True, related_name="+"
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "market research"

    def __str__(self):
        return f"Market research for {self.product.name} ({self.created_at:%Y-%m-%d})"


class ModelProvider(TimeStampedModel):
    """Where a given AI capability is served from — local hardware or an API.

    The whole point is that switching between "our RTX 3060" and "someone
    else's API" is an admin decision, not a code change: pick the capability,
    paste a base URL, an API key and a model name, save. Business logic asks
    for a capability and never learns which side answered.

    Providers are tried in `priority` order, so a cheap local card can be the
    default with a paid API behind it as an overflow — or the reverse while
    the GPU box is down.
    """

    class Capability(models.TextChoices):
        TEXT = "TEXT", "متن، تحلیل و ریسرچ"
        VISION = "VISION", "تحلیل تصویر"
        IMAGE = "IMAGE", "تولید تصویر"
        VIDEO = "VIDEO", "تولید ویدیو"

    class Kind(models.TextChoices):
        # local, self-hosted — no API key, no per-call cost
        OLLAMA = "OLLAMA", "Ollama (لوکال)"
        COMFYUI = "COMFYUI", "ComfyUI (لوکال)"
        # remote APIs
        OPENAI = "OPENAI", "OpenAI-compatible API"
        REPLICATE = "REPLICATE", "Replicate"
        HTTP = "HTTP", "HTTP سفارشی"

    LOCAL_KINDS = {Kind.OLLAMA, Kind.COMFYUI}

    capability = models.CharField(max_length=8, choices=Capability.choices)
    kind = models.CharField(max_length=12, choices=Kind.choices)
    name = models.CharField(max_length=80, help_text="نام دلخواه برای تشخیص در پنل")

    base_url = models.URLField(
        blank=True,
        help_text="مثال: http://127.0.0.1:11434 یا https://api.openai.com/v1 — "
        "خالی یعنی از مقدار .env استفاده شود",
    )
    api_key = models.CharField(
        max_length=255, blank=True, help_text="برای سرویس‌های لوکال خالی بگذار"
    )
    model_name = models.CharField(
        max_length=120,
        help_text="نام مدل یا ورک‌فلو. مثال: qwq:32b · gpt-4o-mini · wan22_i2v@v1",
    )

    is_active = models.BooleanField(default=True)
    priority = models.PositiveSmallIntegerField(
        default=100, help_text="کمتر = زودتر امتحان می‌شود"
    )
    timeout_s = models.PositiveIntegerField(default=600)
    options = models.JSONField(
        default=dict, blank=True,
        help_text="پارامترهای اضافه به‌صورت JSON (temperature، steps، …)",
    )

    # filled in by the admin "test connection" action
    checked_at = models.DateTimeField(null=True, blank=True)
    is_healthy = models.BooleanField(null=True, blank=True)
    last_error = models.TextField(blank=True)

    class Meta:
        ordering = ["capability", "priority", "id"]
        indexes = [models.Index(fields=["capability", "is_active", "priority"])]
        verbose_name = "AI provider"

    def __str__(self):
        return f"{self.get_capability_display()} · {self.name} ({self.get_kind_display()})"

    @property
    def is_local(self) -> bool:
        """Local providers cost GPU minutes; remote ones cost money per call."""
        return self.kind in self.LOCAL_KINDS

    def clean(self):
        from django.core.exceptions import ValidationError

        if not self.is_local and not self.base_url:
            raise ValidationError({"base_url": "برای سرویس بیرونی، آدرس الزامی است."})
        if self.kind == self.Kind.COMFYUI and self.capability not in {
            self.Capability.IMAGE, self.Capability.VIDEO,
        }:
            raise ValidationError({"kind": "ComfyUI فقط تصویر و ویدیو تولید می‌کند."})
        if self.kind == self.Kind.OLLAMA and self.capability not in {
            self.Capability.TEXT, self.Capability.VISION,
        }:
            raise ValidationError({"kind": "Ollama فقط متن و تحلیل تصویر انجام می‌دهد."})
