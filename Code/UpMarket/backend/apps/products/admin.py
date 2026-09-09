from django.contrib import admin

from .models import Category, Product, ProductAttribute, ProductImage, ProductVariant


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0


class ProductAttributeInline(admin.TabularInline):
    model = ProductAttribute
    extra = 0


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 0


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "store", "price", "stock_status", "is_available", "created_at"]
    list_filter = ["stock_status", "is_available"]
    search_fields = ["name", "store__name", "sku"]
    inlines = [ProductImageInline, ProductAttributeInline, ProductVariantInline]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "store", "parent"]
