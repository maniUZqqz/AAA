"""Queueing helpers: dispatch a Celery task, or fail honestly and immediately.

The worst possible outcome for the UI is a job row that stays QUEUED forever
because nothing is consuming the queue — that is exactly what produced the
"infinite spinner" bug. So every dispatch first checks that somebody is
actually listening, and a failed dispatch always leaves the job in a terminal
state with a message the store owner can act on.
"""
import logging
import socket
import time
from urllib.parse import urlparse

from django.conf import settings
from rest_framework import status
from rest_framework.response import Response

from .serializers import JobSerializer

logger = logging.getLogger(__name__)

# Redis presence is probed at most this often; a probe is a TCP connect.
_BROKER_CACHE_SECONDS = 10
_broker_cache = {"at": 0.0, "up": False}

QUEUE_SETUP_HINT = (
    "برای روشن‌کردن صف: فایل install-redis.bat را در پوشهٔ پروژه اجرا کنید "
    "(Redis را خودکار دانلود و نصب می‌کند)، بعد پروژه را با start.bat بالا بیاورید. "
    "نیازی به تغییر دستی backend/.env نیست."
)


def broker_host_port() -> tuple[str, int]:
    parsed = urlparse(settings.CELERY_BROKER_URL or "")
    return (parsed.hostname or "localhost", parsed.port or 6379)


def broker_reachable(force: bool = False) -> bool:
    """True when a TCP connection to the Redis broker succeeds (cached ~10s)."""
    now = time.monotonic()
    if not force and now - _broker_cache["at"] < _BROKER_CACHE_SECONDS:
        return _broker_cache["up"]
    host, port = broker_host_port()
    try:
        with socket.create_connection((host, port), timeout=0.6):
            up = True
    except OSError:
        up = False
    _broker_cache.update({"at": now, "up": up})
    return up


def queue_is_available() -> bool:
    """True when jobs are dispatched to real Celery workers over a live broker."""
    if settings.CELERY_TASK_ALWAYS_EAGER:
        return False
    return broker_reachable()


def queue_unavailable_response(job=None, message: str = ""):
    """Uniform 503 for 'this feature needs the queue and the queue is down'."""
    payload = {
        "error": {
            "code": "queue_unavailable",
            "message": message
            or ("صف پردازش (Redis) در دسترس نیست. " + QUEUE_SETUP_HINT),
        }
    }
    if job is not None:
        payload["job"] = JobSerializer(job).data
    return Response(payload, status=status.HTTP_503_SERVICE_UNAVAILABLE)


def dispatch_job(job, task, *args):
    """Queue `task(*args)` for `job`. Returns None on success, or a DRF Response.

    In queue mode the broker is probed first: without that check a dead Redis
    turns into a job that is QUEUED forever and a spinner that never stops.
    """
    if not settings.CELERY_TASK_ALWAYS_EAGER and not broker_reachable():
        job.mark_failed(
            "صف پردازش (Redis) در دسترس نیست، پس این کار اجرا نشد. " + QUEUE_SETUP_HINT
        )
        return queue_unavailable_response(job)

    try:
        async_result = task.delay(*args)
        job.celery_task_id = str(getattr(async_result, "id", "") or "")
        job.save(update_fields=["celery_task_id", "updated_at"])
        return None
    except Exception as exc:  # broker unavailable → honest failure, no fake success
        logger.warning("Dispatch of %s failed: %s", getattr(task, "name", task), exc)
        job.mark_failed(f"اجرای این کار شروع نشد ({exc}). " + QUEUE_SETUP_HINT)
        return queue_unavailable_response(job)
