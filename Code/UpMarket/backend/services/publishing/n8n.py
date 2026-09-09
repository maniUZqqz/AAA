"""n8n webhook delivery — the only place that talks to the automation layer."""
import logging
import time

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class PublishError(Exception):
    pass


def send_to_n8n(payload: dict, *, url=None, token=None, timeout=30, retries=2, backoff=2.0) -> dict:
    """POST a content package to the configured n8n webhook. Returns response data."""
    conf = settings.UPMARKET_PUBLISHING
    url = url or conf["N8N_WEBHOOK_URL"]
    token = token if token is not None else conf["N8N_WEBHOOK_TOKEN"]
    if not url:
        raise PublishError(
            "N8N_WEBHOOK_URL is not configured — set it in backend/.env"
        )
    headers = {"Content-Type": "application/json"}
    if token:
        headers["X-Upmarket-Token"] = token

    last_error = None
    for attempt in range(retries + 1):
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=timeout)
            response.raise_for_status()
            try:
                return {"status_code": response.status_code, "body": response.json()}
            except ValueError:
                return {"status_code": response.status_code, "body": response.text[:500]}
        except requests.Timeout as exc:
            # the request MAY have reached n8n — never retry a non-idempotent publish
            raise PublishError(
                f"n8n webhook timed out after {timeout}s — the post may or may not have "
                "gone out; check n8n executions before retrying."
            ) from exc
        except requests.HTTPError as exc:
            detail = getattr(exc.response, "text", "")[:500]
            status_code = getattr(exc.response, "status_code", 0)
            if status_code >= 500:
                # n8n may have partially executed — do not auto-retry
                raise PublishError(
                    f"n8n returned {status_code} — check n8n executions before retrying. {detail}"
                ) from exc
            last_error = PublishError(f"n8n delivery failed ({status_code}): {detail}")
            logger.warning("n8n error (attempt %s/%s): %s", attempt + 1, retries + 1, exc)
        except requests.RequestException as exc:
            # connection never established — safe to retry
            last_error = PublishError(f"n8n delivery failed: {exc}")
            logger.warning("n8n error (attempt %s/%s): %s", attempt + 1, retries + 1, exc)
        if attempt < retries:
            time.sleep(backoff * (2**attempt))
    raise last_error
