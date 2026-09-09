"""Capability → provider resolution.

Business logic asks "who can do TEXT?" and gets an ordered list of resolved
providers. It never learns whether the answer came from the RTX 3060 in the
next room or from a paid API, which is the whole point: swapping the two is
an admin decision (apps.ai.models.ModelProvider), not a code change.

When no provider row exists for a capability the configured `.env` defaults
are returned instead, so an untouched install behaves exactly as before.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field

from django.conf import settings

logger = logging.getLogger(__name__)

TEXT = "TEXT"
VISION = "VISION"
IMAGE = "IMAGE"
VIDEO = "VIDEO"

# task type used by services.ai.router → capability
TASK_CAPABILITY = {"REASONING": TEXT, "CODE": TEXT, "VISION": VISION}


@dataclass(frozen=True)
class Resolved:
    """One usable way to serve a capability."""

    capability: str
    kind: str
    name: str
    base_url: str
    api_key: str
    model_name: str
    timeout_s: int
    options: dict = field(default_factory=dict)
    is_local: bool = True
    row_id: int | None = None

    @property
    def uses_gpu(self) -> bool:
        """Local work consumes our own GPU minutes; remote work does not."""
        return self.is_local


def _conf() -> dict:
    return settings.UPMARKET_AI


def _default_for(capability: str) -> Resolved | None:
    """The provider implied by .env when the database has no rows."""
    conf = _conf()
    if capability in (TEXT, VISION):
        key = "MODEL_VISION" if capability == VISION else "MODEL_REASONING"
        return Resolved(
            capability=capability,
            kind="OLLAMA",
            name="Ollama (پیش‌فرض .env)",
            base_url=conf["OLLAMA_BASE_URL"],
            api_key="",
            model_name=conf[key],
            timeout_s=int(conf.get("OLLAMA_TIMEOUT", 600)),
            is_local=True,
        )
    if capability in (IMAGE, VIDEO):
        return Resolved(
            capability=capability,
            kind="COMFYUI",
            name="ComfyUI (پیش‌فرض .env)",
            base_url=conf["COMFYUI_BASE_URL"],
            api_key="",
            model_name="flux_txt2img@v1" if capability == IMAGE else "wan22_i2v@v1",
            timeout_s=int(conf.get("COMFYUI_TIMEOUT", 900)),
            is_local=True,
        )
    return None


def _from_row(row) -> Resolved:
    conf = _conf()
    base = row.base_url or (
        conf["OLLAMA_BASE_URL"] if row.kind == "OLLAMA"
        else conf["COMFYUI_BASE_URL"] if row.kind == "COMFYUI"
        else ""
    )
    return Resolved(
        capability=row.capability,
        kind=row.kind,
        name=row.name,
        base_url=base,
        api_key=row.api_key,
        model_name=row.model_name,
        timeout_s=row.timeout_s,
        options=row.options or {},
        is_local=row.is_local,
        row_id=row.pk,
    )


def candidates(capability: str) -> list[Resolved]:
    """Every active provider for this capability, best first. Never empty."""
    from apps.ai.models import ModelProvider

    try:
        rows = list(
            ModelProvider.objects.filter(capability=capability, is_active=True)
            .order_by("priority", "id")
        )
    except Exception as exc:  # table missing during an early migration
        logger.info("Could not read providers (%s); using .env defaults", exc)
        rows = []

    resolved = [_from_row(row) for row in rows]
    if not resolved:
        fallback = _default_for(capability)
        return [fallback] if fallback else []
    return resolved


def primary(capability: str) -> Resolved | None:
    """The provider that should answer first."""
    found = candidates(capability)
    return found[0] if found else None


def uses_own_gpu(capability: str) -> bool:
    """Does this capability currently run on our hardware?

    Capacity planning depends on the answer: a capability served by an API
    costs money per call but zero GPU minutes, so it does not compete for the
    single GPU slot.
    """
    chosen = primary(capability)
    return bool(chosen and chosen.uses_gpu)


def summary() -> list[dict]:
    """What is serving each capability right now — for the admin and API."""
    from apps.ai.models import ModelProvider

    out = []
    for capability, label in ModelProvider.Capability.choices:
        found = candidates(capability)
        chosen = found[0] if found else None
        out.append({
            "capability": capability,
            "label": label,
            "provider": chosen.name if chosen else None,
            "kind": chosen.kind if chosen else None,
            "model": chosen.model_name if chosen else None,
            "local": chosen.is_local if chosen else None,
            "fallbacks": len(found) - 1 if found else 0,
        })
    return out
