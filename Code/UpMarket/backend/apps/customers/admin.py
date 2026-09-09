from django.contrib import admin

from .models import (
    Conversation,
    Customer,
    Message,
    Notification,
    Order,
    OrderItem,
    PaymentReceipt,
    SupportTicket,
)


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ["role", "text", "intent", "grounding", "created_at"]


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ["id", "store", "customer", "state", "updated_at"]
    list_filter = ["state"]
    inlines = [MessageInline]


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "store", "channel", "created_at"]


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


class PaymentReceiptInline(admin.TabularInline):
    model = PaymentReceipt
    extra = 0
    readonly_fields = ["image", "note", "status", "review_note", "reviewed_at", "created_at"]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "store", "customer", "status", "total", "created_at"]
    list_filter = ["status"]
    inlines = [OrderItemInline, PaymentReceiptInline]


@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ["id", "store", "subject", "status", "priority", "created_at"]
    list_filter = ["status", "priority"]


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ["id", "store", "type", "title", "is_read", "created_at"]
    list_filter = ["type", "is_read"]
