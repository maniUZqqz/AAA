import type { Metadata } from "next";

import JsonLd from "@/components/JsonLd";
import SectionHead from "@/components/SectionHead";
import { breadcrumbs, faqPage } from "@/lib/seo";
import { faq, site } from "@/lib/content";

export const metadata: Metadata = {
  title: "سؤالات متداول",
  description: "پاسخ سؤالات رایج درباره‌ی نحوه‌ی کار، قیمت، امنیت داده و خروجی آپ‌مارکت.",
  alternates: { canonical: "/faq" },
};

export default function FAQ() {
  return (
    <>
      <JsonLd data={[breadcrumbs([{ name: "سؤالات متداول", path: "/faq" }]), faqPage(faq)]} />

      <section className="mesh">
        <div className="wrap w-md">
          <SectionHead eyebrow="سؤالات متداول" title="آنچه معمولاً پرسیده می‌شود" />
          <div className="stack-sm mt-lg">
            {faq.map((f) => (
              <details key={f.q} className="card qa">
                <summary>{f.q}</summary>
                <p>{f.a}</p>
              </details>
            ))}
          </div>

          <p className="muted center mt-lg">
            سؤال دیگری دارید؟{" "}
            <a href={`mailto:${site.email}`} style={{ color: "var(--color-brand-600)" }}>
              برایمان بنویسید
            </a>
            .
          </p>
        </div>
      </section>

    </>
  );
}
