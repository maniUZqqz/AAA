from django.contrib import admin
from django.utils.html import format_html

from . import services
from .models import Plan, Subscription, Usage


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "price_toman", "video_seconds", "images",
                    "captions", "is_public", "is_trial", "sort_order"]
    list_editable = ["price_toman", "sort_order", "is_public"]
    prepopulated_fields = {"slug": ["name"]}
    fieldsets = [
        ("معرفی", {"fields": ["name", "slug", "description", "price_toman",
                              "sort_order", "is_public"]}),
        ("سهمیه‌ی ماهانه", {
            "fields": ["video_seconds", "images", "captions"],
            "description": "این اعداد باید با دیتا/1-داده/data.json یکی بمانند.",
        }),
        ("محدودیت‌ها", {"fields": ["max_products", "max_stores",
                                   "allows_publishing", "allows_sales_agent"]}),
        ("دوره آزمایشی", {"fields": ["is_trial", "trial_days"]}),
    ]


class UsageInline(admin.TabularInline):
    model = Usage
    extra = 0
    fields = ["metric", "quantity", "state", "external", "detail", "created_at"]
    readonly_fields = fields
    can_delete = False
    max_num = 0
    ordering = ["-created_at"]


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ["store", "plan", "status", "usage_bars", "days_left", "period_end"]
    list_filter = ["status", "plan"]
    search_fields = ["store__name"]
    autocomplete_fields = ["store"]
    inlines = [UsageInline]
    actions = ["roll_period", "mark_active"]
    fieldsets = [
        (None, {"fields": ["store", "plan", "status", "note"]}),
        ("دوره", {"fields": ["period_start", "period_end", "cancel_at_period_end"]}),
        ("سهمیه‌ی اضافی دستی", {
            "fields": ["bonus_video_seconds", "bonus_images", "bonus_captions"],
            "description": "برای جبران یک رندر خراب، بدون تغییر پلن.",
        }),
    ]

    @admin.display(description="مصرف این دوره")
    def usage_bars(self, obj):
        parts = []
        for row in services.snapshot(obj.store)["metrics"]:
            color = "#c00" if row["percent"] >= 90 else "#e8a" if row["percent"] >= 70 else "#0a0"
            parts.append(
                f'<div style="font-size:11px">{row["label"]}: '
                f'<b style="color:{color}">{row["used"]}</b>/{row["allowed"]}</div>'
            )
        return format_html("".join(parts) or "—")

    @admin.display(description="روز مانده")
    def days_left(self, obj):
        return obj.days_left

    @admin.action(description="شروع دوره‌ی بعد")
    def roll_period(self, request, queryset):
        for sub in queryset:
            sub.roll_period()
        self.message_user(request, f"{queryset.count()} اشتراک به دوره‌ی بعد رفت.")

    @admin.action(description="فعال کردن")
    def mark_active(self, request, queryset):
        n = queryset.update(status=Subscription.Status.ACTIVE)
        self.message_user(request, f"{n} اشتراک فعال شد.")


@admin.register(Usage)
class UsageAdmin(admin.ModelAdmin):
    list_display = ["created_at", "store", "metric", "quantity", "state", "external", "detail"]
    list_filter = ["metric", "state", "external"]
    search_fields = ["store__name", "detail"]
    readonly_fields = [f.name for f in Usage._meta.fields]
