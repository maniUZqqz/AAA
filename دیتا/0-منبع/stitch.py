# -*- coding: utf-8 -*-
"""
مستند کامل داخلی را از بقیه‌ی مستندات می‌سازد.

    python stitch.py

خروجی: ‎../1-مستند-داخلی/مستند-کامل.md‎ — یک فایل که همه‌چیز در آن است،
برای وقتی که می‌خواهی کل تصویر را یکجا بخوانی یا پرینت بگیری.
"""
from pathlib import Path

from model import compact, fa, load, money, pct

HERE = Path(__file__).parent
DOCS = HERE.parent / "1-مستند-داخلی"

# ترتیب عمدی است: از «چه ساخته‌ایم» به «چقدر می‌ارزد» به «چه مانده»
PARTS = [
    ("دفترچه-محصول.md", "محصول"),
    ("گزارش-مالی.md", "مدل مالی"),
    ("تطبیق-با-کد.md", "داده در برابر کد"),
    ("فرضیات-و-منابع.md", "فرضیات"),
    ("وب-سایت-عمومی.md", "سایت عمومی"),
    ("اصلاحات-انجام-شده.md", "سابقه‌ی اصلاحات"),
]


def _body(path: Path) -> str:
    """محتوای فایل بدون خط تولیدشده و بدون عنوان اصلی (یک سطح پایین می‌آید)."""
    lines = path.read_text(encoding="utf-8").splitlines()
    out = []
    for line in lines:
        if line.startswith("<!-- تولیدشده"):
            continue
        if line.startswith("# "):
            continue  # عنوان بخش را خودمان می‌گذاریم
        # هر تیتر یک سطح پایین‌تر می‌رود تا ساختار فایل نهایی درست بماند
        if line.startswith("#"):
            line = "#" + line
        out.append(line)
    return "\n".join(out).strip()


def main() -> None:
    m = load()
    d = m.d
    som = m.som()

    head = [
        "<!-- تولیدشده با stitch.py — دستی ویرایش نکن -->",
        f"# {d['meta']['brand_fa']} — مستند کامل داخلی",
        "",
        f"> {d['meta']['tagline']}",
        f"> نسخه {fa(d['meta']['version'])} — {d['meta']['updated']}",
        "",
        "این فایل برای **ما**ست، نه برای مشتری و نه برای سرمایه‌گذار.",
        "همه‌چیز در آن هست: اعداد خام، کارهای باقی‌مانده، و چیزهایی که هنوز",
        "تأیید نشده‌اند. برای ارائه به بیرون از `2-ارائه` استفاده کن.",
        "",
        "---",
        "",
        "## یک‌نگاه",
        "",
        "| شاخص | مقدار |",
        "| --- | --- |",
        f"| سرمایه سخت‌افزار | {compact(m.capex)} تومان |",
        f"| هزینه ثابت ماهانه | {compact(m.fixed_total)} تومان |",
        f"| درآمد میانگین هر مشتری | {money(m.avg_revenue)} تومان |",
        f"| حاشیه مشارکت | {money(m.contribution)} تومان |",
        f"| **نقطه سر به سر** | **{fa(m.break_even)} مشتری** |",
        f"| **سقف سخت‌افزار** | **{fa(m.max_customers)} مشتری** |",
        f"| سود ماهانه در ظرفیت کامل | {compact(m.at_capacity['net'])} تومان ({pct(m.at_capacity['margin'])}) |",
        f"| بازگشت نقدی سرمایه | {fa(f'{m.payback_months:.1f}')} ماه |",
        f"| هدف ۳ ساله | {money(som['min'])}–{money(som['max'])} مشتری |",
        "",
        "### کارهای باقی‌مانده",
        "",
        "| کار | شدت | چرا |",
        "| --- | --- | --- |",
    ]
    marks = {"blocker": "🔴 بحرانی", "high": "🟠 مهم", "medium": "🟡 متوسط"}
    for g in m.gaps:
        head.append(f"| {g['title']} | {marks.get(g['severity'], '')} | {g['impact']} |")

    head += ["", "### فهرست", ""]
    for i, (_, title) in enumerate(PARTS, start=1):
        head.append(f"{fa(i)}. [{title}](#{title.replace(' ', '-')})")
    head += ["", "---", ""]

    chunks = ["\n".join(head)]
    for filename, title in PARTS:
        path = DOCS / filename
        if not path.exists():
            continue
        chunks.append(f"## {title}\n\n{_body(path)}\n\n---\n")

    out = DOCS / "مستند-کامل.md"
    text = "\n".join(chunks).rstrip() + "\n"
    out.write_text(text, encoding="utf-8")
    print(f"  نوشته شد: {out.name}  ({len(text.splitlines())} خط از {len(PARTS)} بخش)")


if __name__ == "__main__":
    main()
