import type { MetadataRoute } from "next";

import { getPosts, getTags } from "@/lib/blog";
import { sitemapPages } from "@/lib/content";
import { DEFAULT_LOCALE, LOCALES, localePath, type Locale } from "@/lib/i18n";
import { comparisonSlugs } from "@/lib/compare";
import { featureSlugs } from "@/lib/featurePages";
import { toolSlugs } from "@/lib/tools/meta";
import { legalDocsFor } from "@/lib/legal";
import { SITE_URL } from "@/lib/seo";
import { solutionSlugs } from "@/lib/solutions";
import { useCaseSlugs } from "@/lib/useCases";

/**
 * Priorities reflect what actually earns traffic: the home page and pricing
 * convert, solution and use-case pages catch intent, articles bring people in,
 * legal pages just need to exist.
 *
 * This reads `sitemapPages` rather than the header nav on purpose — a
 * navigation tweak should never silently drop pages out of Google.
 *
 * Blog posts are listed once, under Persian only. They are written in Persian
 * and have no English counterpart; advertising `/en/blog/<persian-slug>` would
 * point Google at a page that does not exist.
 */
export default function sitemap(): MetadataRoute.Sitemap {
  const now = new Date();

  const entry = (
    locale: Locale,
    path: string,
    priority: number,
    changeFrequency: "weekly" | "monthly" | "yearly" = "monthly",
  ) => ({
    url: `${SITE_URL}${localePath(locale, path)}`,
    lastModified: now,
    changeFrequency,
    priority,
  });

  const perLocale = LOCALES.flatMap((locale) => [
    entry(locale, "/", 1, "weekly"),

    ...sitemapPages.map((path) =>
      entry(
        locale,
        path,
        path === "/pricing" ? 0.9 : 0.7,
        path === "/blog" ? "weekly" : "monthly",
      ),
    ),

    // Intent-capturing pages — the reason the SEO architecture exists.
    ...solutionSlugs.map((slug) => entry(locale, `/solutions/${slug}`, 0.8)),
    ...useCaseSlugs.map((slug) => entry(locale, `/use-cases/${slug}`, 0.8)),
    ...featureSlugs.map((slug) => entry(locale, `/features/${slug}`, 0.8)),
    // Free tools are an acquisition channel, so they rank as high as the
    // intent pages; comparisons catch late, high-value decision searches.
    ...toolSlugs.map((slug) => entry(locale, `/tools/${slug}`, 0.8)),
    ...comparisonSlugs.map((slug) => entry(locale, `/compare/${slug}`, 0.7)),

    ...legalDocsFor(locale).map((d) => entry(locale, `/${d.slug}`, 0.3, "yearly")),
  ]);

  const articles = [
    ...getPosts().map((p) => entry(DEFAULT_LOCALE, `/blog/${p.slug}`, 0.6)),
    ...getTags().map((tag) =>
      entry(DEFAULT_LOCALE, `/blog/tag/${encodeURIComponent(tag)}`, 0.5, "weekly"),
    ),
  ];

  return [...perLocale, ...articles];
}
