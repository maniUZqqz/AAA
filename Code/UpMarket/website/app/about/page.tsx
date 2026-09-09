import type { Metadata } from "next";

import JsonLd from "@/components/JsonLd";
import SectionHead from "@/components/SectionHead";
import { breadcrumbs } from "@/lib/seo";
import { about, site } from "@/lib/content";

export const metadata: Metadata = {
  title: "درباره ما",
  description: "چرا آپ‌مارکت را ساختیم و چه اصولی در محصول رعایت می‌کنیم.",
  alternates: { canonical: "/about" },
};

export default function About() {
  return (
    <>
      <JsonLd data={breadcrumbs([{ name: "درباره ما", path: "/about" }])} />
      <section>
        <div className="wrap" style={{ maxWidth: 760, textAlign: "center" }}>
          <span className="eyebrow">درباره ما</span>
          <h1 style={{ marginTop: 18, fontSize: "clamp(1.7rem, 4vw, 2.6rem)" }}>
            بازاریابی حرفه‌ای نباید امتیاز شرکت‌های بزرگ باشد
          </h1>
          <p className="lead" style={{ marginTop: 20 }}>{about.mission}</p>
        </div>
      </section>

      <section className="section-soft">
        <div className="wrap">
          <SectionHead title="چطور به اینجا رسیدیم" />
          <div className="grid g3 mt-lg">
            {about.story.map((s, i) => (
              <div key={s.title} className="card">
                <span className="eyebrow">{["۱", "۲", "۳"][i]}</span>
                <h3 className="mt">{s.title}</h3>
                <p className="muted" style={{ marginTop: 8, lineHeight: 2 }}>{s.text}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section>
        <div className="wrap">
          <SectionHead title="اصولی که رعایت می‌کنیم" />
          <div className="grid g4 mt-lg">
            {about.values.map((v) => (
              <div key={v.title} className="card">
                <div className="icon-lg">{v.icon}</div>
                <h3 className="mt-sm">{v.title}</h3>
                <p className="muted mt-sm">{v.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="section-soft">
        <div className="wrap" style={{ textAlign: "center" }}>
          <h2>با ما کار کنید</h2>
          <a href={`${site.panelUrl}/register`} className="btn btn-primary mt-md">
            شروع رایگان →
          </a>
        </div>
      </section>
    </>
  );
}
