from rest_framework import serializers

from .models import Store, StoreProfile


class StoreProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreProfile
        exclude = ["id", "store"]


class StoreSerializer(serializers.ModelSerializer):
    product_count = serializers.IntegerField(source="products.count", read_only=True)

    class Meta:
        model = Store
        fields = [
            "id",
            "name",
            "slug",
            "business_type",
            "description",
            "target_audience",
            "contact",
            "logo",
            "colors",
            "social_links",
            "is_active",
            "product_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["slug", "created_at", "updated_at"]
