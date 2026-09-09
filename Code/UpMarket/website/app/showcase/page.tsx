import type { Metadata } from "next";
import Link from "next/link";

import works from "@/content/showcase/works.json";
import JsonLd from "@/components/JsonLd";
import SectionHead from "@/components/SectionHead";
import { site } from "@/lib/content";
import { breadcrumbs } from "@/lib/seo";

export const metadata: Metadata = {
  title: "نمونه‌کار",
  description:
    "پوستر، ویدیو و کپشن واقعی تولیدشده با آپ‌مارکت — برای پوشاک، اکسسوری و دکوراسیون.",
  alternates: { canonical: "/showcase" },
};

type Work = {
  id: string;
  category: string;
  product: string;
  image: string;
  videos: string[];
  caption: string;
};

/**
 * Content comes from `content/showcase/works.json`, written by
 * `scripts/sync-showcase.mjs` at build time from the real sample folder.
 * Reading the sibling folder directly at render time made the page depend on
 * a path that does not exist once the site is deployed on its own.
 */
export default function Showcase() {
  const items = works as Work[];

  return (
    <>
      <JsonLd data={breadcrumbs([{ name: "نمونه‌کار", path: "/showcase" }])} />

      <section className="mesh">
        <div className="wrap">
          <SectionHead
            eyebrow="نمونه‌کار"
            title="خروجی واقعی، نه نمونه‌ی تبلیغاتی"
            lead="این‌ها با همان سیستمی ساخته شده‌اند که شما استفاده می‌کنید."
          />

          {items.length === 0 ? (
            <p className="muted center mt-lg">نمونه‌کارها در حال آماده‌سازی‌اند.</p>
          ) : (
            <div className="stack mt-lg gap-lg">
              {items.map((w) => (
                <article key={w.id} className="card">
                  <div className="row-tight">
                    <span className="eyebrow">{w.category}</span>
                    <h2 style={{ fontSize: "1.15rem" }}>{w.product}</h2>
                  </div>

                  <div className="grid g2 mt">
                    <div>
                      {/* eslint-disable-next-line @next/next/no-img-element */}
                      <img
                        className="shot"
                        src={w.image}
                        alt={`پوستر تبلیغاتی تولیدشده با آپ‌مارکت برای ${w.product}`}
                        width={1024}
                        height={1024}
                        loading="lazy"
                      />
                      {w.videos.length > 0 && (
                        <div className="strip">
                          {w.videos.map((v, i) => (
                            <video
                              key={v}
                              src={v}
                              muted
                              loop
                              playsInline
                              autoPlay
                              preload="metadata"
                              aria-label={`قطعه ${i + 1} از ویدیوی ${w.product}`}
                            />
                          ))}
                        </div>
                      )}
                    </div>

                    <div>
                      <div className="muted mb-sm">
                        کپشن تولیدشده
                      </div>
                      <div className="caption-box">{w.caption}</div>
                    </div>
                  </div>
                </article>
              ))}
            </div>
          )}
        </div>
      </section>

      <section className="section-soft">
        <div className="wrap">
          <SectionHead
            eyebrow="چطور ساخته شدند"
            title="همان مسیری که برای شما طی می‌شود"
          />
          <div className="grid g4 mt-lg">
            {[
              { icon: "📷", t: "عکس محصول", d: "ورودی: یک عکس واقعی، بدون استودیو" },
              { icon: "🧠", t: "تحلیل", d: "مدل بینایی عکس را می‌خواند، مدل استدلال استراتژی می‌سازد" },
              { icon: "🎨", t: "تولید", d: "پوستر، ویدیو و کپشن از همان یک ورودی" },
              { icon: "✅", t: "تأیید", d: "شما می‌بینید و تصمیم می‌گیرید" },
            ].map((s) => (
              <article key={s.t} className="card">
                <div className="icon-lg">{s.icon}</div>
                <h3 className="mt-sm">{s.t}</h3>
                <p className="muted mt-sm">{s.d}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section>
        <div className="wrap">
          <div className="cta-band">
            <h2>نمونه‌ی محصول خودتان را بگیرید</h2>
            <p className="lead mt narrower">
              فروشگاهتان را ثبت کنید و در همین جلسه ببینید خروجی برای
              محصول خودتان چه شکلی است.
            </p>
            <div className="row mt-md center-row">
              <a href={`${site.panelUrl}/register`} className="btn btn-primary">
                شروع رایگان ←
              </a>
              <Link href="/pricing" className="btn btn-ghost">دیدن قیمت‌ها</Link>
            </div>
          </div>
        </div>
      </section>
    </>
  );
}
