from rest_framework import serializers

from .models import Job


class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = [
            "id",
            "store",
            "type",
            "state",
            "progress_step",
            "total_steps",
            "current_step_label",
            "retry_count",
            "error",
            "context",
            "result",
            "created_at",
            "updated_at",
        ]
