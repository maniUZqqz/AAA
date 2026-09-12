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
if not DEBUG and ALLOWED_HOSTS == ["*"]:
    from django.core.exceptions import ImproperlyConfigured

    raise ImproperlyConfigured(
        "DJANGO_ALLOWED_HOSTS نمی‌تواند در production برابر * باشد — "
        "دامنه‌های واقعی را بنویسید."
    )

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
    "apps.marketing",
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
# SQLite for development, PostgreSQL for production.
#
# SQLite takes a single writer at a time. That is fine for one developer and
# fatal for the target architecture: hundreds of shops, Celery workers, and
# long-running jobs all writing at once. The capacity model sells 283
# concurrent customers, so the database has to survive them.
#
# Set DATABASE_URL and Postgres is used; leave it empty and SQLite is, with no
# other change anywhere. Migrations stay engine-agnostic either way.
DATABASE_URL = os.getenv("DATABASE_URL", "").strip()

if DATABASE_URL:
    from urllib.parse import unquote, urlparse

    _db = urlparse(DATABASE_URL)
    if _db.scheme not in ("postgres", "postgresql"):
        from django.core.exceptions import ImproperlyConfigured

        raise ImproperlyConfigured(
            f"DATABASE_URL scheme «{_db.scheme}» پشتیبانی نمی‌شود — postgres:// لازم است."
        )
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": (_db.path or "/upmarket").lstrip("/"),
            "USER": unquote(_db.username or ""),
            "PASSWORD": unquote(_db.password or ""),
            "HOST": _db.hostname or "127.0.0.1",
            "PORT": str(_db.port or 5432),
            # Reuse connections instead of opening one per request. Under
            # Celery + web workers this is the difference between a handful of
            # connections and hundreds.
            "CONN_MAX_AGE": int(os.getenv("DB_CONN_MAX_AGE", "60")),
            "CONN_HEALTH_CHECKS": True,
            "OPTIONS": {
                "connect_timeout": int(os.getenv("DB_CONNECT_TIMEOUT", "10")),
            },
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": Path(os.getenv("SQLITE_PATH", BASE_DIR / "db.sqlite3")),
            "OPTIONS": {
                # WAL lets readers work while one writer holds the lock, and a
                # busy timeout turns "database is locked" into a short wait
                # rather than an instant error. Both only matter in dev, but
                # they make dev behave a little more like production.
                "init_command": "PRAGMA journal_mode=WAL; PRAGMA busy_timeout=5000;",
            },
        }
    }

# Refuse to run production on SQLite. Getting this wrong is silent until the
# first concurrent write, and by then there are real customers on it.
if not DEBUG and not DATABASE_URL:
    import warnings

    warnings.warn(
        "DJANGO_DEBUG=false ولی DATABASE_URL تنظیم نشده — production روی SQLite "
        "اجرا می‌شود. برای PostgreSQL مقدار DATABASE_URL را بگذارید.",
        RuntimeWarning,
        stacklevel=2,
    )

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
        # The public contact form is the only anonymous write endpoint we have.
        # A person sends one message; anything near this ceiling is a script.
        "lead": os.getenv("THROTTLE_LEAD", "5/hour"),
        # Analytics is batched, so a real visit is a handful of requests.
        "event": os.getenv("THROTTLE_EVENT", "120/hour"),
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

# Behind a TLS-terminating proxy Django sees plain HTTP, so it rejects admin
# POSTs whose Origin says https unless the origin is listed here. Symptom is a
# 403 on login that looks like a wrong password.
CSRF_TRUSTED_ORIGINS = env_list("CSRF_TRUSTED_ORIGINS")

# Trust the proxy's protocol header so `request.is_secure()` is right; without
# it secure cookies are never set and an SSL redirect loops.
if env_bool("USE_PROXY_SSL_HEADER", not DEBUG):
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# ---------------------------------------------------------------- Celery / Redis
# CELERY_BROKER_URL is what compose sets and what Celery's own docs use;
# REDIS_URL is kept because start.bat and the dev machine already use it.
# Reading only one of the two meant the deployed workers silently fell back to
# localhost and found no broker.
CELERY_BROKER_URL = prefer_ipv4_localhost(
    os.getenv("CELERY_BROKER_URL")
    or os.getenv("REDIS_URL")
    or "redis://127.0.0.1:6379/0"
)
CELERY_RESULT_BACKEND = prefer_ipv4_localhost(
    os.getenv("CELERY_RESULT_BACKEND") or CELERY_BROKER_URL
)


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

# ---------------------------------------------------------------- payments
# Gateway credentials. With none of these set the product still runs: the only
# offered method is a bank transfer a human confirms, which is what the
# business does today.
UPMARKET_PAYMENT = {
    "ZARINPAL_MERCHANT_ID": os.getenv("ZARINPAL_MERCHANT_ID", ""),
    "ZARINPAL_SANDBOX": env_bool("ZARINPAL_SANDBOX", False),
    "MANUAL_ACCOUNT_INFO": os.getenv("MANUAL_ACCOUNT_INFO", ""),
    "DEFAULT_PROVIDER": os.getenv("PAYMENT_DEFAULT_PROVIDER", ""),
    "PERIOD_DAYS": int(os.getenv("BILLING_PERIOD_DAYS", "30")),
    # Days a lapsed subscription keeps working. Cutting someone off the moment
    # a renewal fails loses customers whose card simply expired.
    "GRACE_DAYS": int(os.getenv("BILLING_GRACE_DAYS", "3")),
    # Where the gateway sends the browser back to.
    "CALLBACK_BASE": os.getenv("PAYMENT_CALLBACK_BASE", "http://127.0.0.1:8000"),
    "PANEL_URL": os.getenv("PANEL_URL", "http://127.0.0.1:5173"),
}

# ---------------------------------------------------------------- UpMarket AI stack
UPMARKET_AI = {
    # --- API mode ------------------------------------------------------
    # Setting AI_API_BASE_URL flips text+vision from the local Ollama box to
    # any OpenAI-compatible API (Metis, AvalAI, Liara, OpenAI itself). This is
    # the .env shortcut for what ModelProvider rows already do in the admin —
    # so a machine with no GPU can run the whole product. Admin rows still win
    # when they exist; this only replaces the built-in default.
    "AI_API_BASE_URL": os.getenv("AI_API_BASE_URL", "").rstrip("/"),
    "AI_API_KEY": os.getenv("AI_API_KEY", ""),
    "AI_API_MODEL_TEXT": os.getenv("AI_API_MODEL_TEXT", "gpt-4o-mini"),
    "AI_API_MODEL_VISION": os.getenv("AI_API_MODEL_VISION", "gpt-4o-mini"),
    "AI_API_TIMEOUT": int(os.getenv("AI_API_TIMEOUT", "180")),
    # Data policy for stores that have not chosen one (apps.ai.StoreAIPolicy).
    # HYBRID = any active provider may answer, which is how every install
    # behaved before the policy layer existed. An operator who promises local
    # processing to every customer sets LOCAL_ONLY here and means it.
    "AI_DEFAULT_POLICY": os.getenv("AI_DEFAULT_POLICY", "HYBRID").upper(),
    # Quality guarantee: how many goes at one output before it stops being
    # charged for (apps.billing.credits). One miss is luck, two a coincidence,
    # three means the model cannot do this job today.
    "QUALITY_MAX_ATTEMPTS": int(os.getenv("QUALITY_MAX_ATTEMPTS", "3")),
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
