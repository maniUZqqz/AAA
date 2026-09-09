from django.urls import path

from .views import (
    CaptionView,
    ImageStudioView,
    VideoGenerateView,
    VideoScriptView,
    VoiceGenerateView,
)


urlpatterns = [
    path("products/<int:pk>/captions/", CaptionView.as_view(), name="product-captions"),
    path("products/<int:pk>/image-studio/", ImageStudioView.as_view(), name="product-image-studio"),
    path("products/<int:pk>/video-script/", VideoScriptView.as_view(), name="product-video-script"),
    path("video-scripts/<int:pk>/generate/", VideoGenerateView.as_view(), name="video-generate"),
    path("video-scripts/<int:pk>/voice/", VoiceGenerateView.as_view(), name="video-voice"),
]
