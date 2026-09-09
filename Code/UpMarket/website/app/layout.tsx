import type { Metadata, Viewport } from "next";

import "@fontsource/vazirmatn/arabic-300.css";
import "@fontsource/vazirmatn/arabic-400.css";
import "@fontsource/vazirmatn/arabic-600.css";
import "@fontsource/vazirmatn/arabic-700.css";
import "@fontsource/vazirmatn/arabic-800.css";
import "./globals.css";

import Footer from "@/components/Footer";
import Header from "@/components/Header";
import JsonLd from "@/components/JsonLd";
import { site } from "@/lib/content";
import { SITE_URL, organization, website } from "@/lib/seo";

export const metadata: Metadata = {
  metadataBase: new URL(SITE_URL),
  title: {
    default: `${site.name} — ${site.tagline}`,
    template: `%s | ${site.name}`,
  },
  description: site.oneLiner,
  applicationName: site.name,
  keywords: [
    "بازاریابی هوش مصنوعی",
    "تولید محتوا با هوش مصنوعی",
    "پوستر تبلیغاتی",
    "ویدیو تبلیغاتی",
    "کپشن اینستاگرام",
    "فروشگاه آنلاین",
    "تحلیل رقبا",
    "SaaS ایرانی",
    "دستیار فروش",
  ],
  authors: [{ name: site.name, url: SITE_URL }],
  creator: site.name,
  publisher: site.name,
  openGraph: {
    type: "website",
    locale: "fa_IR",
    url: SITE_URL,
    siteName: site.name,
    title: `${site.name} — ${site.tagline}`,
    description: site.oneLiner,
  },
  twitter: {
    card: "summary_large_image",
    title: `${site.name} — ${site.tagline}`,
    description: site.oneLiner,
  },
  robots: {
    index: true,
    follow: true,
    googleBot: { index: true, follow: true, "max-image-preview": "large" },
  },
  alternates: {
    canonical: "/",
    types: { "application/rss+xml": "/feed.xml" },
  },
  manifest: "/manifest.webmanifest",
  formatDetection: { telephone: false },
};

export const viewport: Viewport = {
  themeColor: [
    { media: "(prefers-color-scheme: light)", color: "#ffffff" },
    { media: "(prefers-color-scheme: dark)", color: "#0b1120" },
  ],
  colorScheme: "light dark",
};

/**
 * Applied before paint so a reader who chose dark never sees a white flash.
 * It only reads storage and stamps an attribute — no styling decisions here.
 */
const themeBoot = `
(function(){try{var t=localStorage.getItem("upmarket-theme");
if(t==="dark"||t==="light")document.documentElement.setAttribute("data-theme",t);
}catch(e){}})();`;

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="fa" dir="rtl" suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: themeBoot }} />
        <JsonLd data={[organization(), website()]} />
      </head>
      <body>
        <a href="#main" className="skip-link">پرش به محتوا</a>
        <Header />
        <main id="main">{children}</main>
        <Footer />
      </body>
    </html>
  );
}
