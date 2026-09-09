from django.urls import path

from .views import JobCancelView, JobDetailView, JobListView

urlpatterns = [
    path("jobs/", JobListView.as_view(), name="job-list"),
    path("jobs/<int:pk>/", JobDetailView.as_view(), name="job-detail"),
    path("jobs/<int:pk>/cancel/", JobCancelView.as_view(), name="job-cancel"),
]
