import Link from "next/link";

import works from "@/content/showcase/works.json";
import JsonLd from "@/components/JsonLd";
import SectionHead from "@/components/SectionHead";
import { notFound } from "next/navigation";

import { TEAM_COST, contentFor, siteFor } from "@/lib/content";
import { dict } from "@/lib/dict";
import { alternatesFor, isLocale, localePath, LOCALES, type Locale } from "@/lib/i18n";
import { getPlans, money, num } from "@/lib/plans";
import { faqPage, howTo } from "@/lib/seo";
import { HOME } from "./copy";

type Props = { params: Promise<{ locale: string }> };

export function generateStaticParams() {
  return LOCALES.map((locale) => ({ locale }));
}

export async function generateMetadata({ params }: Props) {
  const { locale } = await params;
  if (!isLocale(locale)) return {};
  return { alternates: alternatesFor(locale, "/") };
}

type Work = {
  id: string;
  category: string;
  product: string;
  image: string;
  videos: string[];
  caption: string;
};

export default async function Home({ params }: Props) {
  const { locale } = await params;
  if (!isLocale(locale)) notFound();
  const l = locale as Locale;
  const c = HOME[l];
  const t = dict(l);
  const site = siteFor(l);
  const {
    alternatives, audiences, capabilities, faq, features, objections, roles, steps, trust,
  } = contentFor(l);
  const fa = (v: number | string) => num(v, l);
  const toman = (v: number) => money(v, l);

  const { plans } = await getPlans();
  const headline = plans.find((p) => p.slug === "pro") ?? plans[1] ?? plans[0];
  const saving = TEAM_COST - (headline?.price_toman ?? 0);

  // the decor sample is the only one with all three outputs, which makes it
  // the honest choice for the "one product, three outputs" section
  const sample = (works as Work[]).find((w) => w.videos.length > 0) ?? (works as Work[])[0];

  return (
    <>
      <JsonLd data={[howTo(steps), faqPage(faq.slice(0, 4))]} />

      {/* ---------------------------------------------------------- hero */}
      <section className="mesh">
        <div className="wrap hero-grid">
          <div className="reveal">
            <span className="eyebrow">{c.ctaNote}</span>
            <h1 className="mt">
              {c.heroTitle} <span className="gradient-text">{c.heroTitleAccent}</span>
            </h1>
            <p className="lead mt">
              {site.oneLiner} بدون گرافیست، بدون تدوینگر، بدون کپی‌رایتر.
            </p>
            <div className="row mt-md">
              <a href={`${site.panelUrl}/register`} className="btn btn-primary">
                {t.cta.startFree}
              </a>
              <Link href={localePath(l, "/showcase")} className="btn btn-ghost">
                نمونه‌کارهای بیشتر
              </Link>
            </div>
            <div className="pill-row mt-md" style={{ justifyContent: "flex-start" }}>
              <span className="pill">🎨 پوستر</span>
              <span className="pill">🎬 ویدیو</span>
              <span className="pill">✍️ کپشن</span>
              <span className="pill">🤝 پشتیبان فروش</span>
            </div>
          </div>

          <div className="hero-art reveal reveal-1">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src="/showcase/apparel.png"
              alt={c.posterAltFull}
              width={1024}
              height={1024}
              fetchPriority="high"
            />
            <div className="hero-float hero-float-1">
              <span>🎨</span> از عکس واقعی محصول
            </div>
            <div className="hero-float hero-float-2">
              <span>🖼️</span> {c.heroBadge}
            </div>
          </div>
        </div>
      </section>

      {/* -------------------------------------------------- capability band */}
      <div className="band">
        <div className="wrap band-grid">
          {capabilities.map((c) => (
            <div key={c.label} className="band-item">
              <div className="v gradient-text">{c.value}</div>
              <div className="l">{c.label}</div>
              <div className="l" style={{ fontSize: ".72rem", opacity: 0.75 }}>
                {c.hint}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* ------------------------------------------------------- problem */}
      <section>
        <div className="wrap">
          <SectionHead
            eyebrow={c.problemEyebrow}
            title={c.problemTitle}
            lead={c.problemLead}
          />
          <div className="grid g3 mt-lg">
            {roles.map((r) => (
              <article key={r.role} className="card">
                <div className="icon-lg">{r.icon}</div>
                <h3 className="mt-sm">{r.role}</h3>
                <p className="muted">{r.task}</p>
              </article>
            ))}
          </div>

          <div className="vs-grid mt-lg">
            <div className="card vs-card bad">
              <h3>{alternatives.left.title}</h3>
              <ul className="vs-list no">
                {alternatives.left.items.map((i) => (
                  <li key={i}>{i}</li>
                ))}
              </ul>
            </div>
            <div className="vs-mid">{c.vsEyebrow}</div>
            <div className="card vs-card good">
              <h3>{alternatives.right.title}</h3>
              <ul className="vs-list yes">
                {alternatives.right.items.map((i) => (
                  <li key={i}>{i}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* -------------------------------------------- one product, three outputs */}
      {sample && (
        <section className="section-soft">
          <div className="wrap">
            <SectionHead
              eyebrow={c.oneProduct}
              title={c.fromOnePhoto(sample.product)}
              lead={c.heroLead}
            />

            <div className="triptych mt-lg">
              <div className="card">
                <div className="out-head">
                  {c.outHeads.poster}
                </div>
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  className="shot"
                  src={sample.image}
                  alt={c.posterAlt(sample.product)}
                  width={1024}
                  height={1024}
                  loading="lazy"
                />
              </div>

              <div className="card">
                <div className="out-head">
                  {c.outHeads.video} — {fa(sample.videos.length)}
                </div>
                <div className="vid-grid">
                  {sample.videos.slice(0, 5).map((v, i) => (
                    <video
                      key={v}
                      src={v}
                      muted
                      loop
                      playsInline
                      autoPlay
                      preload="metadata"
                      aria-label={`${c.segment(fa(i + 1))} — ${sample.product}`}
                    />
                  ))}
                </div>
              </div>

              <div className="card">
                <div className="out-head">
                  <span>✍️</span> کپشن
                </div>
                <div className="caption-box">{sample.caption}</div>
              </div>
            </div>

            <div className="center mt-md">
              <Link href={localePath(l, "/showcase")} className="btn btn-ghost">
                نمونه‌کارهای بیشتر ←
              </Link>
            </div>
          </div>
        </section>
      )}

      {/* ------------------------------------------------------ features */}
      <section>
        <div className="wrap">
          <SectionHead
            eyebrow={c.solutionEyebrow}
            title={c.solutionTitle}
            lead={c.solutionLead}
          />
          <div className="bento mt-lg">
            {features.map((f, i) => (
              <Link
                key={f.id}
                href={`${localePath(l, "/features")}#${f.id}`}
                className={`card card-hover plain ${i < 2 ? "wide" : ""}`}
              >
                <div className="icon-lg">{f.icon}</div>
                <h3 className="mt-sm">{f.title}</h3>
                <p className="muted mt-sm">{f.lead}</p>
                {i < 2 && (
                  <ul className="checks mt">
                    {f.bullets.slice(0, 3).map((b) => (
                      <li key={b}>{b}</li>
                    ))}
                  </ul>
                )}
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* ---------------------------------------------------------- flow */}
      <section className="section-soft">
        <div className="wrap narrow">
          <SectionHead eyebrow={c.processEyebrow} title={c.processTitle} lead={c.processLead} />
          <div className="timeline mt-lg">
            {steps.map((s) => (
              <div key={s.n} className="tl-item">
                <div className="tl-dot">{s.icon}</div>
                <div className="tl-body">
                  <div className="row-tight">
                    <span className="eyebrow">{c.step} {s.n}</span>
                  </div>
                  <h3 className="mt-sm">{s.title}</h3>
                  <p className="muted mt-sm">{s.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ------------------------------------------------------ audiences */}
      <section>
        <div className="wrap">
          <SectionHead
            eyebrow={c.audienceEyebrow}
            title={c.audienceTitle}
            lead={c.audienceLead}
          />
          <div className="pill-row mt-lg">
            {audiences.map((a) => (
              <span key={a.label} className={`pill ${a.proven ? "on" : ""}`}>
                <span>{a.icon}</span> {a.label}
                {a.proven && <span style={{ fontSize: ".7rem" }}>{c.proven}</span>}
              </span>
            ))}
          </div>
        </div>
      </section>

      {/* ----------------------------------------------------- objections */}
      <section className="section-soft">
        <div className="wrap">
          <SectionHead eyebrow={c.objectionsEyebrow} title={c.objectionsTitle} />
          <div className="grid g4 mt-lg">
            {objections.map((o) => (
              <article key={o.q} className="card">
                <div className="icon-lg">{o.icon}</div>
                <h3 className="mt-sm" style={{ fontSize: "1rem" }}>
                  {o.q}
                </h3>
                <p className="muted mt-sm">{o.a}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      {/* --------------------------------------------------------- trust */}
      <section>
        <div className="wrap">
          <SectionHead eyebrow={c.trustEyebrow} title={c.trustTitle} />
          <div className="grid g4 mt-lg">
            {trust.map((t) => (
              <article key={t.title} className="card">
                <div className="icon-lg">{t.icon}</div>
                <h3 className="mt-sm">{t.title}</h3>
                <p className="muted mt-sm">{t.desc}</p>
              </article>
            ))}
          </div>

          <div className="grid g3 mt-lg">
            <Stat
              value={toman(saving)}
              label={c.savingLabel}
              note={c.vsTitle}
            />
            <Stat value={c.firstOutputValue} label={c.firstOutputLabel} note={c.firstOutputNote} />
            <Stat value={t.cta.free} label="" note={c.ctaNote} />
          </div>
        </div>
      </section>

      {/* ----------------------------------------------------------- cta */}
      <section className="section-soft">
        <div className="wrap">
          <div className="cta-band">
            <h2>{c.ctaTitle}</h2>
            <p className="lead mt narrower">
{c.ctaLead}
            </p>
            <div className="row mt-md center-row">
              <a href={`${site.panelUrl}/register`} className="btn btn-primary">
                {t.cta.startFree}
              </a>
              <Link href={localePath(l, "/pricing")} className="btn btn-ghost">
                {c.seePricing}
              </Link>
            </div>
          </div>
        </div>
      </section>
    </>
  );
}

function Stat({ value, label, note }: { value: string; label: string; note?: string }) {
  return (
    <div className="card stat">
      <div className="v gradient-text num">{value}</div>
      <div className="l">{label}</div>
      {note && <div className="n">{note}</div>}
    </div>
  );
}
