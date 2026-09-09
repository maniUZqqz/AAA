# -*- coding: utf-8 -*-
"""
مستندات مالی را از data.json تولید می‌کند.

    python build_docs.py

خروجی‌ها با دست ویرایش نشوند — با هر بار اجرا بازنویسی می‌شوند.
برای تغییر اعداد، data.json را عوض کن و دوباره اجرا کن.
"""
from __future__ import annotations

from pathlib import Path

from model import compact, fa, load, money, pct

HERE = Path(__file__).parent
DOCS = HERE.parent / "1-مستند-داخلی"
STAMP = "<!-- تولیدشده با build_docs.py — دستی ویرایش نکن -->"


def _row(*cells) -> str:
    return "| " + " | ".join(str(c) for c in cells) + " |"


def _head(*cells) -> str:
    return _row(*cells) + "\n" + _row(*(["---"] * len(cells)))


# ------------------------------------------------------------ گزارش مالی


def financial(m) -> str:
    d = m.d
    L: list[str] = [
        STAMP,
        f"# گزارش مالی {d['meta']['brand_fa']}",
        "",
        f"> منبع: `data.json` · محاسبه: `model.py` · نسخه {fa(d['meta']['version'])}"
        f" — {d['meta']['updated']}",
        "",
        "همه‌ی اعداد این فایل از یک منبع محاسبه شده‌اند. اگر عددی در ارائه دیدی که با",
        "اینجا نمی‌خواند، ارائه اشتباه است نه این فایل.",
        "",
        "---",
        "",
        "## ۱. سخت‌افزار و سرمایه اولیه",
        "",
        _head("سیستم", "CPU", "RAM", "GPU", "قیمت (تومان)"),
    ]
    for s in m.systems:
        L.append(_row(s["name"], s["cpu"], s["ram"], s["gpu"], money(s["price"])))
    L += [
        _row("**جمع**", "", "", "", f"**{money(m.capex)}**"),
        "",
        f"استهلاک {fa(m.a['depreciation_months'])} ماهه → "
        f"**{money(m.depreciation)} تومان در ماه**",
        "",
        "---",
        "",
        "## ۲. ظرفیت GPU",
        "",
        _head("مورد", "مقدار"),
        _row(
            f"{fa(len(m.systems))} سیستم × {fa(m.a['uptime_hours_per_day'])} ساعت"
            f" × {fa(m.a['days_per_month'])} روز",
            f"{money(m.gpu_min_raw)} دقیقه",
        ),
        _row(f"افت واقعی {pct(m.a['derate'])}", f"−{money(m.gpu_min_raw - m.gpu_min_usable)} دقیقه"),
        _row("**ظرفیت مؤثر ماهانه**", f"**{money(m.gpu_min_usable)} دقیقه** ({money(m.gpu_min_usable / 60)} ساعت)"),
        "",
        "### نرخ مصرف",
        "",
        _head("خروجی", "زمان GPU"),
        _row("هر ثانیه ویدیو", f"{fa(m.min_per_video_sec)} دقیقه"),
        _row("هر پوستر", f"{fa(m.min_per_poster)} دقیقه"),
        _row("هر کپشن", "صفر (API متنی، بدون GPU)"),
        "",
        f"> **مهم:** {d['render']['code_note']}",
        "",
        "---",
        "",
        "## ۳. پکیج‌ها",
        "",
        _head("پکیج", "قیمت", "ویدیو", "پوستر", "کپشن", "زمان GPU", "سهم ترکیب"),
    ]
    for p in m.packages:
        L.append(
            _row(
                p["name"],
                money(p["price"]),
                f"{fa(p['video_sec'])} ثانیه",
                fa(p["posters"]),
                fa(p["captions"]),
                f"{fa(int(p['gpu_min']))} دقیقه",
                pct(p["mix_share"]),
            )
        )
    L += [
        _row(
            "**میانگین وزنی**",
            f"**{money(m.avg_revenue)}**",
            f"{fa(m.avg_video_sec)} ثانیه",
            fa(m.avg_posters),
            fa(m.avg_captions),
            f"{fa(m.avg_gpu_min)} دقیقه",
            "۱۰۰٪",
        ),
        "",
        "---",
        "",
        "## ۴. هزینه‌ها",
        "",
        "### ۴.۱ هزینه ثابت ماهانه",
        "",
        _head("ردیف", "مبلغ (تومان)", "سهم"),
    ]
    for line in m.fixed_lines:
        L.append(_row(line["label"], money(line["amount"]), pct(line["amount"] / m.fixed_total)))
    L += [
        _row("**جمع**", f"**{money(m.fixed_total)}**", "۱۰۰٪"),
        "",
        "### ۴.۲ هزینه متغیر هر مشتری",
        "",
        _head("مورد", "مبلغ (تومان)"),
        _row(
            f"{d['variable_costs']['caption_api_per_unit']['label']} × {fa(m.avg_captions)}",
            money(m.cost_captions),
        ),
        _row(
            d["variable_costs"]["instagram_api"]["label"]
            + f" — {d['variable_costs']['instagram_api']['status']}",
            money(m.cost_instagram),
        ),
        _row("**جمع (سناریوی پایه)**", f"**{money(m.variable_planned)}**"),
        _row("امروز، تا وصل‌شدن اینستاگرام", money(m.variable_today)),
        "",
        "> هزینه‌ی GPU در هزینه‌ی متغیر نیست، چون سخت‌افزار متعلق به ماست و",
        "> هزینه‌اش (استهلاک + برق) در هزینه‌ی ثابت آمده. آوردن هر دو، دوباره‌شماری است.",
        "",
        f"> ⚠️ {d['variable_costs']['instagram_api']['note']}",
        "> جزئیات در `تطبیق-با-کد.md`.",
        "",
        "---",
        "",
        "## ۵. نقطه سر به سر و سقف ظرفیت",
        "",
        _head("شاخص", "مقدار"),
        _row("درآمد میانگین هر مشتری", f"{money(m.avg_revenue)} تومان"),
        _row("هزینه متغیر هر مشتری", f"{money(m.variable_per_customer)} تومان"),
        _row("**حاشیه مشارکت**", f"**{money(m.contribution)} تومان** ({pct(m.contribution / m.avg_revenue)})"),
        _row("**نقطه سر به سر (پایه)**", f"**{fa(m.break_even)} مشتری**"),
        _row("نقطه سر به سر امروز", f"{fa(m.break_even_today)} مشتری"),
        _row("**سقف سخت‌افزار فعلی**", f"**{fa(m.max_customers)} مشتری**"),
        "",
        f"> ⚠️ **اصلاح مدل قبلی:** سقف قبلاً {fa(m.max_customers_video_only)} مشتری گزارش شده بود،",
        "> چون فقط زمان ویدیو حساب شده و **زمان پوستر نادیده گرفته شده بود**. چون هر دو روی",
        f"> یک GPU اجرا می‌شوند، سقف درست **{fa(m.max_customers)} مشتری** است"
        f" ({pct((m.max_customers_video_only - m.max_customers) / m.max_customers_video_only)} کمتر).",
        "",
        "---",
        "",
        "## ۶. سناریوهای سود و زیان",
        "",
        _head("مشتری", "درآمد", "هزینه متغیر", "هزینه ثابت", "سود خالص", "حاشیه", "ساعت/سیستم/روز", "ظرفیت"),
    ]
    for s in m.scenarios:
        L.append(
            _row(
                fa(s["customers"]),
                money(s["revenue"]),
                money(s["variable"]),
                money(s["fixed"]),
                money(s["net"]),
                pct(s["margin"]),
                fa(f"{s['hours_per_system_per_day']:.1f}"),
                pct(s["capacity_used"]),
            )
        )
    e = m.expansion
    L += [
        "",
        "### بازگشت سرمایه",
        "",
        _head("مبنا", "مدت"),
        _row("نقدی (سود خالص + استهلاک)", f"{fa(f'{m.payback_months:.1f}')} ماه"),
        _row("حسابداری (فقط سود خالص)", f"{fa(f'{m.payback_months_accounting:.1f}')} ماه"),
        "",
        f"### توسعه با {e['label']}",
        "",
        f"با {compact(e['price'])} تومان سرمایه‌ی اضافه:",
        "",
        _head("شاخص", "فعلی", f"با {e['label']}"),
        _row("سقف مشتری", fa(m.max_customers), fa(e["max_customers"])),
        _row("سود ماهانه", compact(m.at_capacity["net"]), compact(e["pnl"]["net"])),
        _row("حاشیه سود", pct(m.at_capacity["margin"]), pct(e["pnl"]["margin"])),
        "",
        "چون حقوق تیم ثابت می‌ماند، هر سیستم اضافه حاشیه سود را جهش می‌دهد.",
        "",
        "---",
        "",
        "## ۷. مقایسه زیرساخت",
        "",
        _head("گزینه", "سرمایه اولیه", "هر ثانیه ویدیو", "هر پوستر", "هر مشتری", "٪ از درآمد", "ریسک تحریم"),
    ]
    for o in m.infra:
        star = " ⭐" if o.get("recommended") else (" ❌" if o["share_of_revenue"] >= 1 else "")
        L.append(
            _row(
                o["name"] + star,
                compact(o["capex"]) if o["capex"] else "۰",
                money(o["per_video_sec"]),
                money(o["per_poster"]),
                money(o["per_customer"]),
                pct(o["share_of_revenue"]),
                o["sanction_risk"],
            )
        )
    L += [
        "",
        "### حساسیت به نرخ دلار",
        "",
        _head("نرخ دلار", *[o["name"] for o in m.infra]),
    ]
    for rate in (350000, 700000, 1050000):
        cells = [money(r["per_customer"]) + ("" if r["viable"] else " ⚠️") for r in m.sensitivity(rate)]
        L.append(_row(money(rate), *cells))
    api = m.infra_by_id("api")
    personal = m.infra_by_id("personal")
    L += [
        "",
        f"⚠️ = هزینه بالاتر از حاشیه مشارکت ({money(m.contribution)} تومان) — مدل نمی‌بندد.",
        "",
        "**نتیجه:** ارائه‌ی قدیمی «API خارجی» را توصیه می‌کرد، در حالی که هزینه‌ی آن",
        f"**{pct(api['share_of_revenue'])} از درآمد** هر مشتری است — یعنی پیش از هر هزینه‌ی",
        f"ثابتی ضرر می‌دهد. سرور شخصی با **{pct(personal['share_of_revenue'])}** تنها گزینه‌ای",
        "است که مدل کسب‌وکار را می‌بندد.",
        "",
        "---",
        "",
        "## ۸. بازار",
        "",
    ]
    som = m.som()
    L += [
        _head("سطح", "مقدار"),
        _row("TAM — " + d["market"]["tam"]["label"], f"{d['market']['tam']['display']} ({d['market']['tam']['display_usd']})"),
        _row(
            "SAM — " + d["market"]["sam"]["label"],
            f"{money(d['market']['sam']['min'])}–{money(d['market']['sam']['max'])} {d['market']['sam']['unit']}",
        ),
        _row("SOM — " + d["market"]["som"]["label"], f"{money(som['min'])}–{money(som['max'])} مشتری"),
        _row("درآمد سالانه در SOM", f"{compact(som['revenue_min_year'])} تا {compact(som['revenue_max_year'])} تومان"),
        _row("سیستم GPU لازم برای SOM", f"{fa(som['systems_min'])} تا {fa(som['systems_max'])} سیستم"),
        "",
        f"> ⚠️ {d['market']['tam']['warning']}",
        "",
        f"> **واقعیت مقیاس:** رسیدن به {money(som['min'])} مشتری حدود {fa(som['systems_min'])} سیستم GPU",
        f"لازم دارد (تقریباً {compact(som['systems_min'] * m.systems[0]['price'])} تومان سرمایه).",
        "رشد این کسب‌وکار پله‌ای و سرمایه‌بر است، نه نامحدود.",
        "",
    ]
    return "\n".join(L) + "\n"


# --------------------------------------------------------- فرضیات و منابع


def assumptions(m) -> str:
    d = m.d
    labels = d["sources"]
    L = [
        STAMP,
        "# فرضیات و منابع",
        "",
        "هر عددی که در ارائه می‌بینی یکی از این چهار برچسب را دارد.",
        "قبل از ارائه به سرمایه‌گذار، ردیف‌های «نیازمند تأیید» را با قیمت روز به‌روز کن.",
        "",
        _head("برچسب", "معنی"),
    ]
    for key, text in labels.items():
        L.append(_row(f"`{key}`", text))

    L += ["", "---", "", "## فرضیات پایه", "", _head("فرض", "مقدار", "منبع", "توضیح")]
    for a in d["assumptions"]:
        unit = a.get("unit", "")
        val = money(a["value"]) if a["value"] >= 1000 else fa(a["value"])
        L.append(_row(a["label"], f"{val} {unit}".strip(), f"`{a['source']}`", a.get("note", "—")))

    L += [
        "",
        "## ردیف‌هایی که باید تأیید شوند",
        "",
        _head("مورد", "مقدار فعلی", "چرا مهم است"),
        _row(
            "نرخ دلار",
            money(m.a["usd_rate"]) + " تومان",
            "هزینه‌ی سرور ابری و API خارجی را تعیین می‌کند؛ روی گزینه‌ی سرور شخصی اثری ندارد",
        ),
        _row(
            "اجاره GPU ابری",
            f"${fa(m.d['infra_options'][1]['gpu_hour_usd'])} در ساعت",
            "پایه‌ی ستون «سرور ابری» در مقایسه‌ی زیرساخت",
        ),
        _row(
            "قیمت API ویدیو",
            f"${fa(m.d['infra_options'][2]['video_usd_per_sec'])} هر ثانیه",
            "پایه‌ی ستون «API خارجی»",
        ),
        _row(
            "قیمت سیستم‌ها",
            money(m.capex) + " تومان",
            "روی استهلاک، هزینه ثابت و بازگشت سرمایه اثر مستقیم دارد",
        ),
        _row(
            "TAM بازار",
            d["market"]["tam"]["display"],
            "داده‌ی قدیمی است — با گزارش روز بازار تبلیغات دیجیتال جایگزین شود",
        ),
        "",
        "## اعدادی که از کد پروژه استخراج شده‌اند",
        "",
        _head("عدد", "مقدار", "محل در کد"),
        _row("تست خودکار", d["product"]["stats"][1]["value"], "`backend/` — شمارش `def test_`"),
        _row("دامنه‌ی بک‌اند", d["product"]["stats"][0]["value"], "`backend/apps/`"),
        _row("صفحه‌ی داشبورد", d["product"]["stats"][2]["value"], "`frontend/src/App.tsx`"),
        _row("ورک‌فلوی ComfyUI", d["product"]["stats"][3]["value"], "`backend/services/comfyui/workflows/`"),
        _row("هم‌زمانی GPU", "۱", "`GPU_CONCURRENCY_LIMIT` در `docs/ARCHITECTURE.md`"),
        "",
    ]
    return "\n".join(L) + "\n"



# ------------------------------------------------------- دفترچه محصول


def handbook(m) -> str:
    """مرجع محصول — برای ادامه‌ی پروژه، نه برای ارائه."""
    d = m.d
    L = [
        STAMP,
        f"# دفترچه محصول — {d['meta']['brand_fa']}",
        "",
        f"> {d['meta']['tagline']}",
        "",
        "مرجع یکجای «محصول چیست و چه قول‌هایی داده» — برای ادامه‌ی توسعه.",
        "کد در `../../Code/UpMarket` است؛ این فایل تصمیم‌های محصولی را نگه می‌دارد.",
        "",
        "---",
        "",
        "## ۱. محصول در یک جمله",
        "",
        d["meta"]["one_liner"],
        "",
        "## ۲. مشکلی که حل می‌کند",
        "",
        d["problem"]["lead"],
        "",
        _head("نقش", "کار"),
    ]
    for r in d["problem"]["roles"]:
        L.append(_row(f"{r['icon']} {r['role']}", r["task"]))
    L += [
        "",
        f"هزینه‌ی جایگزینی این تیم: **{money(d['problem']['team_cost_monthly'])} تومان در ماه**.",
        "",
        "## ۳. جریان کار محصول",
        "",
        _head("گام", "مرحله", "چه اتفاقی می‌افتد"),
    ]
    for s in d["how_it_works"]:
        L.append(_row(s["n"], f"{s['icon']} {s['title']}", s["desc"]))
    L += [
        "",
        "## ۴. پشته‌ی فناوری",
        "",
        _head("لایه", "انتخاب"),
    ]
    names = {
        "backend": "بک‌اند", "frontend": "فرانت‌اند", "llm": "مدل زبانی",
        "image": "تصویر", "video": "ویدیو", "audio": "صدا", "publish": "انتشار",
    }
    for k, v in d["product"]["stack"].items():
        L.append(_row(names.get(k, k), v))
    L += [
        "",
        "## ۵. وضعیت فعلی",
        "",
        _head("شاخص", "مقدار", "جزئیات"),
    ]
    for s in d["product"]["stats"]:
        L.append(_row(s["label"], s["value"], s["detail"]))
    L += [
        "",
        "## ۶. قول‌های محصول که نباید شکسته شوند",
        "",
        "این‌ها تصمیم‌های محصولی‌اند، نه جزئیات پیاده‌سازی. هر تغییری در کد که",
        "یکی از این‌ها را نقض کند، تغییر محصول است و باید آگاهانه گرفته شود.",
        "",
    ]
    for i, p_ in enumerate(d["product"]["proof"], 1):
        L.append(f"{fa(i)}. {p_}")
    L += [
        "",
        "## ۷. نقشه راه",
        "",
        _head("فاز", "زمان", "عنوان", "محتوا"),
    ]
    for r in d["roadmap"]:
        mark = " ✅" if r["done"] else ""
        L.append(_row(r["phase"] + mark, r["time"], r["title"], " · ".join(r["items"])))
    L += [
        "",
        "## ۸. پکیج‌ها و مصرف منابع",
        "",
        "طراحی هر پکیج باید با ظرفیت GPU سازگار بماند — جدول کامل در `گزارش-مالی.md`.",
        "",
        _head("پکیج", "قیمت", "ویدیو", "پوستر", "کپشن", "زمان GPU"),
    ]
    for p_ in m.packages:
        L.append(_row(
            p_["name"], money(p_["price"]), f"{fa(p_['video_sec'])} ثانیه",
            fa(p_["posters"]), fa(p_["captions"]), f"{fa(int(p_['gpu_min']))} دقیقه",
        ))
    L += [
        "",
        f"**سقف فعلی: {fa(m.max_customers)} مشتری** با {fa(len(m.systems))} سیستم.",
        f"نقطه‌ی سر به سر: **{fa(m.break_even)} مشتری**.",
        "",
        "## ۹. کارهای باز",
        "",
        _head("کار", "چرا مهم است"),
        _row("اجرای واقعی روی سیستم اصلی با مدل‌های نصب‌شده",
             "همه‌ی پایپ‌لاین‌ها با مدل ساختگی تست شده‌اند؛ کیفیت واقعی هنوز دیده نشده"),
        _row("اتصال نوین‌هاب برای انتشار اینستاگرام",
             "فاز ۱ نقشه راه · ۹۹٪ هزینه‌ی متغیر همین است"),
        _row("سایت عمومی با Next.js",
             "برنامه در `وب-سایت-عمومی.md` · لازم برای SEO و جذب"),
        _row("رساندن نمونه‌کارها به ۲۰ عدد",
             f"استراتژی ورود به بازار به آن نیاز دارد؛ الان {fa(len(d['portfolio']))} تاست"),
        _row("به‌روزرسانی داده‌ی بازار",
             "TAM از یک گزارش قدیمی است — جزئیات در `فرضیات-و-منابع.md`"),
        "",
    ]
    return "\n".join(L) + "\n"



# ------------------------------------------------- تطبیق داده با کد


def code_check(m) -> str:
    """هر ادعای داده، در برابر جایی که در کد اثبات می‌شود."""
    d = m.d
    L = [
        STAMP,
        "# تطبیق داده با کد",
        "",
        "> هر ادعایی که در ارائه گفته می‌شود باید در کد قابل اثبات باشد.",
        "> این فایل محل اثبات هر کدام را نشان می‌دهد.",
        "",
        "مسیرها نسبت به `../../Code/UpMarket/` هستند.",
        "",
        "---",
        "",
        "## ادعاهای تأییدشده",
        "",
        _head("ادعا", "محل اثبات در کد"),
    ]
    for f in m.code_facts:
        L.append(_row(f["claim"], "`" + f["where"] + "`"))

    L += [
        "",
        "---",
        "",
        "## شکاف‌ها — چیزی که در داده هست ولی در کد نیست",
        "",
        "این‌ها مهم‌ترین بخش این فایل‌اند. هر کدام قبل از فروش باید بسته شوند.",
        "",
    ]
    marks = {"blocker": "🔴 بحرانی", "high": "🟠 مهم", "medium": "🟡 متوسط", "low": "⚪ کم"}
    for g in m.gaps:
        L += [
            f"### {marks.get(g['severity'], '')} {g['title']}",
            "",
            g["desc"],
            "",
            f"- **اثر:** {g['impact']}",
            f"- **شاهد:** {g['evidence']}",
            "",
        ]

    L += [
        "---",
        "",
        "## محدودیت‌های موتور که روی طراحی پکیج اثر دارند",
        "",
        _head("محدودیت", "مقدار", "منبع"),
        _row("طول هر قطعه ویدیو", f"{fa(m.segment_sec)} ثانیه", "`VIDEO_SEGMENT_DURATION`"),
        _row("حداقل طول یک ویدیو", f"{fa(m.d['render']['min_single_video_sec'])} ثانیه",
             "`apps/content/views.py:167`"),
        _row("حداکثر طول یک ویدیو", f"{fa(m.max_single_video_sec)} ثانیه",
             "`apps/content/views.py:167`"),
        _row("هم‌زمانی GPU", "۱", "`GPU_CONCURRENCY_LIMIT`"),
        _row("پلتفرم‌های کپشن", "اینستاگرام · تلگرام · لینکدین", "`apps/content/models.py:12`"),
        _row("حالت‌های تصویر", "پوستر · عکس اینستاگرامی · بهبود عکس", "`apps/content/models.py:52`"),
        "",
        f"> {d['render']['limits_note']}",
        "",
        "### پکیج‌ها با این محدودیت‌ها",
        "",
        _head("پکیج", "ثانیه در ماه", "تعداد قطعه", "حداقل تعداد ویدیو"),
    ]
    for p_ in m.packages:
        L.append(_row(p_["name"], fa(p_["video_sec"]), fa(p_["segments"]), fa(p_["videos"])))

    L += [
        "",
        f"> {d['packages_note']}",
        "",
        "---",
        "",
        "## اثر روی مدل مالی",
        "",
        "چون نوین‌هاب هنوز وصل نیست، هزینه‌ی متغیر امروز بسیار کمتر است:",
        "",
        _head("سناریو", "هزینه متغیر هر مشتری", "حاشیه مشارکت", "نقطه سر به سر"),
        _row("امروز (انتشار با n8n خودِ فروشگاه‌دار)",
             money(m.variable_today), money(m.contribution_today), f"{fa(m.break_even_today)} مشتری"),
        _row("**پایه — با اتصال اینستاگرام**",
             f"**{money(m.variable_planned)}**", f"**{money(m.contribution_planned)}**",
             f"**{fa(m.break_even_planned)} مشتری**"),
        "",
        "ارائه و همه‌ی محاسبات از **سناریوی پایه** استفاده می‌کنند — یعنی",
        "هزینه‌ی اینستاگرام از حالا لحاظ شده. این عمدی و محافظه‌کارانه است:",
        "انتشار خودکار بخشی از قولِ محصول است، پس هزینه‌اش دیر یا زود می‌آید.",
        "",
    ]
    return "\n".join(L) + "\n"


def main() -> None:
    m = load()
    DOCS.mkdir(exist_ok=True)
    for name, text in (
        ("گزارش-مالی.md", financial(m)),
        ("فرضیات-و-منابع.md", assumptions(m)),
        ("دفترچه-محصول.md", handbook(m)),
        ("تطبیق-با-کد.md", code_check(m)),
    ):
        path = DOCS / name
        path.write_text(text, encoding="utf-8")
        print(f"  نوشته شد: {name}  ({len(text.splitlines())} خط)")


if __name__ == "__main__":
    main()
