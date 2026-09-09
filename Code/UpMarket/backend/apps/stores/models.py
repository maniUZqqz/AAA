from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.common.models import TimeStampedModel
from apps.common.utils import unique_slug


class Store(TimeStampedModel):
    """Tenant boundary: every business object belongs to a Store."""

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="stores")
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, allow_unicode=True, blank=True)
    business_type = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    target_audience = models.CharField(max_length=255, blank=True)
    contact = models.JSONField(default=dict, blank=True)
    logo = models.ImageField(upload_to="stores/logos/", blank=True, null=True)
    colors = models.JSONField(default=dict, blank=True)
    social_links = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(Store, self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class StoreProfile(models.Model):
    """Brand voice, policies and AI preferences for a store."""

    store = models.OneToOneField(Store, on_delete=models.CASCADE, related_name="profile")
    brand_voice = models.CharField(max_length=100, blank=True)
    # NovinHub — publishing straight to the store's own Instagram. Left blank,
    # the shared .env token is used; left blank on both, publishing falls back
    # to the n8n webhook the owner wires up themselves.
    novinhub_token = models.CharField(
        max_length=255, blank=True,
        help_text="توکن اختصاصی نوین‌هاب این فروشگاه (اختیاری)",
    )
    novinhub_account_ids = models.JSONField(
        default=list, blank=True,
        help_text="شناسه‌ی اکانت‌های اینستاگرام که پست روی آن‌ها منتشر می‌شود",
    )
    tone = models.CharField(max_length=100, blank=True)
    content_style = models.CharField(max_length=100, blank=True)
    visual_preferences = models.JSONField(default=dict, blank=True)
    shipping_policy = models.TextField(blank=True)
    return_policy = models.TextField(blank=True)
    refund_policy = models.TextField(blank=True)
    payment_info = models.TextField(blank=True)
    business_rules = models.TextField(blank=True)
    working_hours = models.JSONField(default=dict, blank=True)
    ai_preferences = models.JSONField(default=dict, blank=True)
    publishing_preferences = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"Profile of {self.store.name}"


@receiver(post_save, sender=Store)
def create_store_profile(sender, instance, created, **kwargs):
    if created:
        StoreProfile.objects.get_or_create(store=instance)
