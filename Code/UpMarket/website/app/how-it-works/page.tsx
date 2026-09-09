import type { Metadata } from "next";
import Link from "next/link";

import JsonLd from "@/components/JsonLd";
import SectionHead from "@/components/SectionHead";
import { site, steps } from "@/lib/content";
import { fa } from "@/lib/plans";
import { breadcrumbs, howTo } from "@/lib/seo";

export const metadata: Metadata = {
  title: "چطور کار می‌کند",
  description: "شش قدم از ثبت فروشگاه تا انتشار خودکار در اینستاگرام.",
  alternates: { canonical: "/how-it-works" },
};

/** What the owner does vs what the system does — the split people ask about
 *  before they trust an automation with their storefront. */
const split = [
  {
    icon: "🙋",
    title: "کاری که شما می‌کنید",
    items: [
      "یک‌بار برند و لحن فروشگاه را ثبت می‌کنید",
      "محصول را با عکس واقعی اضافه می‌کنید",
      "خروجی را می‌بینید و تأیید یا رد می‌کنید",
      "پرداخت مشتری را تأیید می‌کنید",
    ],
    tone: "brand",
  },
  {
    icon: "⚙️",
    title: "کاری که سیستم می‌کند",
    items: [
      "عکس محصول را تحلیل می‌کند",
      "قیمت و موضع رقبا را از وب درمی‌آورد",
      "پوستر، ویدیو و کپشن می‌سازد",
      "به دایرکت مشتری پاسخ می‌دهد و سفارش ثبت می‌کند",
      "بعد از تأیید شما منتشر می‌کند",
    ],
    tone: "ok",
  },
];

export default function HowItWorks() {
  return (
    <>
      <JsonLd
        data={[breadcrumbs([{ name: "چطور کار می‌کند", path: "/how-it-works" }]), howTo(steps)]}
      />

      <section className="mesh">
        <div className="wrap">
          <SectionHead
            eyebrow="فرایند"
            title="از ثبت محصول تا انتشار"
            lead="یک‌بار تنظیم می‌کنید؛ بعد از آن فقط تأیید می‌کنید."
          />
        </div>
      </section>

      {/* ------------------------------------------------------- timeline */}
      <section style={{ paddingTop: 0 }}>
        <div className="wrap narrow">
          <div className="timeline">
            {steps.map((s, i) => (
              <div key={s.n} className={`tl-item reveal reveal-${(i % 3) + 1}`}>
                <div className="tl-dot">{s.icon}</div>
                <div className="tl-body">
                  <div className="row-tight">
                    <span className="eyebrow">قدم {s.n}</span>
                    {i === steps.length - 1 && <span className="muted">پایان</span>}
                  </div>
                  <h2 className="mt-sm" style={{ fontSize: "1.15rem" }}>
                    {s.title}
                  </h2>
                  <p className="mt-sm" style={{ color: "var(--text-2)", fontSize: ".95rem" }}>
                    {s.desc}
                  </p>
                  <p className="muted mt-sm">{s.detail}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ---------------------------------------------------------- split */}
      <section className="section-soft">
        <div className="wrap">
          <SectionHead
            eyebrow="تقسیم کار"
            title="چه چیزی دست شماست، چه چیزی خودکار"
            lead="هیچ تصمیم مهمی بدون شما گرفته نمی‌شود."
          />
          <div className="grid g2 mt-lg">
            {split.map((s) => (
              <article key={s.title} className="card">
                <div className="icon-lg">{s.icon}</div>
                <h3 className="mt-sm">{s.title}</h3>
                <ul className="checks mt">
                  {s.items.map((i) => (
                    <li key={i}>{i}</li>
                  ))}
                </ul>
              </article>
            ))}
          </div>
        </div>
      </section>

      {/* --------------------------------------------------------- timing */}
      <section>
        <div className="wrap">
          <SectionHead eyebrow="زمان" title="هر مرحله چقدر طول می‌کشد" />
          <div className="grid g4 mt-lg">
            <div className="card stat">
              <div className="v gradient-text">{fa(1)}–{fa(2)}</div>
              <div className="l">دقیقه برای تحلیل محصول</div>
            </div>
            <div className="card stat">
              <div className="v gradient-text">~{fa(2)}</div>
              <div className="l">دقیقه برای هر تصویر</div>
            </div>
            <div className="card stat">
              <div className="v gradient-text">چند ثانیه</div>
              <div className="l">برای هر کپشن</div>
            </div>
            <div className="card stat">
              <div className="v gradient-text">چند دقیقه</div>
              <div className="l">برای ویدیو — پیشرفتش را زنده می‌بینید</div>
            </div>
          </div>
          <p className="muted center mt-md narrow">
            ویدیو سنگین‌ترین بخش است چون هر ثانیه‌اش جداگانه رندر می‌شود.
            لازم نیست منتظر بمانید — می‌توانید صفحه را ببندید و بعداً برگردید.
          </p>
        </div>
      </section>

      <section className="section-soft">
        <div className="wrap">
          <div className="cta-band">
            <h2>اولین بسته‌ی محتوا در همین جلسه</h2>
            <p className="lead mt narrower">دو هفته رایگان، بدون کارت بانکی.</p>
            <div className="row mt-md center-row">
              <a href={`${site.panelUrl}/register`} className="btn btn-primary">
                شروع رایگان ←
              </a>
              <Link href="/showcase" className="btn btn-ghost">
                اول نمونه‌کارها را ببینم
              </Link>
            </div>
          </div>
        </div>
      </section>
    </>
  );
}
