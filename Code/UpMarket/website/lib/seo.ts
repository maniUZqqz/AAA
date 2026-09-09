/**
 * Structured data helpers.
 *
 * Google reads these to build rich results — a price shown in search, an FAQ
 * expanded under the link, a breadcrumb trail. Each builder returns a plain
 * object; the caller drops it into a <script type="application/ld+json">.
 */
import { site } from "./content";

export const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL || "https://upmarket.ir";

export function abs(path = ""): string {
  return `${SITE_URL}${path}`;
}

export function organization() {
  return {
    "@context": "https://schema.org",
    "@type": "Organization",
    name: site.name,
    alternateName: site.nameEn,
    url: SITE_URL,
    logo: abs("/icon.png"),
    email: site.email,
    sameAs: [site.instagram],
    description: site.oneLiner,
    areaServed: { "@type": "Country", name: "ایران" },
  };
}

export function website() {
  return {
    "@context": "https://schema.org",
    "@type": "WebSite",
    name: site.name,
    url: SITE_URL,
    inLanguage: "fa-IR",
    publisher: { "@type": "Organization", name: site.name },
  };
}

/** Breadcrumbs help Google show the section instead of a bare URL. */
export function breadcrumbs(trail: { name: string; path: string }[]) {
  return {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: [{ name: "خانه", path: "/" }, ...trail].map((item, i) => ({
      "@type": "ListItem",
      position: i + 1,
      name: item.name,
      item: abs(item.path),
    })),
  };
}

/** One offer per plan, so search can show the real starting price. */
export function offers(
  plans: { name: string; slug: string; price_toman: number; description: string }[],
) {
  return {
    "@context": "https://schema.org",
    "@type": "Product",
    name: site.name,
    description: site.oneLiner,
    brand: { "@type": "Brand", name: site.name },
    offers: plans.map((p) => ({
      "@type": "Offer",
      name: p.name,
      price: p.price_toman,
      priceCurrency: "IRR",
      description: p.description,
      url: abs(`/pricing#${p.slug}`),
      availability: "https://schema.org/InStock",
      priceValidUntil: `${new Date().getFullYear() + 1}-01-01`,
    })),
  };
}

export function howTo(steps: { title: string; desc: string }[]) {
  return {
    "@context": "https://schema.org",
    "@type": "HowTo",
    name: "چطور با آپ‌مارکت محتوای تبلیغاتی بسازیم",
    description: "از ثبت فروشگاه تا انتشار خودکار در اینستاگرام.",
    step: steps.map((s, i) => ({
      "@type": "HowToStep",
      position: i + 1,
      name: s.title,
      text: s.desc,
    })),
  };
}

export function faqPage(items: { q: string; a: string }[]) {
  return {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    mainEntity: items.map((f) => ({
      "@type": "Question",
      name: f.q,
      acceptedAnswer: { "@type": "Answer", text: f.a },
    })),
  };
}

export function blogPosting(post: {
  title: string;
  description: string;
  date: string;
  author: string;
  slug: string;
  tags: string[];
}) {
  return {
    "@context": "https://schema.org",
    "@type": "BlogPosting",
    headline: post.title,
    description: post.description,
    datePublished: post.date,
    keywords: post.tags.join(", "),
    inLanguage: "fa-IR",
    author: { "@type": "Organization", name: post.author },
    publisher: {
      "@type": "Organization",
      name: site.name,
      logo: { "@type": "ImageObject", url: abs("/icon.png") },
    },
    mainEntityOfPage: { "@type": "WebPage", "@id": abs(`/blog/${post.slug}`) },
  };
}

/** Small component-free helper so pages stay tidy. */
export function jsonLd(data: unknown) {
  return {
    type: "application/ld+json",
    dangerouslySetInnerHTML: { __html: JSON.stringify(data) },
  };
}
