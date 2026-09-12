import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";

import SectionHead from "@/components/SectionHead";
import JsonLd from "@/components/JsonLd";
import { getPosts, getTags } from "@/lib/blog";
import { alternatesFor, DEFAULT_LOCALE, isLocale, localePath, LOCALES, type Locale } from "@/lib/i18n";
import { num } from "@/lib/plans";
import { breadcrumbs } from "@/lib/seo";

type Props = { params: Promise<{ locale: string }> };

export function generateStaticParams() {
  return LOCALES.map((locale) => ({ locale }));
}

const COPY = {
  fa: {
    eyebrow: "وبلاگ",
    title: "بازاریابی، فروش و هوش مصنوعی",
    lead: "آنچه در عمل برای فروشگاه‌های کوچک ایرانی کار می‌کند.",
    all: "همه",
    empty: "هنوز مقاله‌ای منتشر نشده است.",
    minutes: (n: string) => `${n} دقیقه مطالعه`,
    metaDesc:
      "مقالاتی درباره‌ی بازاریابی، فروش آنلاین و استفاده از هوش مصنوعی در کسب‌وکار کوچک.",
    persianNote: null as string | null,
  },
  en: {
    eyebrow: "Blog",
    title: "Marketing, sales and AI",
    lead: "What actually works for small Iranian shops.",
    all: "All",
    empty: "No articles published yet.",
    minutes: (n: string) => `${n} min read`,
    metaDesc:
      "Articles on marketing, online selling, and using AI in a small business.",
    // Said plainly rather than letting an English reader click into Persian
    // with no warning.
    persianNote: "The articles themselves are written in Persian.",
  },
} as const;

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { locale } = await params;
  if (!isLocale(locale)) return {};
  return {
    title: COPY[locale].eyebrow,
    description: COPY[locale].metaDesc,
    alternates: {
      ...alternatesFor(locale, "/blog"),
      types: { "application/rss+xml": "/feed.xml" },
    },
  };
}

export default async function Blog({ params }: Props) {
  const { locale } = await params;
  if (!isLocale(locale)) notFound();
  const l = locale as Locale;
  const c = COPY[l];
  const posts = getPosts();
  const tags = getTags();

  /** Articles exist only in Persian, so every article link points at the
   *  Persian URL regardless of which language the index is being read in. */
  const articleHref = (path: string) => localePath(DEFAULT_LOCALE, path);

  return (
    <section className="mesh">
      <JsonLd data={breadcrumbs([{ name: c.eyebrow, path: "/blog" }], l)} />
      <div className="wrap">
        <SectionHead as="h1" eyebrow={c.eyebrow} title={c.title} lead={c.lead} />

        {c.persianNote && <p className="muted center mt-sm">{c.persianNote}</p>}

        <div className="row mt-md center-row">
          <span className="tag-link on">{c.all}</span>
          {tags.map((t) => (
            <Link
              key={t}
              href={articleHref(`/blog/tag/${encodeURIComponent(t)}`)}
              className="tag-link"
            >
              {t}
            </Link>
          ))}
          <a href="/feed.xml" className="tag-link">
            RSS
          </a>
        </div>

        {posts.length === 0 ? (
          <p className="muted center mt-lg">{c.empty}</p>
        ) : (
          <div className="grid g3 mt-lg">
            {posts.map((post) => (
              <Link
                key={post.slug}
                href={articleHref(`/blog/${post.slug}`)}
                className="card card-hover plain"
                lang="fa"
                dir="rtl"
              >
                <div className="row-tight">
                  {post.tags.slice(0, 2).map((t) => (
                    <span key={t} className="eyebrow">
                      {t}
                    </span>
                  ))}
                </div>
                <h2 className="mt-sm" style={{ fontSize: "1.1rem" }}>
                  {post.title}
                </h2>
                <p className="muted mt-sm">{post.description}</p>
                <div className="muted mt" style={{ fontSize: ".76rem" }}>
                  {post.date} · {c.minutes(num(post.readingMinutes, l))}
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </section>
  );
}
