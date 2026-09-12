"""The human half of incremental generation.

A job that stops after five seconds is only useful if there is somewhere to say
"yes, keep going" or "no, stop". These are those endpoints.

Rejecting is not the same as cancelling, and the difference is the credit:

* **reject** — this segment is wrong. The job stops, and because nothing usable
  came out of it, the credit goes back through the quality path
  (`apps.billing.credits`), which counts it as an attempt against the quality
  guarantee.
* **cancel** — I have changed my mind. Same refund, but not counted as a
  quality failure, because the model did nothing wrong.

Conflating them would either make our own quality numbers look terrible every
time someone changes their mind, or let genuine failures hide.
"""
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.stores import access

from . import cancellation, machine
from .models import Job
from .serializers import JobSerializer


def _job(request, pk, permission=access.CONTENT):
    store_ids = access.stores_for(request.user)
    job = Job.objects.filter(store__in=store_ids, pk=pk).select_related("store").first()
    if job is None:
        from django.http import Http404

        raise Http404("این Job وجود ندارد.")
    access.get_store(request.user, job.store_id, permission)
    return job


class JobApproveView(APIView):
    """POST /api/v1/jobs/{id}/approve/ — carry on from the preview."""

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        job = _job(request, pk)
        if not job.awaiting_human:
            return Response(
                {"error": {
                    "code": "not_awaiting_approval",
                    "message": f"این کار «{machine.label(job.state)}» است و تأیید نمی‌خواهد.",
                }},
                status=status.HTTP_409_CONFLICT,
            )
        job.advance(Job.State.APPROVED, label="تأیید شد — ادامه می‌دهیم")
        # Resuming is the pipeline's business, not the endpoint's: the task that
        # parked the job is the one that knows what comes next.
        from .resume import resume

        resume(job)
        job.refresh_from_db()
        return Response(JobSerializer(job).data)


class JobRejectView(APIView):
    """POST /api/v1/jobs/{id}/reject/ — this piece is wrong, stop.

    Counted against the quality guarantee, unlike cancel.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        job = _job(request, pk)
        if job.state in machine.TERMINAL:
            return Response(
                {"error": {"code": "already_finished", "message": "این کار تمام شده است."}},
                status=status.HTTP_409_CONFLICT,
            )

        reason = str(request.data.get("reason", "")).strip() or "فروشگاه‌دار خروجی را نپسندید"
        outcome = cancellation.cancel(job, actor=request.user, reason=reason)
        job.refresh_from_db()
        return Response({"job": JobSerializer(job).data, **outcome})


class JobModeView(APIView):
    """PATCH /api/v1/jobs/{id}/mode/ — switch between Safe and Auto mid-flight.

    Allowed while the job is still running because that is when the owner
    learns which one they wanted: the first approval prompt is what tells them
    whether they care to see the rest.
    """

    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        job = _job(request, pk)
        mode = request.data.get("mode")
        if mode not in Job.Mode.values:
            return Response(
                {"error": {"code": "bad_mode", "message": "حالت نامعتبر است."}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if job.state in machine.TERMINAL:
            return Response(
                {"error": {"code": "already_finished", "message": "این کار تمام شده است."}},
                status=status.HTTP_409_CONFLICT,
            )
        job.mode = mode
        job.save(update_fields=["mode", "updated_at"])
        return Response(JobSerializer(job).data)
