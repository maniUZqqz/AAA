from django.urls import path

from .views import EmbeddingsView, MarketAnalysisView, ProductAnalyzeView, ProductIntelligenceView
from .views_providers import AIProviderHealthView, AIStatusView



urlpatterns = [
    path("ai/status/", AIStatusView.as_view(), name="ai-status"),
    path("ai/providers/health/", AIProviderHealthView.as_view(), name="ai-provider-health"),
    path("products/<int:pk>/analyze/", ProductAnalyzeView.as_view(), name="product-analyze"),
    path("stores/<int:store_id>/embeddings/", EmbeddingsView.as_view(), name="store-embeddings"),
    path(
        "stores/<int:store_id>/embeddings/rebuild/",
        EmbeddingsView.as_view(),
        name="store-embeddings-rebuild",
    ),
    path(
        "products/<int:pk>/intelligence/",
        ProductIntelligenceView.as_view(),
        name="product-intelligence",
    ),
    path(
        "products/<int:pk>/market-analysis/",
        MarketAnalysisView.as_view(),
        name="product-market-analysis",
    ),
]
