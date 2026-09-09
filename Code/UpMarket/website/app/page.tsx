import Link from "next/link";

import works from "@/content/showcase/works.json";
import JsonLd from "@/components/JsonLd";
import SectionHead from "@/components/SectionHead";
import {
  TEAM_COST,
  alternatives,
  audiences,
  capabilities,
  faq,
  features,
  objections,
  roles,
  site,
  steps,
  trust,
} from "@/lib/content";
import { fa, getPlans, toman } from "@/lib/plans";
import { faqPage, howTo } from "@/lib/seo";

type Work = {
  id: string;
  category: string;
  product: string;
  image: string;
  videos: string[];
  caption: string;
};

export default async function Home() {
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
            <span className="eyebrow">دو هفته رایگان، بدون کارت بانکی</span>
            <h1 className="mt">
              بازاریابی فروشگاه شما، <span className="gradient-text">خودکار</span>
            </h1>
            <p className="lead mt">
              {site.oneLiner} بدون گرافیست، بدون تدوینگر، بدون کپی‌رایتر.
            </p>
            <div className="row mt-md">
              <a href={`${site.panelUrl}/register`} className="btn btn-primary">
                شروع رایگان ←
              </a>
              <Link href="/showcase" className="btn btn-ghost">
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
              alt="پوستر تبلیغاتی تولیدشده با آپ‌مارکت برای یک کت اورسایز کرم"
              width={1024}
              height={1024}
              fetchPriority="high"
            />
            <div className="hero-float hero-float-1">
              <span>🎨</span> از عکس واقعی محصول
            </div>
            <div className="hero-float hero-float-2">
              <span>⏱️</span> چند دقیقه، نه چند هفته
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
            eyebrow="مشکل"
            title="برای یک صفحه‌ی حرفه‌ای، به چند نفر نیاز دارید"
            lead="و هرکدام باید استخدام، هماهنگ و پرداخت شوند."
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
            <div className="vs-mid">در برابر</div>
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
              eyebrow="یک محصول، سه خروجی"
              title={`از یک عکس ${sample.product}، یک بسته‌ی کامل`}
              lead="پوستر، ویدیوی پیوسته و کپشن — همه از یک ورودی، همه هماهنگ با هم."
            />

            <div className="triptych mt-lg">
              <div className="card">
                <div className="out-head">
                  <span>🎨</span> پوستر
                </div>
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  className="shot"
                  src={sample.image}
                  alt={`پوستر تولیدشده برای ${sample.product}`}
                  width={1024}
                  height={1024}
                  loading="lazy"
                />
              </div>

              <div className="card">
                <div className="out-head">
                  <span>🎬</span> ویدیو — {fa(sample.videos.length)} قطعه‌ی پیوسته
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
                      aria-label={`قطعه ${i + 1} از ویدیوی ${sample.product}`}
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
              <Link href="/showcase" className="btn btn-ghost">
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
            eyebrow="راه‌حل"
            title="یک پلتفرم به‌جای یک تیم"
            lead="همه‌ی مسیر، از ثبت محصول تا انتشار و پاسخ به مشتری."
          />
          <div className="bento mt-lg">
            {features.map((f, i) => (
              <Link
                key={f.id}
                href={`/features#${f.id}`}
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
          <SectionHead eyebrow="فرایند" title="چطور کار می‌کند" lead="شش قدم، یک‌بار تنظیم." />
          <div className="timeline mt-lg">
            {steps.map((s) => (
              <div key={s.n} className="tl-item">
                <div className="tl-dot">{s.icon}</div>
                <div className="tl-body">
                  <div className="row-tight">
                    <span className="eyebrow">قدم {s.n}</span>
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
            eyebrow="برای چه کسب‌وکارهایی"
            title="هر فروشگاهی که محصول فیزیکی می‌فروشد"
            lead="سه دسته‌ی اول نمونه‌ی واقعی دارند؛ بقیه همان شکل از مسئله‌اند."
          />
          <div className="pill-row mt-lg">
            {audiences.map((a) => (
              <span key={a.label} className={`pill ${a.proven ? "on" : ""}`}>
                <span>{a.icon}</span> {a.label}
                {a.proven && <span style={{ fontSize: ".7rem" }}>✓ نمونه دارد</span>}
              </span>
            ))}
          </div>
        </div>
      </section>

      {/* ----------------------------------------------------- objections */}
      <section className="section-soft">
        <div className="wrap">
          <SectionHead eyebrow="نگرانی‌های رایج" title="آنچه معمولاً می‌پرسند" />
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
          <SectionHead eyebrow="خیال راحت" title="بدون ریسک شروع کنید" />
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
              label="تومان صرفه‌جویی در ماه"
              note={`در برابر تیم ${fa(TEAM_COST / 1_000_000)} میلیونی`}
            />
            <Stat value="چند دقیقه" label="تا آماده شدن بسته‌ی محتوا" note="نه چند هفته" />
            <Stat value={`${fa(2)} هفته`} label="رایگان" note="بدون کارت بانکی" />
          </div>
        </div>
      </section>

      {/* ----------------------------------------------------------- cta */}
      <section className="section-soft">
        <div className="wrap">
          <div className="cta-band">
            <h2>همین امروز شروع کنید</h2>
            <p className="lead mt narrower">
              فروشگاه و چند محصولتان را ثبت کنید و اولین بسته‌ی محتوا را
              در همین جلسه تحویل بگیرید.
            </p>
            <div className="row mt-md center-row">
              <a href={`${site.panelUrl}/register`} className="btn btn-primary">
                شروع رایگان ←
              </a>
              <Link href="/pricing" className="btn btn-ghost">
                دیدن قیمت‌ها
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
