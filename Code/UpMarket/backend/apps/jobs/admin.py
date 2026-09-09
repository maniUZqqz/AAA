from django.contrib import admin

from .models import Job


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ["id", "type", "state", "store", "progress_step", "total_steps", "created_at"]
    list_filter = ["type", "state"]
    readonly_fields = ["created_at", "updated_at"]
