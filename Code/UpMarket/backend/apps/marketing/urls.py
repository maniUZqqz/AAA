from django.urls import path

from .event_views import EventIngestView
from .views import LeadCreateView

urlpatterns = [
    path("leads/", LeadCreateView.as_view(), name="lead-create"),
    path("events/", EventIngestView.as_view(), name="event-ingest"),
]
