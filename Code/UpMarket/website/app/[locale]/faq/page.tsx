import type { Metadata } from "next";
import { notFound } from "next/navigation";

import JsonLd from "@/components/JsonLd";
import SectionHead from "@/components/SectionHead";
import { contentFor, siteFor } from "@/lib/content";
import { alternatesFor, isLocale, LOCALES, type Locale } from "@/lib/i18n";
import { breadcrumbs, faqPage } from "@/lib/seo";

type Props = { params: Promise<{ locale: string }> };

export function generateStaticParams() {
  return LOCALES.map((locale) => ({ locale }));
}

const COPY = {
  fa: {
    eyebrow: "سؤالات متداول",
    title: "آنچه معمولاً پرسیده می‌شود",
    more: "سؤال دیگری دارید؟ ",
    write: "برایمان بنویسید",
    metaDesc: "پاسخ سؤالات رایج درباره‌ی نحوه‌ی کار، قیمت، امنیت داده و خروجی آپ‌مارکت.",
  },
  en: {
    eyebrow: "FAQ",
    title: "The questions we get asked",
    more: "Something else on your mind? ",
    write: "Write to us",
    metaDesc: "Common questions about how it works, pricing, data handling and output.",
  },
} as const;

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { locale } = await params;
  if (!isLocale(locale)) return {};
  return {
    title: COPY[locale].eyebrow,
    description: COPY[locale].metaDesc,
    alternates: alternatesFor(locale, "/faq"),
  };
}

export default async function FAQ({ params }: Props) {
  const { locale } = await params;
  if (!isLocale(locale)) notFound();
  const l = locale as Locale;
  const c = COPY[l];
  const { faq } = contentFor(l);
  const site = siteFor(l);

  return (
    <>
      <JsonLd
        data={[breadcrumbs([{ name: c.eyebrow, path: "/faq" }], l), faqPage(faq)]}
      />

      <section className="mesh">
        <div className="wrap w-md">
          <SectionHead as="h1" eyebrow={c.eyebrow} title={c.title} />
          <div className="stack-sm mt-lg">
            {faq.map((f) => (
              <details key={f.q} className="card qa">
                <summary>{f.q}</summary>
                <p>{f.a}</p>
              </details>
            ))}
          </div>

          <p className="muted center mt-lg">
            {c.more}
            <a href={`mailto:${site.email}`} style={{ color: "var(--color-brand-600)" }}>
              {c.write}
            </a>
            .
          </p>
        </div>
      </section>
    </>
  );
}
