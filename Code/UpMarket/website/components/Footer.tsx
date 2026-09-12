import Link from "next/link";

import { siteFor } from "@/lib/content";
import { dict } from "@/lib/dict";
import { localePath, type Locale } from "@/lib/i18n";

const linkStyle = {
  color: "var(--text-2)",
  textDecoration: "none",
  fontSize: ".88rem",
} as const;

const colTitle = { fontSize: ".9rem", marginBottom: 12 } as const;
const list = { listStyle: "none", padding: 0, display: "grid", gap: 8 } as const;

export default function Footer({ locale }: { locale: Locale }) {
  const site = siteFor(locale);
  const t = dict(locale);

  return (
    <footer style={{ borderTop: "1px solid var(--line)", background: "var(--bg-soft)" }}>
      <div className="wrap" style={{ paddingBlock: 48 }}>
        <div className="grid g4">
          <div>
            <div className="gradient-text" style={{ fontWeight: 800, fontSize: "1.3rem" }}>
              {site.name}
            </div>
            <p className="muted" style={{ marginTop: 8, lineHeight: 1.9 }}>
              {site.tagline}
            </p>
            <a
              href={`${site.panelUrl}/register`}
              className="btn btn-primary"
              style={{ marginTop: 16 }}
            >
              {t.cta.free}
            </a>
          </div>

          {t.footer.map((col) => (
            <div key={col.title}>
              <h3 style={colTitle}>{col.title}</h3>
              <ul style={list}>
                {col.links.map((i) => (
                  <li key={i.href}>
                    <Link href={localePath(locale, i.href)} style={linkStyle}>
                      {i.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <div
          style={{
            marginTop: 40,
            paddingTop: 24,
            borderTop: "1px solid var(--line)",
            display: "flex",
            flexWrap: "wrap",
            gap: 12,
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <span className="muted">
            © {new Date().getFullYear()} {site.name} — {t.common.rights}
          </span>

          {/* Legal links belong in the footer on every page — that is where
              people look for them, and where a reviewer expects them. */}
          <nav style={{ display: "flex", flexWrap: "wrap", gap: 16 }}>
            {t.legal.map((i) => (
              <Link key={i.href} href={localePath(locale, i.href)} style={linkStyle}>
                {i.label}
              </Link>
            ))}
          </nav>

          <a href={`mailto:${site.email}`} className="muted" style={{ textDecoration: "none" }}>
            {site.email}
          </a>
        </div>
      </div>
    </footer>
  );
}
