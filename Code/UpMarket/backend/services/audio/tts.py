"""Replaceable TTS provider layer (Phase 13).

Default: edge-tts (Microsoft neural voices — real Persian support, verified with
fa-IR-FaridNeural). gTTS remains as a fallback engine but does NOT support
Persian, so it validates its language up front instead of failing mid-pipeline.
"""
from pathlib import Path

from django.conf import settings


class TTSError(Exception):
    pass


class BaseTTSProvider:
    name = "base"

    def synthesize(self, text: str, out_path) -> Path:  # pragma: no cover - interface
        raise NotImplementedError


SUPPORTED_LANGUAGES = ("fa", "en")


def voice_for_language(language: str) -> str:
    """Edge voice for a narration language ('fa' or 'en'), from settings."""
    conf = settings.UPMARKET_AI
    if language == "en":
        return conf.get("TTS_VOICE_EN", "en-US-ChristopherNeural")
    return conf.get("TTS_VOICE_FA", conf.get("TTS_VOICE", "fa-IR-FaridNeural"))


class EdgeTTSProvider(BaseTTSProvider):
    """Microsoft Edge neural TTS (needs internet). Persian: fa-IR-FaridNeural / fa-IR-DilaraNeural."""

    name = "edge"

    def __init__(self, voice=None):
        self.voice = voice or settings.UPMARKET_AI.get("TTS_VOICE", "fa-IR-FaridNeural")

    def synthesize(self, text: str, out_path) -> Path:
        try:
            import asyncio

            import edge_tts
        except ImportError as exc:
            raise TTSError("edge-tts is not installed — pip install edge-tts") from exc
        out = Path(out_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        try:
            communicate = edge_tts.Communicate(text, self.voice)
            asyncio.run(communicate.save(str(out)))
        except Exception as exc:  # network / voice errors
            raise TTSError(f"edge-tts synthesis failed (voice={self.voice}): {exc}") from exc
        if not out.exists() or out.stat().st_size == 0:
            raise TTSError("edge-tts produced no audio")
        return out


class GTTSProvider(BaseTTSProvider):
    """Google Translate TTS. NOTE: does not support Persian ('fa') — validated up front."""

    name = "gtts"

    def __init__(self, language=None):
        self.language = language or settings.UPMARKET_AI.get("TTS_LANGUAGE", "fa")
        try:
            from gtts.lang import tts_langs
        except ImportError as exc:
            raise TTSError("gTTS is not installed — pip install gTTS") from exc
        supported = tts_langs()
        if self.language not in supported:
            raise TTSError(
                f"gTTS does not support language '{self.language}' (Persian is NOT supported). "
                f"Use TTS_PROVIDER=edge for Persian voices."
            )

    def synthesize(self, text: str, out_path) -> Path:
        from gtts import gTTS

        out = Path(out_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        try:
            gTTS(text=text, lang=self.language).save(str(out))
        except Exception as exc:
            raise TTSError(f"gTTS synthesis failed: {exc}") from exc
        if not out.exists() or out.stat().st_size == 0:
            raise TTSError("gTTS produced no audio")
        return out


def get_tts_provider(language: str | None = None) -> BaseTTSProvider:
    """TTS provider, optionally bound to a narration language ('fa'/'en')."""
    name = settings.UPMARKET_AI.get("TTS_PROVIDER", "edge").lower()
    if language is not None and language not in SUPPORTED_LANGUAGES:
        raise TTSError(f"Unsupported TTS language '{language}' — supported: {SUPPORTED_LANGUAGES}")
    if name == "edge":
        return EdgeTTSProvider(voice=voice_for_language(language) if language else None)
    if name == "gtts":
        return GTTSProvider(language=language)
    raise TTSError(f"Unknown TTS provider '{name}' — supported: edge, gtts")
