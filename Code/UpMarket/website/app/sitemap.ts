import type { MetadataRoute } from "next";

import { getPosts, getTags } from "@/lib/blog";
import { nav } from "@/lib/content";
import { SITE_URL } from "@/lib/seo";

/** Priorities reflect what actually earns traffic: the home page and the
 *  pricing page convert, articles bring people in, the rest supports them. */
export default function sitemap(): MetadataRoute.Sitemap {
  const now = new Date();

  const pages = ["", ...nav.map((n) => n.href)].map((href) => ({
    url: `${SITE_URL}${href}`,
    lastModified: now,
    changeFrequency: (href === "" || href === "/blog" ? "weekly" : "monthly") as
      | "weekly"
      | "monthly",
    priority: href === "" ? 1 : href === "/pricing" ? 0.9 : 0.7,
  }));

  const posts = getPosts().map((p) => ({
    url: `${SITE_URL}/blog/${p.slug}`,
    lastModified: now,
    changeFrequency: "monthly" as const,
    priority: 0.6,
  }));

  const tags = getTags().map((tag) => ({
    url: `${SITE_URL}/blog/tag/${encodeURIComponent(tag)}`,
    lastModified: now,
    changeFrequency: "weekly" as const,
    priority: 0.5,
  }));

  return [...pages, ...posts, ...tags];
}
