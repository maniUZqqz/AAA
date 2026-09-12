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


class Membership(TimeStampedModel):
    """A person's seat in a store, with a role.

    `Store.owner` is not a row here. Ownership is the tenant's anchor — who
    pays and who can delete — and folding it into the membership table would
    make it possible to remove the last owner and orphan a paying store. The
    access layer treats the owner as OWNER without needing a row.
    """

    class Role(models.TextChoices):
        OWNER = "OWNER", "مالک"
        ADMIN = "ADMIN", "مدیر"
        MARKETING = "MARKETING", "بازاریابی"
        CONTENT_MANAGER = "CONTENT", "مدیر محتوا"
        SUPPORT = "SUPPORT", "پشتیبانی"
        VIEWER = "VIEWER", "بازدیدکننده"

    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="memberships")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="store_memberships")
    role = models.CharField(max_length=12, choices=Role.choices, default=Role.VIEWER)
    is_active = models.BooleanField(default=True)

    invited_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="+"
    )
    #: Removing access should be reversible and answerable ("who removed me?"),
    #: so a seat is deactivated rather than deleted.
    removed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["store", "user"], name="one_seat_per_user_per_store"),
        ]
        indexes = [models.Index(fields=["user", "is_active"])]
        ordering = ["store", "role", "id"]
        verbose_name = "عضو فروشگاه"
        verbose_name_plural = "اعضای فروشگاه"

    def __str__(self):
        return f"{self.user} @ {self.store} ({self.get_role_display()})"

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.store_id and self.user_id and self.store.owner_id == self.user_id:
            raise ValidationError(
                "مالک فروشگاه به‌صورت خودکار دسترسی کامل دارد و نیازی به عضویت ندارد."
            )


# The sales-agent settings live in their own module for size, but Django only
# discovers models imported from here.
from .agent_settings import SalesAgentSettings  # noqa: E402,F401
