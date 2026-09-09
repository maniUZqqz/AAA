"""
UpMarket — Django settings.

All infrastructure values are environment-driven (see ../.env.example) so the
same codebase runs on the dev machine (no AI services) and on the main system
(Ollama + ComfyUI + Redis installed) without code changes.
"""
from datetime import timedelta
from pathlib import Path
import os
import sys

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def env_bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}


def env_list(name: str, default: str = "") -> list[str]:
    raw = os.getenv(name, default)
    return [item.strip() for item in raw.split(",") if item.strip()]


def prefer_ipv4_localhost(url: str) -> str:
    """Rewrite a `localhost` URL to 127.0.0.1.

    On Windows `localhost` resolves to ::1 first. Ollama, ComfyUI and Redis all
    bind IPv4 only, so every single call first waits ~2 seconds for the IPv6
    attempt to be refused — measured here: 3 requests to http://localhost:11434
    took 6.16s, the same 3 to http://127.0.0.1:11434 took 0.05s. A job makes
    several such calls, so this is seconds of pure waiting per action.

    Only the literal host `localhost` is rewritten; an explicit ::1 or a remote
    host is left exactly as configured.
    """
    from urllib.parse import urlsplit, urlunsplit

    try:
        parts = urlsplit(url)
        if (parts.hostname or "").lower() != "localhost":
            return url
        netloc = "127.0.0.1" if parts.port is None else f"127.0.0.1:{parts.port}"
        if parts.username:
            credentials = parts.username + (f":{parts.password}" if parts.password else "")
            netloc = f"{credentials}@{netloc}"
        return urlunsplit((parts.scheme, netloc, parts.path, parts.query, parts.fragment))
    except ValueError:
        return url


# ---------------------------------------------------------------- core
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-insecure-key-change-on-main-system")
DEBUG = env_bool("DJANGO_DEBUG", True)
if not DEBUG and SECRET_KEY == "dev-insecure-key-change-on-main-system":
    from django.core.exceptions import ImproperlyConfigured

    raise ImproperlyConfigured(
        "DJANGO_SECRET_KEY must be set to a long random value when DJANGO_DEBUG=false "
        "(JWTs are signed with it)."
    )
ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS", "*")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # third-party
    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",
    "drf_spectacular",
    # UpMarket domains
    "apps.accounts",
    "apps.stores",
    "apps.products",
    "apps.jobs",
    "apps.ai",
    "apps.customers",
    "apps.content",
    "apps.campaigns",
    "apps.analytics",
    "apps.billing",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# ---------------------------------------------------------------- database
# Official database: Django's built-in SQLite (decision D2, revised) — zero
# setup on both the dev machine and the main system. If the project ever
# needs PostgreSQL (many concurrent users), only this block changes; the
# ORM models/migrations stay engine-agnostic.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": Path(os.getenv("SQLITE_PATH", BASE_DIR / "db.sqlite3")),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ---------------------------------------------------------------- i18n / static / media
LANGUAGE_CODE = "en-us"
TIME_ZONE = os.getenv("TIME_ZONE", "UTC")
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = Path(os.getenv("STATIC_ROOT", BASE_DIR / "staticfiles"))
MEDIA_URL = "/media/"
MEDIA_ROOT = Path(os.getenv("MEDIA_ROOT", BASE_DIR / "media"))

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Upload limits (uploads are untrusted input)
MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "10"))
DATA_UPLOAD_MAX_MEMORY_SIZE = MAX_UPLOAD_MB * 1024 * 1024
FILE_UPLOAD_MAX_MEMORY_SIZE = MAX_UPLOAD_MB * 1024 * 1024

# ---------------------------------------------------------------- production security
# Activated automatically when DJANGO_DEBUG=false on the deployment machine.
if not DEBUG:
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SESSION_COOKIE_SECURE = env_bool("SESSION_COOKIE_SECURE", False)
    CSRF_COOKIE_SECURE = env_bool("CSRF_COOKIE_SECURE", False)
    SECURE_SSL_REDIRECT = env_bool("SECURE_SSL_REDIRECT", False)
    SECURE_HSTS_SECONDS = int(os.getenv("SECURE_HSTS_SECONDS", "0"))
    X_FRAME_OPTIONS = "DENY"

# ---------------------------------------------------------------- logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{asctime} {levelname} [{name}] {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "verbose"},
    },
    "root": {"handlers": ["console"], "level": os.getenv("LOG_LEVEL", "INFO")},
    "loggers": {
        "django.request": {"level": "WARNING"},
        "services": {"level": "INFO"},
        "apps": {"level": "INFO"},
    },
}

# ---------------------------------------------------------------- DRF / auth
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    # `Response(None)` must serialise to the JSON literal `null`; DRF's stock
    # renderer emits zero bytes, which is not parseable JSON (apps.common.renderers)
    "DEFAULT_RENDERER_CLASSES": [
        "apps.common.renderers.NullableJSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": os.getenv("THROTTLE_ANON", "30/minute"),
        "user": os.getenv("THROTTLE_USER", "240/minute"),
    },
}

# Throttling off during automated tests (rate limits would make them flaky)
IS_TEST = "test" in sys.argv
if IS_TEST:
    REST_FRAMEWORK["DEFAULT_THROTTLE_CLASSES"] = []

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=12),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
}

SPECTACULAR_SETTINGS = {
    "TITLE": "UpMarket API",
    "DESCRIPTION": "AI Sales & Marketing Employee for online stores",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    # schema/docs are public in dev, authenticated-only in production
    "SERVE_PERMISSIONS": (
        ["rest_framework.permissions.AllowAny"]
        if DEBUG
        else ["rest_framework.permissions.IsAuthenticated"]
    ),
}

# ---------------------------------------------------------------- CORS
# Note: the vite dev server proxies /api same-origin, so CORS is only relevant
# when the frontend is served from a different origin.
_cors_origins = env_list("CORS_ALLOWED_ORIGINS")
if _cors_origins:
    CORS_ALLOWED_ORIGINS = _cors_origins
    CORS_ALLOW_CREDENTIALS = True
else:
    # dev convenience only; credentials stay off with a wildcard origin
    CORS_ALLOW_ALL_ORIGINS = DEBUG

# ---------------------------------------------------------------- Celery / Redis
CELERY_BROKER_URL = prefer_ipv4_localhost(os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0"))
CELERY_RESULT_BACKEND = CELERY_BROKER_URL


def _redis_is_up(url: str, timeout: float = 0.6) -> bool:
    """One TCP connect to the broker. Never raises."""
    import socket
    from urllib.parse import urlparse

    parsed = urlparse(url or "")
    try:
        with socket.create_connection(
            (parsed.hostname or "localhost", parsed.port or 6379), timeout=timeout
        ):
            return True
    except OSError:
        return False


# CELERY_TASK_ALWAYS_EAGER=auto (the default) picks the mode by looking at the
# machine instead of making the user edit .env: Redis up → real queue (video
# generation works); Redis down → run AI jobs inside the request so everything
# else still works. `true`/`false` still force a mode. (beter.md v2 #5)
_EAGER_RAW = os.getenv("CELERY_TASK_ALWAYS_EAGER", "auto").strip().lower()
if _EAGER_RAW in {"", "auto"}:
    CELERY_TASK_ALWAYS_EAGER = not _redis_is_up(CELERY_BROKER_URL)
    CELERY_MODE_SOURCE = "auto"
else:
    CELERY_TASK_ALWAYS_EAGER = _EAGER_RAW in {"1", "true", "yes", "on"}
    CELERY_MODE_SOURCE = "env"

if IS_TEST:  # tests must never depend on a Redis being up on the dev machine
    CELERY_TASK_ALWAYS_EAGER = True
    CELERY_MODE_SOURCE = "test"
CELERY_TASK_EAGER_PROPAGATES = True
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
# AI (Ollama) work and GPU (ComfyUI) work run on dedicated queues so heavy
# generation can be capped independently (GPU_CONCURRENCY_LIMIT).
CELERY_TASK_ROUTES = {
    "apps.content.tasks.generate_video_task": {"queue": "gpu"},
    "apps.content.tasks.generate_image_task": {"queue": "gpu"},
    "apps.ai.tasks.*": {"queue": "ai"},
    "apps.content.tasks.*": {"queue": "ai"},
    "apps.campaigns.tasks.*": {"queue": "ai"},
}

# ---------------------------------------------------------------- UpMarket AI stack
UPMARKET_AI = {
    "OLLAMA_BASE_URL": prefer_ipv4_localhost(
        os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    ),
    # cold call on the main system = model load from disk (1-3 min) + long
    # generation; 180 timed out intermittently (beter.md #2)
    "OLLAMA_TIMEOUT": int(os.getenv("OLLAMA_TIMEOUT", "600")),
    "OLLAMA_RETRIES": int(os.getenv("OLLAMA_RETRIES", "2")),
    "MODEL_REASONING": os.getenv("OLLAMA_MODEL_REASONING", "qwq:32b"),
    "MODEL_VISION": os.getenv("OLLAMA_MODEL_VISION", "qwen3-vl:30b"),
    "MODEL_CODER": os.getenv("OLLAMA_MODEL_CODER", "qwen3-coder:30b"),
    # tried in order when the preferred model is not installed or fails; any
    # name not actually pulled on the machine is skipped automatically
    "MODEL_FALLBACKS": env_list(
        "OLLAMA_MODEL_FALLBACKS",
        ",".join(
            [
                os.getenv("OLLAMA_MODEL_VISION", "qwen3-vl:30b"),
                os.getenv("OLLAMA_MODEL_CODER", "qwen3-coder:30b"),
            ]
        ),
    ),
    # false = fail on the first model instead of trying the next one
    "MODEL_FALLBACK_ENABLED": env_bool("OLLAMA_MODEL_FALLBACK", True),
    # how many models one call may try in total. 2 keeps the worst case at
    # roughly twice a timeout — a live sales chat must not spend half an hour
    # walking down the model list.
    "MODEL_MAX_ATTEMPTS": max(1, int(os.getenv("OLLAMA_MODEL_MAX_ATTEMPTS", "2"))),
    # How long Ollama keeps a model in VRAM after a call. VRAM safety comes
    # from explicitly evicting the OTHER models before heavy work (services.gpu),
    # so this can stay at Ollama's own 5m default: a shorter value would force
    # an 18 GB reload from disk (1-3 min) between two steps of the same demo.
    "OLLAMA_KEEP_ALIVE": os.getenv("OLLAMA_KEEP_ALIVE", "5m"),
    # context window per request; smaller = less KV cache = more room for
    # weights on the GPU. 0 = let Ollama decide.
    "OLLAMA_NUM_CTX": int(os.getenv("OLLAMA_NUM_CTX", "8192")),
    # Generation cap for JSON answers. A market analysis with competitors is a
    # genuinely long object: cutting this too low truncates the JSON and the
    # answer fails validation, which is far worse than the extra seconds.
    "OLLAMA_NUM_PREDICT_JSON": int(os.getenv("OLLAMA_NUM_PREDICT_JSON", "4096")),
    "COMFYUI_BASE_URL": prefer_ipv4_localhost(
        os.getenv("COMFYUI_BASE_URL", "http://127.0.0.1:8188")
    ),
    "COMFYUI_TIMEOUT": int(os.getenv("COMFYUI_TIMEOUT", "900")),
    "COMFYUI_POLL_INTERVAL": float(os.getenv("COMFYUI_POLL_INTERVAL", "2.0")),
    "VIDEO_SEGMENT_DURATION": int(os.getenv("VIDEO_SEGMENT_DURATION", "5")),
    "GPU_CONCURRENCY_LIMIT": int(os.getenv("GPU_CONCURRENCY_LIMIT", "1")),
    # single-GPU VRAM coordination: unload Ollama models before ComfyUI work
    # and free ComfyUI VRAM before/after heavy Ollama work (best-effort)
    "GPU_AUTO_UNLOAD": env_bool("GPU_AUTO_UNLOAD", True),
    "TTS_PROVIDER": os.getenv("TTS_PROVIDER", "edge"),
    "TTS_VOICE": os.getenv("TTS_VOICE", "fa-IR-FaridNeural"),
    "TTS_LANGUAGE": os.getenv("TTS_LANGUAGE", "fa"),
    # per-narration-language voices (edge-tts voice names)
    "TTS_VOICE_FA": os.getenv("TTS_VOICE_FA", os.getenv("TTS_VOICE", "fa-IR-FaridNeural")),
    "TTS_VOICE_EN": os.getenv("TTS_VOICE_EN", "en-US-ChristopherNeural"),
    # semantic product search — OFF until an embedding model is installed on
    # the main system; everything falls back to keyword retrieval when off
    "EMBEDDINGS_ENABLED": env_bool("EMBEDDINGS_ENABLED", False),
    "MODEL_EMBEDDING": os.getenv("OLLAMA_MODEL_EMBEDDING", "nomic-embed-text"),
}

# ---------------------------------------------------------------- web research
# General web search for competitor sites — proper, non-blocking providers only:
#   searxng = self-hosted metasearch (recommended; your own instance, never blocked)
#   brave   = official Brave Search API (free-tier key)
#   none    = marketplace sources only (Digikala/Torob)
UPMARKET_RESEARCH = {
    "WEB_SEARCH_PROVIDER": os.getenv("WEB_SEARCH_PROVIDER", "none").lower(),
    "SEARXNG_BASE_URL": prefer_ipv4_localhost(
        os.getenv("SEARXNG_BASE_URL", "http://127.0.0.1:8888")
    ).rstrip("/"),
    "BRAVE_API_KEY": os.getenv("BRAVE_API_KEY", ""),
}

# ---------------------------------------------------------------- publishing (n8n)
UPMARKET_PUBLISHING = {
    # NovinHub — managed Instagram publishing (https://novinhub.com/developers).
    # A per-store token on StoreProfile overrides this shared one.
    "NOVINHUB_BASE_URL": os.getenv("NOVINHUB_BASE_URL", "https://api.novinhub.com/token/v2"),
    "NOVINHUB_TOKEN": os.getenv("NOVINHUB_TOKEN", ""),
    "N8N_WEBHOOK_URL": os.getenv("N8N_WEBHOOK_URL", ""),
    "N8N_WEBHOOK_TOKEN": os.getenv("N8N_WEBHOOK_TOKEN", ""),
    # used to build absolute media URLs inside webhook payloads
    "PUBLIC_BASE_URL": os.getenv("PUBLIC_BASE_URL", "http://localhost:8000").rstrip("/"),
}
