from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from . import staleness
from .models import Job
from .serializers import JobSerializer
from apps.stores import access


class JobDetailView(generics.RetrieveAPIView):
    """One job. Dead rows are reaped on read so a poller always terminates."""

    serializer_class = JobSerializer

    def get_queryset(self):
        qs = Job.objects.filter(store__in=access.stores_for(self.request.user))
        staleness.reap(qs)
        return qs


class JobListView(generics.ListAPIView):
    serializer_class = JobSerializer

    def get_queryset(self):
        qs = Job.objects.filter(store__in=access.stores_for(self.request.user))
        # every listing reaps first: a panel that re-attaches on mount must
        # never latch onto a job that can no longer finish (beter.md v2 #1/#2)
        staleness.reap(qs)
        params = self.request.query_params
        state = params.get("state")
        if state:
            qs = qs.filter(state=state)
        # active=true → only jobs that are still in flight; lets the frontend
        # re-attach its progress polling after a page refresh (beter.md #2)
        if params.get("active") in ("true", "1"):
            qs = qs.filter(state__in=staleness.ACTIVE_STATES)
        job_type = params.get("type")
        if job_type:
            qs = qs.filter(type=job_type)
        for param, field in (("product_id", "context__product_id"), ("script_id", "context__script_id")):
            raw = params.get(param)
            if raw:
                try:
                    qs = qs.filter(**{field: int(raw)})
                except (TypeError, ValueError):
                    qs = qs.none()
        return qs


class JobCancelView(APIView):
    """POST /api/v1/jobs/{id}/cancel/ — let the user unstick a panel.

    The underlying Celery task cannot be killed reliably on Windows, so this
    marks the row CANCELLED: the UI stops polling and the button unlocks
    immediately, and a task that is still alive finds a CANCELLED row when it
    tries to finish.
    """

    def post(self, request, pk):
        job = Job.objects.filter(store__in=access.stores_for(request.user), pk=pk).first()
        if job is None:
            return Response(
                {"error": {"code": "not_found", "message": "این Job وجود ندارد."}},
                status=status.HTTP_404_NOT_FOUND,
            )
        if job.state in staleness.ACTIVE_STATES:
            job.state = Job.State.CANCELLED
            job.error = "توسط کاربر لغو شد."
            job.save(update_fields=["state", "error", "updated_at"])
        return Response(JobSerializer(job).data)
