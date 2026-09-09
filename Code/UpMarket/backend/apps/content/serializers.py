from rest_framework import serializers

from .models import Caption, GeneratedImage, VideoScene, VideoScript, VideoSegment


class GeneratedImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneratedImage
        fields = [
            "id",
            "product",
            "kind",
            "concept",
            "prompt_en",
            "style",
            "instructions",
            "source_image",
            "image",
            "workflow_version",
            # the poster's Persian headline/price live here, and so does
            # `text_overlay_error` — without it a poster whose text overlay
            # failed looks exactly like one that worked
            "metadata",
            "created_at",
        ]


class CaptionSerializer(serializers.ModelSerializer):
    about_image_url = serializers.SerializerMethodField()
    about_label = serializers.SerializerMethodField()

    class Meta:
        model = Caption
        fields = [
            "id",
            "product",
            "platform",
            "tone",
            "objective",
            "short_text",
            "medium_text",
            "long_text",
            "hashtags",
            "cta",
            "about_image",
            "about_video",
            "about_image_url",
            "about_label",
            "created_at",
        ]

    def get_about_image_url(self, obj):
        if obj.about_image and obj.about_image.image:
            request = self.context.get("request")
            url = obj.about_image.image.url
            return request.build_absolute_uri(url) if request else url
        return None

    def get_about_label(self, obj):
        if obj.about_image:
            kind = {
                "POSTER": "پوستر",
                "PRODUCT_SHOT": "عکس اینستاگرامی",
                "ENHANCED": "عکس بهبودیافته",
            }.get(obj.about_image.kind, "تصویر")
            return f"برای {kind} #{obj.about_image_id}"
        if obj.about_video:
            return f"برای ویدیو #{obj.about_video_id}"
        return "برای خود محصول"


class VideoSceneSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoScene
        fields = [
            "index",
            "duration",
            "visual_prompt",
            "motion_prompt",
            "narration",
            "transition",
        ]


class VideoSegmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoSegment
        fields = [
            "index",
            "status",
            "anchor_source",
            "video",
            "last_frame",
            "retry_count",
            "error",
            "updated_at",
        ]


class VideoScriptSerializer(serializers.ModelSerializer):
    scenes = VideoSceneSerializer(many=True, read_only=True)
    segments = VideoSegmentSerializer(many=True, read_only=True)

    class Meta:
        model = VideoScript
        fields = [
            "id",
            "product",
            "concept",
            "objective",
            "cta",
            "total_duration",
            "narration_language",
            "status",
            "final_video",
            "voice_audio",
            "final_video_voiced",
            "scenes",
            "segments",
            "created_at",
            "updated_at",
        ]
