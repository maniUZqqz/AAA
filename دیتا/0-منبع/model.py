# -*- coding: utf-8 -*-
"""
موتور محاسبه‌ی مدل مالی آپ‌مارکت.

هیچ عددی اینجا hard-code نشده — همه از data.json خوانده می‌شود.
برای تغییر مدل فقط data.json را عوض کن؛ اسلایدها و مستندات خودکار به‌روز می‌شوند.

    python model.py        # گزارش خلاصه در ترمینال
"""
from __future__ import annotations

import json
import math
from pathlib import Path

DATA_FILE = Path(__file__).with_name("data.json")

# ---------------------------------------------------------------- قالب‌بندی

_FA_DIGITS = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")


def fa(value) -> str:
    """ارقام لاتین را فارسی می‌کند."""
    return str(value).translate(_FA_DIGITS)


def money(value, digits: int = 0) -> str:
    """۱۲۳۴۵۶۷ → ۱٬۲۳۴٬۵۶۷"""
    return fa(f"{round(value, digits):,.{digits}f}").replace(",", "٬")


def compact(value) -> str:
    """عدد بزرگ را به «هزار / میلیون / میلیارد» کوتاه می‌کند."""
    value = float(value)
    for unit, size in (("میلیارد", 1_000_000_000), ("میلیون", 1_000_000), ("هزار", 1_000)):
        if abs(value) >= size:
            text = f"{value / size:.1f}".rstrip("0").rstrip(".")
            return f"{fa(text)} {unit}"
    return money(value)


def pct(value, digits: int = 0) -> str:
    return fa(f"{value * 100:.{digits}f}") + "٪"


# -------------------------------------------------------------------- مدل


class Model:
    """کل مدل مالی، محاسبه‌شده از data.json."""

    def __init__(self, data: dict):
        self.d = data
        self.a = {item["key"]: item["value"] for item in data["assumptions"]}
        a = self.a

        # ---------- سخت‌افزار و استهلاک ----------
        self.systems = data["hardware"]["systems"]
        self.capex = sum(s["price"] for s in self.systems)
        self.depreciation = self.capex / a["depreciation_months"]

        # ---------- ظرفیت GPU ----------
        r = data["render"]
        self.segment_sec_hint = r.get("segment_sec", 5)
        self.max_single_video_sec_hint = r.get("max_single_video_sec", 60)
        self.min_per_video_sec = r["video_gpu_min_per_second"]
        self.min_per_poster = r["poster_gpu_min_per_image"]

        self.gpu_min_raw = (
            len(self.systems) * a["uptime_hours_per_day"] * a["days_per_month"] * 60
        )
        self.gpu_min_usable = self.gpu_min_raw * (1 - a["derate"])

        # ---------- پکیج‌ها ----------
        self.packages = []
        for p in data["packages"]:
            gpu_min = (
                p["video_sec"] * self.min_per_video_sec
                + p["posters"] * self.min_per_poster
            )
            videos = math.ceil(p["video_sec"] / self.max_single_video_sec_hint)
            self.packages.append(dict(
                p, gpu_min=gpu_min, videos=videos,
                segments=int(p["video_sec"] / self.segment_sec_hint),
            ))

        def weighted(field):
            return sum(p[field] * p["mix_share"] for p in self.packages)

        self.avg_revenue = weighted("price")
        self.avg_gpu_min = weighted("gpu_min")
        self.avg_video_sec = weighted("video_sec")
        self.avg_posters = weighted("posters")
        self.avg_captions = weighted("captions")

        # سهم ویدیو از کل زمان GPU
        self.video_share_of_gpu = (
            self.avg_video_sec * self.min_per_video_sec / self.avg_gpu_min
        )

        # ---------- هزینه ثابت ----------
        self.fixed_lines = []
        for row in data["fixed_costs"]:
            amount = (
                self.depreciation
                if row.get("computed") == "depreciation"
                else row["amount"]
            )
            self.fixed_lines.append(dict(row, amount=amount))
        self.fixed_total = sum(row["amount"] for row in self.fixed_lines)
        self.electricity = next(
            row["amount"] for row in self.fixed_lines if "برق" in row["label"]
        )

        # ---------- هزینه متغیر (سرور شخصی) ----------
        # دو حالت: «امروز» با آنچه واقعاً در کد هست، و «کامل» با اتصال‌های
        # برنامه‌ریزی‌شده. اقتصاد کوتاه‌مدت و بلندمدت با هم فرق دارد.
        v = data["variable_costs"]
        self.cost_instagram = (
            v["instagram_api"]["bundle_price"] / v["instagram_api"]["bundle_customers"]
        )
        self.instagram_active = v["instagram_api"].get("active", True)
        self.cost_captions = self.avg_captions * v["caption_api_per_unit"]["amount"]

        self.variable_today = self.cost_captions
        self.variable_planned = self.cost_captions + self.cost_instagram
        # پیش‌فرض عمداً محافظه‌کارانه است: انتشار خودکار در اینستاگرام بخشی از
        # قولِ محصول است، پس هزینه‌اش دیر یا زود می‌آید. حالت «امروز» فقط
        # به‌عنوان مزیت کوتاه‌مدت گزارش می‌شود، نه به‌عنوان سناریوی پایه.
        self.variable_per_customer = self.variable_planned

        # ---------- سر به سر و سقف ظرفیت ----------
        self.contribution = self.avg_revenue - self.variable_per_customer
        self.contribution_today = self.avg_revenue - self.variable_today
        self.contribution_planned = self.avg_revenue - self.variable_planned
        self.break_even = math.ceil(self.fixed_total / self.contribution)
        self.break_even_today = math.ceil(self.fixed_total / self.contribution_today)
        self.break_even_planned = math.ceil(self.fixed_total / self.contribution_planned)
        self.max_customers = math.floor(self.gpu_min_usable / self.avg_gpu_min)

        # ---------- محدودیت‌های موتور ویدیو (از کد) ----------
        self.segment_sec = r.get("segment_sec", 5)
        self.max_single_video_sec = r.get("max_single_video_sec", 60)

        # سقفی که مدل قدیمی می‌داد، چون فقط ویدیو را حساب می‌کرد
        self.max_customers_video_only = math.floor(
            self.gpu_min_usable / self.min_per_video_sec / self.avg_video_sec
        )

        # ---------- زیرساخت ----------
        self.infra = [self._infra(o) for o in data["infra_options"]]

        # ---------- سناریوها ----------
        self.scenarios = [self.pnl(n) for n in data["scenarios"]]
        self.at_capacity = self.pnl(self.max_customers)

        # ---------- توسعه با سیستم سوم ----------
        e = data["expansion"]
        n_sys = len(self.systems) + 1
        gpu_min_3 = (
            n_sys * a["uptime_hours_per_day"] * a["days_per_month"] * 60
            * (1 - a["derate"])
        )
        extra_fixed = (
            e["third_system_price"] / a["depreciation_months"]
            + e["third_system_electricity"]
        )
        self.expansion = {
            "price": e["third_system_price"],
            "label": e["label"],
            "systems": n_sys,
            "max_customers": math.floor(gpu_min_3 / self.avg_gpu_min),
            "extra_fixed": extra_fixed,
        }
        self.expansion["pnl"] = self.pnl(
            self.expansion["max_customers"], extra_fixed=extra_fixed
        )

    # ------------------------------------------------------------ زیرساخت

    def _infra(self, o: dict) -> dict:
        """هزینه‌ی واحد تولید را برای یک گزینه‌ی زیرساخت حساب می‌کند."""
        rate = self.a["usd_rate"]
        out = dict(o)

        if o["model"] == "api":
            # قیمت‌گذاری مستقیم روی خروجی، نه روی زمان GPU
            out["per_video_sec"] = o["video_usd_per_sec"] * rate
            out["per_poster"] = o["image_usd_each"] * rate
            out["per_gpu_min"] = None
            out["monthly_gpu_cost"] = None
        else:
            if o["model"] == "own":
                # GPU از قبل خریداری شده: هزینه‌اش استهلاک + برق است
                monthly = self.depreciation + self.electricity
                per_min = monthly / self.gpu_min_usable
                out["capex"] = self.capex
                out["monthly_gpu_cost"] = monthly
            else:  # rent — اجاره ساعتی، تبدیل به «دقیقه‌ی معادل RTX 3060»
                per_min = o["gpu_hour_usd"] * rate / 60 / o["speedup_vs_3060"]
                out["monthly_gpu_cost"] = per_min * self.gpu_min_usable
            out["per_gpu_min"] = per_min
            out["per_video_sec"] = per_min * self.min_per_video_sec
            out["per_poster"] = per_min * self.min_per_poster

        out["per_customer"] = (
            self.avg_video_sec * out["per_video_sec"]
            + self.avg_posters * out["per_poster"]
        )
        out["share_of_revenue"] = out["per_customer"] / self.avg_revenue
        return out

    def infra_by_id(self, key: str) -> dict:
        return next(o for o in self.infra if o["id"] == key)

    def sensitivity(self, rate: float) -> list:
        """هزینه‌ی تولید هر مشتری با یک نرخ دلار دلخواه."""
        rows = []
        for o in self.d["infra_options"]:
            if o["model"] == "own":
                cost = self.infra_by_id(o["id"])["per_customer"]
            elif o["model"] == "rent":
                per_min = o["gpu_hour_usd"] * rate / 60 / o["speedup_vs_3060"]
                cost = (
                    self.avg_video_sec * per_min * self.min_per_video_sec
                    + self.avg_posters * per_min * self.min_per_poster
                )
            else:
                cost = (
                    self.avg_video_sec * o["video_usd_per_sec"] * rate
                    + self.avg_posters * o["image_usd_each"] * rate
                )
            rows.append({
                "id": o["id"],
                "name": o["name"],
                "per_customer": cost,
                "share_of_revenue": cost / self.avg_revenue,
                "viable": cost < self.contribution,
            })
        return rows

    # ----------------------------------------------------------- سود و زیان

    def pnl(self, customers: int, extra_fixed: float = 0.0) -> dict:
        revenue = customers * self.avg_revenue
        variable = customers * self.variable_per_customer
        fixed = self.fixed_total + extra_fixed
        net = revenue - variable - fixed
        gpu_min = customers * self.avg_gpu_min
        n_sys = len(self.systems) + (1 if extra_fixed else 0)
        return {
            "customers": customers,
            "revenue": revenue,
            "variable": variable,
            "fixed": fixed,
            "net": net,
            "margin": net / revenue if revenue else 0.0,
            "gpu_hours": gpu_min / 60,
            "hours_per_system_per_day": gpu_min / 60 / n_sys / self.a["days_per_month"],
            "capacity_used": gpu_min / self.gpu_min_usable,
        }

    @property
    def payback_months(self) -> float:
        """بازگشت نقدی سرمایه در ظرفیت کامل (سود خالص + استهلاک)."""
        cash = self.at_capacity["net"] + self.depreciation
        return self.capex / cash if cash > 0 else float("inf")

    @property
    def payback_months_accounting(self) -> float:
        net = self.at_capacity["net"]
        return self.capex / net if net > 0 else float("inf")

    @property
    def gaps(self) -> list:
        """کارهای باقی‌مانده، مرتب بر اساس شدت."""
        order = {"blocker": 0, "high": 1, "medium": 2, "low": 3}
        return sorted(self.d.get("gaps", []), key=lambda g: order.get(g["severity"], 9))

    @property
    def code_facts(self) -> list:
        return self.d.get("code_facts", [])

    # ------------------------------------------------- ارزش برای مشتری

    def customer_roi(self) -> list:
        """در برابر هزینه‌ی تیم بازاریابی داخلی، هر پکیج چقدر صرفه دارد."""
        team = self.d["problem"]["team_cost_monthly"]
        rows = []
        for p in self.packages:
            rows.append({
                "name": p["name"],
                "price": p["price"],
                "video_sec": p["video_sec"],
                "posters": p["posters"],
                "captions": p["captions"],
                "highlight": p["highlight"],
                "saving": team - p["price"],
                "multiple": team / p["price"],
                "cheaper_by": 1 - p["price"] / team,
            })
        return rows

    @property
    def headline_roi(self) -> dict:
        """پکیج پرفروش، همان که در ارائه‌ی مشتری برجسته می‌شود."""
        return next(r for r in self.customer_roi() if r["highlight"])

    # ----------------------------------------------------------------- SOM

    def som(self) -> dict:
        s = self.d["market"]["som"]
        return {
            "min": s["min"],
            "max": s["max"],
            "revenue_min_year": s["min"] * self.avg_revenue * 12,
            "revenue_max_year": s["max"] * self.avg_revenue * 12,
            "systems_min": math.ceil(s["min"] / self.max_customers) * len(self.systems),
            "systems_max": math.ceil(s["max"] / self.max_customers) * len(self.systems),
        }


def load() -> Model:
    with DATA_FILE.open(encoding="utf-8") as fh:
        return Model(json.load(fh))


# -------------------------------------------------------------------- گزارش


def _report(m: Model) -> None:
    bar = "-" * 66
    print(bar)
    print("  مدل مالی آپ‌مارکت — محاسبه‌شده از data.json")
    print(bar)
    print(f"  سرمایه سخت‌افزار         {money(m.capex)} تومان")
    print(f"  استهلاک ماهانه           {money(m.depreciation)} تومان")
    print(f"  هزینه ثابت ماهانه        {money(m.fixed_total)} تومان")
    print()
    print(f"  ظرفیت GPU خام            {money(m.gpu_min_raw)} دقیقه/ماه")
    print(f"  ظرفیت مؤثر (منهای {pct(m.a['derate'])})   {money(m.gpu_min_usable)} دقیقه/ماه")
    print(f"  مصرف هر مشتری            {money(m.avg_gpu_min, 1)} دقیقه GPU"
          f"   (سهم ویدیو {pct(m.video_share_of_gpu)})")
    print()
    print(f"  درآمد میانگین هر مشتری   {money(m.avg_revenue)} تومان")
    print(f"  هزینه متغیر هر مشتری     {money(m.variable_per_customer)} تومان"
          f"   (امروز فقط {money(m.variable_today)})")
    print(f"  حاشیه مشارکت             {money(m.contribution)} تومان")
    print()
    print(f"  * نقطه سر به سر          {fa(m.break_even)} مشتری   (سناریوی پایه)")
    print(f"    امروز، تا وقتی اینستاگرام وصل نشده: {fa(m.break_even_today)} مشتری")
    print(f"  * سقف سخت‌افزار           {fa(m.max_customers)} مشتری")
    print(f"    (مدل قدیمی {fa(m.max_customers_video_only)} می‌داد — زمان پوستر را نادیده گرفته بود)")
    print()
    print(bar)
    print(f"  {'مشتری':>7} {'درآمد':>15} {'سود خالص':>16} {'حاشیه':>7} {'ساعت/سیستم':>12}")
    print(bar)
    for s in m.scenarios:
        hours = fa(f"{s['hours_per_system_per_day']:.1f}")
        print(f"  {fa(s['customers']):>7} {money(s['revenue']):>15} "
              f"{money(s['net']):>16} {pct(s['margin']):>7} {hours:>12}")
    print(bar)
    print()
    print("  هزینه تولید هر مشتری بر حسب زیرساخت:")
    for o in m.infra:
        flag = "   <-- برنامه‌ی ما" if o.get("recommended") else ""
        note = "" if o["share_of_revenue"] < 1 else "  (بیشتر از درآمد!)"
        print(f"    {o['name']:<12} {money(o['per_customer']):>13} تومان"
              f"  = {pct(o['share_of_revenue'])} از درآمد{note}{flag}")
    print()
    print(f"  بازگشت نقدی سرمایه       {fa(f'{m.payback_months:.1f}')} ماه")
    e = m.expansion
    print(f"  با {e['label']} ({fa(e['max_customers'])} مشتری): "
          f"سود {compact(e['pnl']['net'])} تومان/ماه، حاشیه {pct(e['pnl']['margin'])}")
    print()
    print("  کارهای باقی‌مانده:")
    for g in m.gaps:
        mark = {"blocker": "[!!]", "high": "[! ]", "medium": "[  ]"}.get(g["severity"], "[  ]")
        print(f"    {mark} {g['title']}")
    print(bar)


if __name__ == "__main__":
    _report(load())
