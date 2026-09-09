from django.db import models

from apps.common.models import TimeStampedModel
from apps.common.utils import unique_slug
from apps.stores.models import Store


class Category(TimeStampedModel):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="categories")
    name = models.CharField(max_length=100)
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="children"
    )

    class Meta:
        verbose_name_plural = "categories"
        constraints = [
            models.UniqueConstraint(fields=["store", "name", "parent"], name="uniq_category_per_store")
        ]

    def __str__(self):
        return self.name


class Product(TimeStampedModel):
    class StockStatus(models.TextChoices):
        IN_STOCK = "IN_STOCK", "In stock"
        OUT_OF_STOCK = "OUT_OF_STOCK", "Out of stock"
        PREORDER = "PREORDER", "Preorder"

    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="products")
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="products"
    )
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, allow_unicode=True, blank=True)
    sku = models.CharField(max_length=64, blank=True)
    description = models.TextField(blank=True)
    short_description = models.CharField(max_length=300, blank=True)
    brand = models.CharField(max_length=100, blank=True)
    price = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    compare_at_price = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=8, default="IRT")
    stock_quantity = models.PositiveIntegerField(default=0)
    stock_status = models.CharField(
        max_length=16, choices=StockStatus.choices, default=StockStatus.IN_STOCK
    )
    tags = models.JSONField(default=list, blank=True)
    shipping_info = models.JSONField(default=dict, blank=True)
    marketing_notes = models.TextField(blank=True)
    is_available = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["store", "created_at"])]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(Product, self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.store.name})"


class ProductVariant(TimeStampedModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="variants")
    name = models.CharField(max_length=100)
    attributes = models.JSONField(default=dict, blank=True)
    price_override = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    stock_quantity = models.PositiveIntegerField(default=0)
    sku = models.CharField(max_length=64, blank=True)

    def __str__(self):
        return f"{self.product.name} / {self.name}"


class ProductAttribute(models.Model):
    """Key/value specs — port of the legacy `ProductFeature` model."""

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="attributes")
    key = models.CharField(max_length=100)
    value = models.CharField(max_length=300)

    def __str__(self):
        return f"{self.key}: {self.value}"


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="products/images/")
    is_main = models.BooleanField(default=False)
    alt_text = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"Image {self.id} of {self.product.name}"
