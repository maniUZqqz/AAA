import type { Metadata } from "next";

import JsonLd from "@/components/JsonLd";
import SectionHead from "@/components/SectionHead";
import { breadcrumbs, faqPage, offers } from "@/lib/seo";
import { TEAM_COST, faq, site, trust } from "@/lib/content";
import { fa, getPlans, toman } from "@/lib/plans";

export const metadata: Metadata = {
  title: "قیمت‌ها",
  description:
    "پلن‌های ماهانه آپ‌مارکت با سهمیه‌ی شفاف ویدیو، تصویر و کپشن. " +
    "دو هفته رایگان، بدون کارت بانکی.",
  alternates: { canonical: "/pricing" },
};

// prices are read from the running backend; five minutes is fresh enough for
// a marketing page and keeps the site up if the API blips
export const revalidate = 300;

export default async function Pricing() {
  const { plans, live } = await getPlans();
  const paid = plans.filter((p) => !p.is_trial);

  return (
    <>
      <JsonLd
        data={[
          breadcrumbs([{ name: "قیمت‌ها", path: "/pricing" }]),
          offers(paid),
          faqPage(faq.slice(6, 9)),
        ]}
      />

      <section className="mesh">
        <div className="wrap">
          <SectionHead
            eyebrow="قیمت‌گذاری"
            title="سهمیه‌ی شفاف، بدون هزینه‌ی پنهان"
            lead="هر پلن مقدار مشخصی ویدیو، تصویر و کپشن در ماه دارد. مصرفتان را زنده می‌بینید."
          />

          <div className="grid g3" style={{ marginTop: 48, alignItems: "start" }}>
            {paid.map((plan) => {
              const featured = plan.slug === "pro";
              const saving = TEAM_COST - plan.price_toman;
              return (
                <div
                  key={plan.slug}
                  id={plan.slug}
                  className={`card card-hover plan ${featured ? "plan-featured" : ""}`}
                >
                  {featured && <span className="eyebrow plan-tag">پیشنهاد ما</span>}

                  <h3 style={{ fontSize: "1.25rem" }}>{plan.name}</h3>

                  <div className="plan-price">
                    <span className={`v num ${featured ? "gradient-text" : ""}`}>
                      {toman(plan.price_toman)}
                    </span>
                    <span className="muted">تومان / ماه</span>
                  </div>

                  <ul className="checks mt-md">
                    <Item>{fa(plan.video_seconds)} ثانیه ویدیوی تبلیغاتی با صداگذاری</Item>
                    <Item>{fa(plan.images)} تصویر — پوستر، عکس اینستاگرامی یا بهبود</Item>
                    <Item>{fa(plan.captions)} کپشن با هشتگ و فراخوان به اقدام</Item>
                    <Item>تحلیل محصول و رقبا</Item>
                    {plan.allows_sales_agent && <Item>پشتیبان فروش ۲۴ ساعته</Item>}
                    {plan.allows_publishing && <Item>انتشار مستقیم در اینستاگرام</Item>}
                    <Item>
                      {plan.max_products === 0
                        ? "تعداد محصول نامحدود"
                        : `تا ${fa(plan.max_products)} محصول`}
                    </Item>
                  </ul>

                  <a
                    href={`${site.panelUrl}/register?plan=${plan.slug}`}
                    className={featured ? "btn btn-primary" : "btn btn-ghost"}
                    style={{ marginTop: 24, width: "100%", justifyContent: "center" }}
                  >
                    شروع رایگان
                  </a>

                  <p className="muted center mt">
                    {toman(saving)} تومان ارزان‌تر از تیم داخلی
                  </p>
                </div>
              );
            })}
          </div>

          <p className="muted center mt-md">
            همه‌ی پلن‌ها با <b style={{ color: "var(--text-2)" }}>دو هفته رایگان</b> شروع می‌شوند —
            بدون کارت بانکی و بدون تمدید خودکار.
            {!live && " (قیمت‌ها از نسخه‌ی ذخیره‌شده — برای عدد دقیق تماس بگیرید.)"}
          </p>
        </div>
      </section>

      {/* --------------------------------------------- plan side by side */}
      <section className="section-soft">
        <div className="wrap">
          <SectionHead eyebrow="مقایسه‌ی پلن‌ها" title="چه چیزی در کدام پلن هست" />
          <div className="card mt-lg" style={{ overflowX: "auto" }}>
            <table className="cmp">
              <thead>
                <tr>
                  <Th>سهمیه‌ی ماهانه</Th>
                  {paid.map((p) => (
                    <Th key={p.slug} highlight={p.slug === "pro"}>{p.name}</Th>
                  ))}
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td className="label">ثانیه ویدیو</td>
                  {paid.map((p) => (
                    <td key={p.slug} className={p.slug === "pro" ? "win" : ""}>
                      {fa(p.video_seconds)}
                    </td>
                  ))}
                </tr>
                <tr>
                  <td className="label">تصویر</td>
                  {paid.map((p) => (
                    <td key={p.slug} className={p.slug === "pro" ? "win" : ""}>
                      {fa(p.images)}
                    </td>
                  ))}
                </tr>
                <tr>
                  <td className="label">کپشن</td>
                  {paid.map((p) => (
                    <td key={p.slug} className={p.slug === "pro" ? "win" : ""}>
                      {fa(p.captions)}
                    </td>
                  ))}
                </tr>
                <tr>
                  <td className="label">تعداد محصول</td>
                  {paid.map((p) => (
                    <td key={p.slug} className={p.slug === "pro" ? "win" : ""}>
                      {p.max_products === 0 ? "نامحدود" : fa(p.max_products)}
                    </td>
                  ))}
                </tr>
                <tr>
                  <td className="label">پشتیبان فروش</td>
                  {paid.map((p) => (
                    <td key={p.slug}>{p.allows_sales_agent ? "✔" : "—"}</td>
                  ))}
                </tr>
                <tr>
                  <td className="label">انتشار خودکار</td>
                  {paid.map((p) => (
                    <td key={p.slug}>{p.allows_publishing ? "✔" : "—"}</td>
                  ))}
                </tr>
                <tr>
                  <td className="label">تحلیل محصول و رقبا</td>
                  {paid.map((p) => (
                    <td key={p.slug}>✔</td>
                  ))}
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* ------------------------------------------------------ comparison */}
      <section>
        <div className="wrap">
          <SectionHead
            eyebrow="مقایسه"
            title="در برابر ساختن یک تیم"
            lead={`هزینه‌ی حداقلی یک تیم بازاریابی: ${toman(TEAM_COST)} تومان در ماه.`}
          />
          <div className="card mt-lg" style={{ overflowX: "auto" }}>
            <table className="cmp">
              <thead>
                <tr>
                  <Th>مورد</Th>
                  <Th>تیم داخلی</Th>
                  <Th>آژانس</Th>
                  <Th highlight>آپ‌مارکت</Th>
                </tr>
              </thead>
              <tbody>
                <Row label="هزینه ماهانه" a={`${toman(TEAM_COST)}+`} b="نامشخص" c={`از ${toman(paid[0]?.price_toman ?? 0)}`} />
                <Row label="زمان تا اولین خروجی" a="هفته‌ها" b="روزها" c="چند دقیقه" />
                <Row label="تخصص لازم شما" a="مدیریت تیم" b="مدیریت قرارداد" c="هیچ" />
                <Row label="کنترل روی خروجی" a="کامل" b="کم" c="کامل — تأیید با شما" />
                <Row label="پشتیبانی فروش" a="ادمین جدا" b="معمولاً نه" c="شامل است" />
                <Row label="تحلیل رقبا" a="دستی" b="گاهی" c="خودکار از وب" />
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* ----------------------------------------------------------- trust */}
      <section className="section-soft">
        <div className="wrap">
          <div className="grid g4">
            {trust.map((t) => (
              <div key={t.title} className="card">
                <div className="icon-lg">{t.icon}</div>
                <h3 className="mt-sm">{t.title}</h3>
                <p className="muted mt-sm">{t.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ------------------------------------------------------------- faq */}
      <section className="section-soft">
        <div className="wrap w-md">
          <SectionHead title="سؤالات مربوط به قیمت" />
          <div className="stack-sm mt-md">
            {faq.slice(6, 9).map((f) => (
              <details key={f.q} className="card qa">
                <summary>{f.q}</summary>
                <p>{f.a}</p>
              </details>
            ))}
          </div>
        </div>
      </section>

      <section>
        <div className="wrap">
          <div className="cta-band">
            <h2>با دوره‌ی رایگان شروع کنید</h2>
            <p className="lead mt narrower">
              دو هفته، بدون کارت بانکی، بدون تمدید خودکار. اگر نتیجه نگرفتید
              هیچ هزینه‌ای نمی‌پردازید.
            </p>
            <div className="row mt-md center-row">
              <a href={`${site.panelUrl}/register`} className="btn btn-primary">
                شروع رایگان ←
              </a>
            </div>
          </div>
        </div>
      </section>
    </>
  );
}

function Item({ children }: { children: React.ReactNode }) {
  return <li>{children}</li>;
}

function Th({ children, highlight }: { children: React.ReactNode; highlight?: boolean }) {
  return <th className={highlight ? "win" : ""}>{children}</th>;
}

function Row({ label, a, b, c }: { label: string; a: string; b: string; c: string }) {
  return (
    <tr>
      <td className="label">{label}</td>
      <td>{a}</td>
      <td>{b}</td>
      <td className="win">{c}</td>
    </tr>
  );
}
