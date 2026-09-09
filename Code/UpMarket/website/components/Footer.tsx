import Link from "next/link";

import { nav, site } from "@/lib/content";

export default function Footer() {
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
          </div>

          <div>
            <h3 style={{ fontSize: ".9rem", marginBottom: 12 }}>محصول</h3>
            <ul style={{ listStyle: "none", padding: 0, display: "grid", gap: 8 }}>
              {nav.slice(0, 4).map((i) => (
                <li key={i.href}>
                  <Link href={i.href} style={{ color: "var(--text-2)", textDecoration: "none", fontSize: ".88rem" }}>
                    {i.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <h3 style={{ fontSize: ".9rem", marginBottom: 12 }}>شرکت</h3>
            <ul style={{ listStyle: "none", padding: 0, display: "grid", gap: 8 }}>
              {nav.slice(4).map((i) => (
                <li key={i.href}>
                  <Link href={i.href} style={{ color: "var(--text-2)", textDecoration: "none", fontSize: ".88rem" }}>
                    {i.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <h3 style={{ fontSize: ".9rem", marginBottom: 12 }}>شروع کنید</h3>
            <p className="muted" style={{ marginBottom: 12 }}>
              دو هفته رایگان، بدون کارت بانکی.
            </p>
            <a href={`${site.panelUrl}/register`} className="btn btn-primary">
              ساخت حساب
            </a>
          </div>
        </div>

        <div
          style={{
            marginTop: 40, paddingTop: 24, borderTop: "1px solid var(--line)",
            display: "flex", flexWrap: "wrap", gap: 12, justifyContent: "space-between",
          }}
        >
          <span className="muted">
            © {new Date().getFullYear()} {site.name} — همه حقوق محفوظ است.
          </span>
          <a href={`mailto:${site.email}`} className="muted" style={{ textDecoration: "none" }}>
            {site.email}
          </a>
        </div>
      </div>
    </footer>
  );
}
