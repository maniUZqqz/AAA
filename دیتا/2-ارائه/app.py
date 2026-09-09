# -*- coding: utf-8 -*-
"""
ارائه‌ی آپ‌مارکت — دو مخاطب، یک منبع داده.

    pip install flask
    python app.py            →  http://127.0.0.1:5100

    /                        صفحه‌ی انتخاب مخاطب
    /deck/customer/1         ارائه‌ی مشتری   — ساده، بدون اعداد داخلی
    /deck/investor/1         ارائه‌ی سرمایه‌گذار — کامل، با مدل مالی

هر عددی که در اسلایدها می‌بینی از ‎../0-منبع/data.json‎ می‌آید و با
‎model.py‎ محاسبه می‌شود. هیچ عددی داخل قالب‌ها نوشته نشده — برای تغییر
قیمت یا هزینه فقط همان فایل را عوض کن.
"""
from __future__ import annotations

import sys
from pathlib import Path

from flask import Flask, abort, render_template, url_for

BASE = Path(__file__).resolve().parent
DATA_DIR = BASE.parent / "0-منبع"
SAMPLES_DIR = BASE.parent / "3-نمونه‌کار"

sys.path.insert(0, str(DATA_DIR))
import model as fin  # noqa: E402  (پس از تنظیم sys.path)

app = Flask(__name__)

# ---------------------------------------------------------------- ارائه‌ها
# هر سطر: (نام قالب، برچسب بالای اسلاید، عنوان)

CUSTOMER = [
    ("c_cover",   "آپ‌مارکت",     "بازاریابی فروشگاه شما، خودکار"),
    ("c_problem", "چرا",          "بازاریابی حرفه‌ای گران است"),
    ("work1",     "نمونه کار",    "پوستر و کپشن واقعی"),
    ("work2",     "نمونه کار",    "ویدیوی تبلیغاتی"),
    ("how",       "فرایند",       "چطور کار می‌کند"),
    ("c_pricing", "پکیج‌ها",       "قیمت و صرفه‌جویی شما"),
    ("c_trust",   "خیال راحت",    "بدون ریسک شروع کنید"),
    ("c_start",   "شروع",         "دو هفته رایگان"),
]

INVESTOR = [
    ("cover",     "معرفی",             "آپ‌مارکت"),
    ("problem",   "چالش",              "مشکل"),
    ("solution",  "راه‌حل",             "آپ‌مارکت چه می‌کند"),
    ("how",       "فرایند",            "نحوه کار"),
    ("work1",     "نمونه کار",         "پوشاک و اکسسوری"),
    ("work2",     "نمونه کار",         "ویدیوی تبلیغاتی"),
    ("product",   "محصول",             "چه چیزی ساخته شده"),
    ("engine",    "معماری",            "موتور قابل تعویض"),
    ("edge",      "مزیت رقابتی",       "چرا آپ‌مارکت"),
    ("market",    "بازار",             "TAM · SAM · SOM"),
    ("rivals",    "رقبا",              "تحلیل رقابتی"),
    ("pricing",   "قیمت‌گذاری",         "پکیج‌ها و واحد اقتصادی"),
    ("infra",     "زیرساخت",           "سه گزینه، یک انتخاب"),
    ("capacity",  "ظرفیت",             "سقف واقعی سخت‌افزار"),
    ("profit",    "سودآوری",           "نقطه سر به سر و سود"),
    ("gtm",       "استراتژی",          "ورود به بازار"),
    ("roadmap",   "نقشه راه",          "مسیر پیش رو"),
    ("swot",      "تحلیل استراتژیک",   "SWOT"),
    ("ask",       "جمع‌بندی",           "درخواست ما"),
]

DECKS = {
    "customer": {
        "slides": CUSTOMER,
        "name": "ارائه‌ی مشتری",
        "audience": "برای صاحب فروشگاه",
        "desc": "محصول چیست، چه چیزی تحویل می‌دهد، چقدر صرفه دارد. بدون اعداد داخلی.",
        "icon": "🛍️",
    },
    "investor": {
        "slides": INVESTOR,
        "name": "ارائه‌ی سرمایه‌گذار",
        "audience": "برای سرمایه‌گذار و شریک",
        "desc": "بازار، رقبا، مدل مالی، ظرفیت، سر به سر و درخواست سرمایه.",
        "icon": "📈",
    },
}


def _captions(m) -> dict:
    """متن کپشن هر نمونه‌کار را از فایل واقعی‌اش می‌خواند."""
    out = {}
    for item in m.d["portfolio"]:
        path = SAMPLES_DIR / item["caption_file"]
        try:
            out[item["id"]] = path.read_text(encoding="utf-8").strip()
        except OSError:
            out[item["id"]] = f"«فایل کپشن پیدا نشد: {item['caption_file']}»"
    return out


@app.context_processor
def inject():
    """چیزهایی که هر قالب به آن‌ها دسترسی دارد."""
    m = fin.load()  # هر بار تازه خوانده می‌شود تا ویرایش data.json آنی دیده شود
    return {
        "m": m,
        "d": m.d,
        "decks": DECKS,
        "captions": _captions(m),
        "fa": fin.fa,
        "money": fin.money,
        "compact": fin.compact,
        "pct": fin.pct,
    }


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/deck/<deck>/<int:num>")
def slide(deck: str, num: int):
    if deck not in DECKS:
        abort(404)
    slides = DECKS[deck]["slides"]
    if not 1 <= num <= len(slides):
        abort(404)
    name, tag, title = slides[num - 1]
    return render_template(
        f"slides/{name}.html",
        deck=deck,
        meta=DECKS[deck],
        slides=slides,
        num=num,
        total=len(slides),
        tag=tag,
        title=title,
        prev=num - 1 if num > 1 else None,
        next=num + 1 if num < len(slides) else None,
    )


@app.errorhandler(404)
def not_found(_):
    return render_template("home.html"), 404


if __name__ == "__main__":
    print("\n  ارائه‌ی آپ‌مارکت")
    for key, deck in DECKS.items():
        print(f"    {deck['icon']} {deck['name']:<18} {len(deck['slides']):>2} اسلاید"
              f"   http://127.0.0.1:5100/deck/{key}/1")
    print("\n  انتخاب مخاطب:  http://127.0.0.1:5100\n")
    app.run(debug=True, port=5100)
