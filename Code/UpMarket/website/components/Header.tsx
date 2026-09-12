"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";

import { siteFor } from "@/lib/content";
import { dict } from "@/lib/dict";
import { localePath, stripLocale, type Locale } from "@/lib/i18n";

import LocaleToggle from "./LocaleToggle";
import ThemeToggle from "./ThemeToggle";

export default function Header({ locale }: { locale: Locale }) {
  const path = usePathname();
  const [open, setOpen] = useState(false);
  const site = siteFor(locale);
  const t = dict(locale);
  // Compare against the locale-free path so the active pill highlights on
  // /en/pricing exactly as it does on /pricing.
  const bare = stripLocale(path || "/");

  return (
    <header
      style={{
        position: "sticky", top: 0, zIndex: 50,
        background: "color-mix(in srgb, var(--bg) 88%, transparent)",
        backdropFilter: "blur(12px)",
        borderBottom: "1px solid var(--line)",
      }}
    >
      <div
        className="wrap"
        style={{ display: "flex", alignItems: "center", gap: 16, height: 64 }}
      >
        <Link
          href={localePath(locale, "/")}
          style={{ textDecoration: "none", fontWeight: 800, fontSize: "1.25rem" }}
          className="gradient-text"
        >
          {site.name}
        </Link>

        <nav className="desktop-nav" style={{ display: "flex", gap: 4, marginInlineStart: 12 }}>
          {t.nav.map((item) => (
            <Link
              key={item.href}
              href={localePath(locale, item.href)}
              style={{
                padding: "7px 12px", borderRadius: 999, textDecoration: "none",
                fontSize: ".88rem", fontWeight: 500,
                color: bare === item.href ? "var(--color-brand-600)" : "var(--text-2)",
                background: bare === item.href ? "var(--eyebrow-bg)" : "transparent",
              }}
            >
              {item.label}
            </Link>
          ))}
        </nav>

        <div style={{ marginInlineStart: "auto", display: "flex", gap: 8, alignItems: "center" }}>
          <LocaleToggle locale={locale} />
          <ThemeToggle />
          <a href={site.panelUrl} className="btn btn-ghost desktop-only">
            {locale === "fa" ? "ورود" : "Log in"}
          </a>
          <a href={`${site.panelUrl}/register`} className="btn btn-primary">
            {t.cta.startFree}
          </a>
          <button
            className="mobile-only btn btn-ghost"
            style={{ padding: "8px 12px" }}
            onClick={() => setOpen((v) => !v)}
            aria-label={locale === "fa" ? "منو" : "Menu"}
            aria-expanded={open}
          >
            ☰
          </button>
        </div>
      </div>

      {open && (
        <div className="wrap mobile-only" style={{ paddingBottom: 16 }}>
          <div style={{ display: "grid", gap: 4 }}>
            {t.nav.map((item) => (
              <Link
                key={item.href}
                href={localePath(locale, item.href)}
                onClick={() => setOpen(false)}
                style={{
                  padding: "10px 14px", borderRadius: 12, textDecoration: "none",
                  color: "var(--text-2)", background: "var(--bg-soft)",
                }}
              >
                {item.label}
              </Link>
            ))}
          </div>
        </div>
      )}

      <style>{`
        .mobile-only { display: none; }
        @media (max-width: 1020px) {
          .desktop-nav, .desktop-only { display: none !important; }
          .mobile-only { display: inline-flex; }
        }
      `}</style>
    </header>
  );
}
