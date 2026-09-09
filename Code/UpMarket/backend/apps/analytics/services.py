"""Store analytics — real aggregations over existing data. Nothing is fabricated."""
from datetime import datetime, time, timedelta

from django.db.models import Avg, Count, F, Sum
from django.db.models.functions import TruncDate
from django.utils import timezone

from apps.ai.models import AIRequest
from apps.campaigns.models import Campaign, PublishJob
from apps.content.models import Caption, GeneratedImage, VideoScript
from apps.customers.models import Conversation, Message, Order, PaymentReceipt, SupportTicket
from apps.jobs.models import Job


def _window(days: int):
    """(today_local, aware start-of-oldest-day) — aligned with TruncDate's tz."""
    today = timezone.localdate()
    oldest = today - timedelta(days=days - 1)
    since = timezone.make_aware(
        datetime.combine(oldest, time.min), timezone.get_current_timezone()
    )
    return today, since


def _by_field(queryset, field):
    return {row[field]: row["n"] for row in queryset.values(field).annotate(n=Count("id"))}


def store_overview(store) -> dict:
    products = store.products.all()
    conversations = Conversation.objects.filter(store=store)
    orders = Order.objects.filter(store=store)
    ai_requests = AIRequest.objects.filter(store=store)
    jobs = Job.objects.filter(store=store)

    confirmed_revenue = (
        orders.filter(status=Order.Status.CONFIRMED).aggregate(s=Sum("total"))["s"] or 0
    )
    draft_value = orders.filter(status=Order.Status.DRAFT).aggregate(s=Sum("total"))["s"] or 0

    return {
        "products": {
            "total": products.count(),
            "available": products.filter(is_available=True).count(),
        },
        "conversations": {
            "total": conversations.count(),
            "by_state": _by_field(conversations, "state"),
            "messages": Message.objects.filter(conversation__store=store).count(),
        },
        "orders": {
            "total": orders.count(),
            "by_status": _by_field(orders, "status"),
            "confirmed_revenue": str(confirmed_revenue),
            "draft_value": str(draft_value),
        },
        "campaigns": {
            "total": Campaign.objects.filter(store=store).count(),
            "by_state": _by_field(Campaign.objects.filter(store=store), "approval_state"),
        },
        "publishing": {
            "total": PublishJob.objects.filter(store=store).count(),
            "by_status": _by_field(PublishJob.objects.filter(store=store), "status"),
        },
        "content": {
            "generated_images": GeneratedImage.objects.filter(store=store).count(),
            "captions": Caption.objects.filter(store=store).count(),
            "videos_ready": VideoScript.objects.filter(
                store=store, status=VideoScript.Status.READY
            ).count(),
        },
        "ai": {
            "requests": ai_requests.count(),
            "by_status": _by_field(ai_requests, "status"),
            "avg_latency_ms": round(
                ai_requests.aggregate(a=Avg("latency_ms"))["a"] or 0
            ),
        },
        "jobs": {
            "total": jobs.count(),
            "by_state": _by_field(jobs, "state"),
        },
    }


def store_timeseries(store, days: int = 14) -> dict:
    """Per-day counts for the last `days` days (conversations, orders, AI requests)."""
    days = max(1, min(90, days))
    today, since = _window(days)

    def daily(queryset):
        rows = (
            queryset.filter(created_at__gte=since)
            .annotate(day=TruncDate("created_at"))
            .values("day")
            .annotate(n=Count("id"))
        )
        return {row["day"].isoformat(): row["n"] for row in rows}

    conversations = daily(Conversation.objects.filter(store=store))
    orders = daily(Order.objects.filter(store=store))
    ai_requests = daily(AIRequest.objects.filter(store=store))

    series = []
    for offset in range(days - 1, -1, -1):
        day = (today - timedelta(days=offset)).isoformat()
        series.append(
            {
                "date": day,
                "conversations": conversations.get(day, 0),
                "orders": orders.get(day, 0),
                "ai_requests": ai_requests.get(day, 0),
            }
        )
    return {"days": days, "series": series}


def store_sales(store, days: int = 30) -> dict:
    """Sales & support dashboard data — real orders/receipts/tickets only."""
    days = max(1, min(90, days))
    today, since = _window(days)
    orders = Order.objects.filter(store=store)
    confirmed = orders.filter(status=Order.Status.CONFIRMED)

    # daily revenue (confirmed orders) + daily order counts
    revenue_rows = (
        confirmed.filter(created_at__gte=since)
        .annotate(day=TruncDate("created_at"))
        .values("day")
        .annotate(total=Sum("total"), n=Count("id"))
    )
    revenue_by_day = {row["day"].isoformat(): row for row in revenue_rows}
    order_rows = (
        orders.filter(created_at__gte=since)
        .annotate(day=TruncDate("created_at"))
        .values("day")
        .annotate(n=Count("id"))
    )
    orders_by_day = {row["day"].isoformat(): row["n"] for row in order_rows}
    series = []
    for offset in range(days - 1, -1, -1):
        day = (today - timedelta(days=offset)).isoformat()
        revenue_row = revenue_by_day.get(day)
        series.append(
            {
                "date": day,
                "orders": orders_by_day.get(day, 0),
                "confirmed_orders": revenue_row["n"] if revenue_row else 0,
                "revenue": str(revenue_row["total"]) if revenue_row else "0",
            }
        )

    # top products by confirmed quantity/revenue
    top_products = list(
        confirmed.values(name=F("items__product__name"))
        .annotate(
            quantity=Sum("items__quantity"),
            revenue=Sum(F("items__quantity") * F("items__unit_price")),
        )
        .exclude(name=None)
        .order_by("-revenue")[:10]
    )
    for row in top_products:
        row["revenue"] = str(row["revenue"] or 0)

    conversations_total = Conversation.objects.filter(store=store).count()
    orders_total = orders.count()
    revenue_total = confirmed.aggregate(s=Sum("total"))["s"] or 0
    return {
        "days": days,
        "orders": {"total": orders_total, "by_status": {
            row["status"]: row["n"]
            for row in orders.values("status").annotate(n=Count("id"))
        }},
        "revenue": {
            "confirmed_total": str(revenue_total),
            "confirmed_orders": confirmed.count(),
            "avg_order_value": str(
                round(revenue_total / confirmed.count(), 2) if confirmed.count() else 0
            ),
        },
        "conversion": {
            "conversations": conversations_total,
            "orders": orders_total,
            "rate_percent": round(orders_total / conversations_total * 100, 1)
            if conversations_total
            else 0,
        },
        "pending": {
            "receipts": PaymentReceipt.objects.filter(
                order__store=store, status=PaymentReceipt.Status.PENDING
            ).count(),
            "awaiting_approval": orders.filter(status=Order.Status.AWAITING_APPROVAL).count(),
            "open_tickets": SupportTicket.objects.filter(store=store)
            .exclude(status=SupportTicket.Status.RESOLVED)
            .count(),
        },
        "series": series,
        "top_products": top_products,
    }
