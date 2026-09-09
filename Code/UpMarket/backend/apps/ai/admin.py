from django.contrib import admin

from .models import AIRequest, AIResponse, MarketResearch, ProductIntelligence


class AIResponseInline(admin.StackedInline):
    model = AIResponse
    extra = 0
    readonly_fields = ["raw_output", "parsed", "valid"]


@admin.register(AIRequest)
class AIRequestAdmin(admin.ModelAdmin):
    list_display = ["id", "task_type", "model", "prompt_id", "status", "latency_ms", "created_at"]
    list_filter = ["task_type", "status", "model"]
    inlines = [AIResponseInline]


@admin.register(ProductIntelligence)
class ProductIntelligenceAdmin(admin.ModelAdmin):
    list_display = ["product", "recommended_tone", "updated_at"]


@admin.register(MarketResearch)
class MarketResearchAdmin(admin.ModelAdmin):
    list_display = ["product", "store", "confidence", "created_at"]
    list_filter = ["confidence"]
from .admin_providers import ModelProviderAdmin  # noqa: F401
