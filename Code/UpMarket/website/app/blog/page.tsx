import type { Metadata } from "next";
import Link from "next/link";

import SectionHead from "@/components/SectionHead";
import JsonLd from "@/components/JsonLd";
import { getPosts, getTags } from "@/lib/blog";
import { breadcrumbs } from "@/lib/seo";
import { fa } from "@/lib/plans";

export const metadata: Metadata = {
  title: "وبلاگ",
  description: "مقالاتی درباره‌ی بازاریابی، فروش آنلاین و استفاده از هوش مصنوعی در کسب‌وکار کوچک.",
  alternates: { canonical: "/blog", types: { "application/rss+xml": "/feed.xml" } },
};

export default function Blog() {
  const posts = getPosts();
  const tags = getTags();

  return (
    <section className="mesh">
      <JsonLd data={breadcrumbs([{ name: "وبلاگ", path: "/blog" }])} />
      <div className="wrap">
        <SectionHead
          eyebrow="وبلاگ"
          title="بازاریابی، فروش و هوش مصنوعی"
          lead="آنچه در عمل برای فروشگاه‌های کوچک ایرانی کار می‌کند."
        />

        <div className="row mt-md center-row">
          <span className="tag-link on">همه</span>
          {tags.map((t) => (
            <Link key={t} href={`/blog/tag/${encodeURIComponent(t)}`} className="tag-link">
              {t}
            </Link>
          ))}
          <a href="/feed.xml" className="tag-link">RSS</a>
        </div>

        {posts.length === 0 ? (
          <p className="muted center mt-lg">
            هنوز مقاله‌ای منتشر نشده است.
          </p>
        ) : (
          <div className="grid g3 mt-lg">
            {posts.map((post) => (
              <Link
                key={post.slug}
                href={`/blog/${post.slug}`}
                className="card card-hover plain"
              >
                <div className="row-tight">
                  {post.tags.slice(0, 2).map((t) => (
                    <span key={t} className="eyebrow">{t}</span>
                  ))}
                </div>
                <h2 className="mt-sm" style={{ fontSize: "1.1rem" }}>{post.title}</h2>
                <p className="muted mt-sm">{post.description}</p>
                <div className="muted mt" style={{ fontSize: ".76rem" }}>
                  {post.date} · {fa(post.readingMinutes)} دقیقه مطالعه
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </section>
  );
}
