from django.db import models

from apps.ai.models import AIRequest
from apps.common.models import TimeStampedModel
from apps.products.models import Product, ProductVariant
from apps.stores.models import Store


class Customer(TimeStampedModel):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="customers")
    name = models.CharField(max_length=200, blank=True)
    phone = models.CharField(max_length=32, blank=True)
    external_id = models.CharField(max_length=100, blank=True)
    channel = models.CharField(max_length=32, default="web")
    metadata = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return self.name or f"Customer #{self.id}"


class Conversation(TimeStampedModel):
    class State(models.TextChoices):
        AI = "AI", "AI handling"
        HUMAN = "HUMAN", "Human handling"
        ESCALATED = "ESCALATED", "Escalated to human"
        RESOLVED = "RESOLVED", "Resolved"

    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="conversations")
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="conversations")
    state = models.CharField(max_length=12, choices=State.choices, default=State.AI)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return f"Conversation #{self.id} ({self.store.name})"


class Message(TimeStampedModel):
    class Role(models.TextChoices):
        CUSTOMER = "CUSTOMER", "Customer"
        AI = "AI", "AI agent"
        HUMAN = "HUMAN", "Human agent"

    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name="messages"
    )
    role = models.CharField(max_length=12, choices=Role.choices)
    text = models.TextField()
    intent = models.CharField(max_length=32, blank=True)
    grounding = models.JSONField(default=dict, blank=True)
    ai_request = models.ForeignKey(
        AIRequest, on_delete=models.SET_NULL, null=True, blank=True, related_name="+"
    )

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.role}: {self.text[:40]}"


class Order(TimeStampedModel):
    """Order foundation. Created ONLY from real database data, never AI claims.

    Lifecycle: DRAFT (AI creates from chat) → AWAITING_RECEIPT (payment info
    shared, customer must send the receipt) → AWAITING_APPROVAL (receipt
    uploaded, human must verify) → CONFIRMED / CANCELLED (human decision).
    """

    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        AWAITING_RECEIPT = "AWAITING_RECEIPT", "Awaiting payment receipt"
        AWAITING_APPROVAL = "AWAITING_APPROVAL", "Awaiting human approval"
        CONFIRMED = "CONFIRMED", "Confirmed"
        CANCELLED = "CANCELLED", "Cancelled"

    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="orders")
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="orders")
    conversation = models.ForeignKey(
        Conversation, on_delete=models.SET_NULL, null=True, blank=True, related_name="orders"
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    total = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order #{self.id} ({self.status})"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="+")
    variant = models.ForeignKey(
        ProductVariant, on_delete=models.PROTECT, null=True, blank=True, related_name="+"
    )
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=14, decimal_places=2)

    def __str__(self):
        return f"{self.quantity}× {self.product.name}"


class PaymentReceipt(TimeStampedModel):
    """A payment receipt image the customer sends for an order.

    The AI only COLLECTS the receipt; approving it (and the order) is always a
    human decision — the model never confirms payments.
    """

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending review"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="receipts")
    image = models.ImageField(upload_to="receipts/%Y/%m/")
    note = models.CharField(max_length=300, blank=True)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.PENDING)
    review_note = models.CharField(max_length=300, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Receipt #{self.id} for order #{self.order_id} [{self.status}]"


class SupportTicket(TimeStampedModel):
    """A tracked support issue/complaint, usually opened by the AI agent."""

    class Status(models.TextChoices):
        OPEN = "OPEN", "Open"
        IN_PROGRESS = "IN_PROGRESS", "In progress"
        RESOLVED = "RESOLVED", "Resolved"

    class Priority(models.TextChoices):
        NORMAL = "NORMAL", "Normal"
        URGENT = "URGENT", "Urgent"

    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="tickets")
    customer = models.ForeignKey(
        Customer, on_delete=models.SET_NULL, null=True, blank=True, related_name="tickets"
    )
    conversation = models.ForeignKey(
        Conversation, on_delete=models.SET_NULL, null=True, blank=True, related_name="tickets"
    )
    subject = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.OPEN)
    priority = models.CharField(max_length=12, choices=Priority.choices, default=Priority.NORMAL)
    resolution_note = models.TextField(blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Ticket #{self.id} ({self.status}): {self.subject[:40]}"


class Notification(TimeStampedModel):
    """In-app notification for the store owner — fired whenever the AI needs a
    human (escalation, receipt review, order approval, ticket, AI failure)."""

    class Type(models.TextChoices):
        ESCALATION = "ESCALATION", "Conversation escalated"
        ORDER = "ORDER", "New order"
        RECEIPT = "RECEIPT", "Payment receipt received"
        TICKET = "TICKET", "Support ticket"
        AI_ERROR = "AI_ERROR", "AI failure"

    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="notifications")
    type = models.CharField(max_length=16, choices=Type.choices)
    title = models.CharField(max_length=200)
    body = models.TextField(blank=True)
    # frontend route the bell links to, e.g. /stores/3/sales
    link = models.CharField(max_length=200, blank=True)
    context = models.JSONField(default=dict, blank=True)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["store", "is_read"])]

    def __str__(self):
        return f"[{self.type}] {self.title}"


def notify(store, type, title, body="", link="", context=None):
    """Create an owner notification. Never raises — a notification failure must
    not break the customer-facing flow it accompanies."""
    try:
        return Notification.objects.create(
            store=store, type=type, title=title, body=body, link=link, context=context or {}
        )
    except Exception:  # pragma: no cover - defensive
        import logging

        logging.getLogger(__name__).exception("Failed to create notification for store %s", store)
        return None
