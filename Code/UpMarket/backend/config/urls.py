from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve as media_serve
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/auth/", include("apps.accounts.urls")),
    path("api/v1/", include("apps.stores.urls")),
    path("api/v1/", include("apps.products.urls")),
    path("api/v1/", include("apps.ai.urls")),
    path("api/v1/", include("apps.jobs.urls")),
    path("api/v1/", include("apps.customers.urls")),
    path("api/v1/", include("apps.content.urls")),
    path("api/v1/", include("apps.campaigns.urls")),
    path("api/v1/", include("apps.analytics.urls")),
    path("api/v1/", include("apps.billing.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    # LAN deployment serves media through Django too (product images, generated
    # videos, n8n payload URLs). Put a real web server in front if internet-facing.
    urlpatterns += [
        re_path(
            r"^media/(?P<path>.*)$", media_serve, {"document_root": settings.MEDIA_ROOT}
        )
    ]
