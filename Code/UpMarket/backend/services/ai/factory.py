"""Build the provider that should answer a capability right now.

Call sites ask for `text_provider()` or `vision_provider()` and get back
something with `.generate()` / `.generate_json()`. Whether that is the local
Ollama box or a paid API is decided by the ModelProvider rows in the admin,
so business logic never mentions a vendor.
"""
from __future__ import annotations

import logging

from . import providers
from .ollama import OllamaProvider
from .openai_compat import OpenAICompatProvider

logger = logging.getLogger(__name__)


def build(resolved: providers.Resolved):
    """Turn a resolved provider row into a usable client."""
    if resolved.kind == "OLLAMA":
        return OllamaProvider(base_url=resolved.base_url, timeout=resolved.timeout_s)
    if resolved.kind in ("OPENAI", "HTTP"):
        return OpenAICompatProvider(
            base_url=resolved.base_url,
            api_key=resolved.api_key,
            model=resolved.model_name,
            timeout=resolved.timeout_s,
            options=resolved.options,
        )
    raise ValueError(f"«{resolved.kind}» متن تولید نمی‌کند.")


def _for(capability: str):
    chosen = providers.primary(capability)
    if chosen is None:
        return OllamaProvider(), None
    logger.info(
        "%s → %s (%s · %s)",
        capability, chosen.name, chosen.kind, chosen.model_name,
    )
    return build(chosen), chosen


def text_provider():
    """Provider for reasoning, analysis, research, captions and scripts."""
    return _for(providers.TEXT)[0]


def vision_provider():
    """Provider that can read a product photo."""
    return _for(providers.VISION)[0]


def provider_for_task(task_type: str):
    """`services.ai.router` task type → client."""
    return _for(providers.TASK_CAPABILITY.get(task_type, providers.TEXT))[0]


def model_name_for(capability: str) -> str | None:
    """Which model will actually run — recorded on every AIRequest row."""
    chosen = providers.primary(capability)
    return chosen.model_name if chosen else None


def health(resolved: providers.Resolved) -> tuple[bool, str]:
    """Probe a provider without running a real job. Used by the admin action."""
    try:
        if resolved.kind == "OLLAMA":
            from services.net import is_listening

            if not is_listening(resolved.base_url):
                return False, f"چیزی روی {resolved.base_url} گوش نمی‌دهد."
            from . import models_registry

            found = models_registry.resolve_installed(resolved.model_name)
            if not found:
                return False, f"مدل «{resolved.model_name}» روی این Ollama نصب نیست."
            return True, f"مدل {found} آماده است."

        if resolved.kind == "COMFYUI":
            from services.net import is_listening

            if not is_listening(resolved.base_url):
                return False, f"ComfyUI روی {resolved.base_url} بالا نیست."
            return True, "ComfyUI پاسخ می‌دهد."

        if resolved.kind in ("OPENAI", "HTTP"):
            return build(resolved).health()

        if resolved.kind == "REPLICATE":
            from services.media.api_media import replicate_health

            return replicate_health(resolved)

    except Exception as exc:  # noqa: BLE001 — the admin wants the real reason
        return False, f"{type(exc).__name__}: {exc}"
    return False, f"نوع «{resolved.kind}» شناخته نشد."
