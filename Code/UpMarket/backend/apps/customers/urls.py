from django.urls import path

from .views import (
    ChatView,
    ConversationListView,
    HandoffView,
    MessageListView,
    NotificationListView,
    NotificationReadView,
    OrderDecisionView,
    OrderListView,
    OrderReceiptView,
    TicketListView,
    TicketResolveView,
)

urlpatterns = [
    path("stores/<int:store_id>/chat/", ChatView.as_view(), name="store-chat"),
    path(
        "stores/<int:store_id>/conversations/",
        ConversationListView.as_view(),
        name="store-conversations",
    ),
    path("stores/<int:store_id>/orders/", OrderListView.as_view(), name="store-orders"),
    path("stores/<int:store_id>/tickets/", TicketListView.as_view(), name="store-tickets"),
    path("conversations/<int:pk>/messages/", MessageListView.as_view(), name="conversation-messages"),
    path("conversations/<int:pk>/handoff/", HandoffView.as_view(), name="conversation-handoff"),
    path("orders/<int:pk>/receipt/", OrderReceiptView.as_view(), name="order-receipt"),
    path(
        "orders/<int:pk>/confirm/",
        OrderDecisionView.as_view(),
        {"decision": "confirm"},
        name="order-confirm",
    ),
    path(
        "orders/<int:pk>/reject/",
        OrderDecisionView.as_view(),
        {"decision": "reject"},
        name="order-reject",
    ),
    path(
        "orders/<int:pk>/cancel/",
        OrderDecisionView.as_view(),
        {"decision": "cancel"},
        name="order-cancel",
    ),
    path("tickets/<int:pk>/resolve/", TicketResolveView.as_view(), name="ticket-resolve"),
    path("notifications/", NotificationListView.as_view(), name="notifications"),
    path("notifications/read-all/", NotificationReadView.as_view(), name="notifications-read-all"),
    path("notifications/<int:pk>/read/", NotificationReadView.as_view(), name="notification-read"),
]
