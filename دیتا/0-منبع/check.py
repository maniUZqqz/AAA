# -*- coding: utf-8 -*-
"""
تطبیق data.json با کد واقعی پروژه.

    python check.py        # خروج با کد ۱ اگر ناسازگاری باشد

هر بار که کد عوض شد این را اجرا کن. اگر قرمز شد، یعنی ارائه چیزی می‌گوید
که دیگر در کد درست نیست — یکی از آن دو باید اصلاح شود.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CODE = HERE.parent.parent / "Code" / "UpMarket"
DATA = json.loads((HERE / "data.json").read_text(encoding="utf-8"))

SKIP = ("__pycache__", "node_modules", ".git")


def count(pattern: str, sub: str, glob: str = "*.py") -> int:
    """چند بار یک الگو در زیرشاخه‌ی داده‌شده دیده می‌شود."""
    total = 0
    root = CODE / sub
    if not root.exists():
        return -1
    for path in root.rglob(glob):
        if any(s in str(path) for s in SKIP):
            continue
        try:
            total += len(re.findall(pattern, path.read_text(encoding="utf-8", errors="ignore")))
        except OSError:
            pass
    return total


def count_tests() -> int:
    """تست‌های واقعی — فقط داخل فایل‌هایی که Django کشف می‌کند (tests*.py).

    شمارش متنی `def test_` روی کل backend اشتباه بود: اکشن ادمین
    `admin_providers.py:test_connection` را هم تست حساب می‌کرد و عدد را
    یکی بیشتر نشان می‌داد (۲۱۵ به‌جای ۲۱۴).
    """
    return count(r"def test_", "backend", glob="tests*.py")


def read(rel: str) -> str:
    path = CODE / rel
    return path.read_text(encoding="utf-8", errors="ignore") if path.exists() else ""


def stat(label: str):
    """مقدار یک آمار محصول را از data.json برمی‌دارد."""
    return next(s["value"] for s in DATA["product"]["stats"] if label in s["label"])


def main() -> int:
    settings = read("backend/config/settings.py")
    views = read("backend/apps/content/views.py")
    app_tsx = read("frontend/src/App.tsx")

    apps_dir = CODE / "backend" / "apps"
    domains = sorted(
        p.name for p in apps_dir.iterdir()
        if p.is_dir() and p.name not in ("__pycache__", "common")
    ) if apps_dir.exists() else []

    workflows = sorted(
        p.stem for p in (CODE / "backend/services/comfyui/workflows").glob("*_v1.json")
    )

    fa_digits = str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789")
    tests_claimed = int(stat("تست").translate(fa_digits))
    domains_claimed = int(stat("دامنه").translate(fa_digits))

    r = DATA["render"]
    checks = [
        # ── آمار محصول ───────────────────────────────────────────────
        # فقط داخل فایل‌های tests*.py می‌شماریم — وگرنه اکشن‌های ادمین مثل
        # apps/ai/admin_providers.py:test_connection هم تست حساب می‌شوند.
        ("تعداد تست", count_tests() == tests_claimed,
         f"کد {count_tests()} · داده {tests_claimed}"),
        ("تعداد دامنه بک‌اند", len(domains) == domains_claimed,
         f"کد {len(domains)} · داده {domains_claimed}"),
        ("سه ورک‌فلوی نسخه‌دار ComfyUI", len(workflows) == 3,
         " · ".join(workflows)),

        # ── پشته فناوری ──────────────────────────────────────────────
        ("مدل استدلال qwq:32b", "qwq:32b" in settings, "settings.py"),
        ("مدل بینایی qwen3-vl:30b", "qwen3-vl:30b" in settings, "settings.py"),
        ("صدای فارسی edge-tts", "fa-IR-FaridNeural" in settings, "settings.py"),
        ("انتشار با n8n", "N8N_WEBHOOK_URL" in settings, "settings.py"),

        # ── محدودیت‌هایی که پایه‌ی مدل ظرفیت‌اند ──────────────────────
        ("هم‌زمانی GPU برابر ۱",
         f'GPU_CONCURRENCY_LIMIT", "{1}"' in settings,
         "اگر بیشتر شود، محاسبه‌ی ظرفیت باید بازنویسی شود"),
        ("طول قطعه ویدیو",
         f'VIDEO_SEGMENT_DURATION", "{r["segment_sec"]}"' in settings,
         f'داده می‌گوید {r["segment_sec"]} ثانیه'),
        ("سقف طول یک ویدیو",
         f'min({r["max_single_video_sec"]}, total_duration)' in views,
         f'داده می‌گوید {r["max_single_video_sec"]} ثانیه'),
        ("کف طول یک ویدیو",
         f'max({r["min_single_video_sec"]}, min(' in views,
         f'داده می‌گوید {r["min_single_video_sec"]} ثانیه'),

        # ── فرانت ────────────────────────────────────────────────────
        ("تعداد مسیر فرانت‌اند", app_tsx.count("Route path") == 10, "App.tsx"),

        # ── شکاف‌های اعلام‌شده باید واقعاً شکاف باشند ──────────────────
        ("سیستم اشتراک و سهمیه ساخته شده",
         count(r"class\s+(Subscription|Plan|Usage)[(]", "backend") >= 3,
         "apps/billing/models.py"),
        ("نوین‌هاب پیاده شده",
         count(r"(?i)novinhub", "backend") > 0,
         "services/publishing/novinhub.py"),
        ("سوییچ لوکال/API برای هر قابلیت",
         count(r"class\s+ModelProvider[(]", "backend") == 1,
         "apps/ai/models.py"),
        ("نگهبان سهمیه روی اندپوینت‌های تولید",
         count(r"guards\.check\(", "backend/apps/content") >= 3,
         "apps/content/views.py"),

        # ── سازگاری درونی داده ───────────────────────────────────────
        ("ثانیه‌های پکیج مضرب طول قطعه",
         all(p["video_sec"] % r["segment_sec"] == 0 for p in DATA["packages"]),
         str([p["video_sec"] for p in DATA["packages"]])),
        ("جمع سهم ترکیب مشتریان = ۱۰۰٪",
         abs(sum(p["mix_share"] for p in DATA["packages"]) - 1) < 1e-6,
         str(sum(p["mix_share"] for p in DATA["packages"]))),
        ("هر نمونه‌کار فایل کپشن دارد",
         all((HERE.parent / "3-نمونه‌کار" / p["caption_file"]).exists()
             for p in DATA["portfolio"]),
         "3-نمونه‌کار/"),
    ]

    print()
    print("  تطبیق data.json با کد پروژه")
    print("  " + "-" * 62)
    failed = 0
    for name, ok, detail in checks:
        mark = "[OK]  " if ok else "[FAIL]"
        if not ok:
            failed += 1
        print(f"  {mark} {name:<32} {detail}")
    print("  " + "-" * 62)

    if failed:
        print(f"  {failed} ناسازگاری — داده و کد از هم جدا افتاده‌اند.")
        print("  یا کد را درست کن یا data.json را. جزئیات در تطبیق-با-کد.md")
    else:
        print("  همه‌ی ادعاهای داده در کد قابل اثبات‌اند.")
    print()
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
