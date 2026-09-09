from django.contrib import admin

from .models import Store, StoreProfile


class StoreProfileInline(admin.StackedInline):
    model = StoreProfile
    extra = 0


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ["name", "owner", "business_type", "is_active", "created_at"]
    search_fields = ["name", "owner__username"]
    inlines = [StoreProfileInline]
