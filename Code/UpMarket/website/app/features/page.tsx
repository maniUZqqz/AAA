import type { Metadata } from "next";
import Link from "next/link";

import JsonLd from "@/components/JsonLd";
import SectionHead from "@/components/SectionHead";
import { capabilities, features, site } from "@/lib/content";
import { breadcrumbs } from "@/lib/seo";

export const metadata: Metadata = {
  title: "قابلیت‌ها",
  description:
    "هوش محصول، تحلیل رقبا، استودیوی تصویر و ویدیو، موتور کپشن و پشتیبان فروش — " +
    "همه در یک جریان.",
  alternates: { canonical: "/features" },
};

/** Engineering decisions worth stating on a marketing page, because each one
 *  answers a doubt a careful buyer already has. */
const guarantees = [
  {
    icon: "🖼️",
    title: "از عکس واقعی، نه از صفر",
    desc: "پوستر روی عکس خود محصول ساخته می‌شود. مشتری همان چیزی را می‌بیند که می‌خرد.",
  },
  {
    icon: "🔤",
    title: "متن فارسی با کد، نه با مدل",
    desc: "حروف فارسی روی تصویر با کد نوشته می‌شوند تا هرگز به‌هم نریزند.",
  },
  {
    icon: "🔢",
    title: "عدد ساخته نمی‌شود",
    desc: "قیمت، موجودی و اطلاعات پرداخت فقط از دیتابیس خودتان خوانده می‌شود.",
  },
  {
    icon: "🔗",
    title: "ویدیوی پیوسته",
    desc: "هر قطعه از فریم آخر قبلی شروع می‌شود؛ نتیجه یک ویدیو است نه اسلایدشو.",
  },
  {
    icon: "🔁",
    title: "خطا کل کار را خراب نمی‌کند",
    desc: "اگر قطعه‌ای شکست بخورد فقط همان دوباره ساخته می‌شود و سهمیه‌اش برمی‌گردد.",
  },
  {
    icon: "👤",
    title: "انسان تصمیم می‌گیرد",
    desc: "انتشار و تأیید پرداخت هرگز خودکار نیست.",
  },
];

export default function Features() {
  return (
    <>
      <JsonLd data={breadcrumbs([{ name: "قابلیت‌ها", path: "/features" }])} />

      <section className="mesh">
        <div className="wrap">
          <SectionHead
            eyebrow="قابلیت‌ها"
            title="کاری که آپ‌مارکت انجام می‌دهد"
            lead="نه چند ابزار جدا — یک جریان که از محصول شما شروع می‌شود و به فروش می‌رسد."
          />
          <div className="band-grid mt-lg">
            {capabilities.map((c) => (
              <div key={c.label} className="band-item">
                <div className="v gradient-text">{c.value}</div>
                <div className="l">{c.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {features.map((f, index) => (
        <section
          key={f.id}
          id={f.id}
          className={index % 2 ? "section-soft" : ""}
          style={{ paddingBlock: "clamp(32px, 5vw, 64px)" }}
        >
          <div className="wrap">
            <div className="grid g2">
              <div className={index % 2 ? "" : "reveal"}>
                <div className="icon-xl">{f.icon}</div>
                <h2 className="mt">{f.title}</h2>
                <p className="lead mt-sm">{f.lead}</p>
              </div>
              <div className="card">
                <ul className="checks">
                  {f.bullets.map((b) => (
                    <li key={b}>{b}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        </section>
      ))}

      {/* ----------------------------------------------------- guarantees */}
      <section className="section-soft">
        <div className="wrap">
          <SectionHead
            eyebrow="تصمیم‌های مهندسی"
            title="چیزهایی که عمداً این‌طور ساخته شده‌اند"
            lead="هرکدام جواب یک نگرانی واقعی است، نه یک ویژگی تبلیغاتی."
          />
          <div className="grid g3 mt-lg">
            {guarantees.map((g) => (
              <article key={g.title} className="card">
                <div className="icon-lg">{g.icon}</div>
                <h3 className="mt-sm">{g.title}</h3>
                <p className="muted mt-sm">{g.desc}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section>
        <div className="wrap">
          <div className="cta-band">
            <h2>امتحانش رایگان است</h2>
            <p className="lead mt narrower">دو هفته، بدون کارت بانکی.</p>
            <div className="row mt-md center-row">
              <a href={`${site.panelUrl}/register`} className="btn btn-primary">
                شروع رایگان ←
              </a>
              <Link href="/pricing" className="btn btn-ghost">
                دیدن قیمت‌ها
              </Link>
            </div>
          </div>
        </div>
      </section>
    </>
  );
}
