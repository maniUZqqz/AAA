from django.urls import path

from .views import (
    PlanListView,
    StoreSubscriptionView,
    StoreUsageHistoryView,
    StoreUsageView,
)

urlpatterns = [
    path("plans/", PlanListView.as_view(), name="plan-list"),
    path("stores/<int:pk>/usage/", StoreUsageView.as_view(), name="store-usage"),
    path("stores/<int:pk>/usage/history/", StoreUsageHistoryView.as_view(), name="store-usage-history"),
    path("stores/<int:pk>/subscription/", StoreSubscriptionView.as_view(), name="store-subscription"),
]
