"""Plans and usage over the API — what the panel needs to draw its meters."""
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.stores.models import Store

from . import services
from .models import Plan, Subscription, Usage
from .serializers import PlanSerializer, SubscriptionSerializer, UsageSerializer


class PlanListView(APIView):
    """Public — the pricing page reads this, logged in or not."""

    permission_classes = [AllowAny]

    def get(self, request):
        plans = Plan.objects.filter(is_public=True).order_by("sort_order", "price_toman")
        return Response(PlanSerializer(plans, many=True).data)


def _owned_store(request, pk) -> Store:
    return get_object_or_404(Store, pk=pk, owner=request.user)


class StoreUsageView(APIView):
    """Live quota state for one store: plan, period and every meter."""

    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        store = _owned_store(request, pk)
        return Response(services.snapshot(store))


class StoreSubscriptionView(APIView):
    """Read the subscription, or switch plan."""

    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        store = _owned_store(request, pk)
        sub = Subscription.objects.filter(store=store).select_related("plan").first()
        if sub is None:
            return Response(None)
        return Response(SubscriptionSerializer(sub).data)

    def post(self, request, pk):
        """Choose a plan. Payment is a separate step — this only records intent."""
        store = _owned_store(request, pk)
        slug = str(request.data.get("plan") or "")
        plan = Plan.objects.filter(slug=slug, is_public=True).first()
        if plan is None:
            return Response(
                {"error": {"code": "unknown_plan", "message": "چنین پلنی وجود ندارد."}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        sub = services.subscription_for(store)
        sub.plan = plan
        # a paid plan starts as PAST_DUE until a payment is recorded, so the
        # quota gate cannot be opened by simply picking an expensive package
        sub.status = (
            Subscription.Status.ACTIVE if plan.price_toman == 0
            else Subscription.Status.PAST_DUE
        )
        sub.save(update_fields=["plan", "status", "updated_at"])
        return Response(SubscriptionSerializer(sub).data)


class StoreUsageHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        store = _owned_store(request, pk)
        rows = Usage.objects.filter(store=store).select_related("job")[:100]
        return Response(UsageSerializer(rows, many=True).data)
