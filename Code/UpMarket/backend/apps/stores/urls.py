from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import StoreViewSet
from .views_members import (
    StoreAgentSettingsView,
    StoreMembersView,
    StoreMemberView,
    StoreOnboardingView,
)

router = DefaultRouter()
router.register(r"stores", StoreViewSet, basename="store")

urlpatterns = router.urls + [
    path("stores/<int:pk>/members/", StoreMembersView.as_view(), name="store-members"),
    path(
        "stores/<int:pk>/members/<int:member_id>/",
        StoreMemberView.as_view(),
        name="store-member",
    ),
    path(
        "stores/<int:pk>/agent-settings/",
        StoreAgentSettingsView.as_view(),
        name="store-agent-settings",
    ),
    path(
        "stores/<int:pk>/onboarding/",
        StoreOnboardingView.as_view(),
        name="store-onboarding",
    ),
]
