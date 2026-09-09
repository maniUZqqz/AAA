import type { Metadata } from "next";

import SectionHead from "@/components/SectionHead";
import { site } from "@/lib/content";

export const metadata: Metadata = {
  title: "تماس با ما",
  description: "راه‌های ارتباط با تیم آپ‌مارکت.",
  alternates: { canonical: "/contact" },
};

export default function Contact() {
  return (
    <section>
      <div className="wrap" style={{ maxWidth: 720 }}>
        <SectionHead
          eyebrow="تماس"
          title="با ما حرف بزنید"
          lead="سؤال، پیشنهاد، یا می‌خواهید محصولتان را قبل از ثبت‌نام ببینیم؟"
        />

        <div className="grid g2 mt-lg">
          <a
            href={`mailto:${site.email}`}
            className="card card-hover plain"
          >
            <div className="icon-lg">✉️</div>
            <h3 className="mt-sm">ایمیل</h3>
            <p className="muted mt-sm">{site.email}</p>
          </a>

          <a
            href={site.instagram}
            target="_blank"
            rel="noopener noreferrer"
            className="card card-hover plain"
          >
            <div className="icon-lg">📷</div>
            <h3 className="mt-sm">اینستاگرام</h3>
            <p className="muted mt-sm">نمونه‌کارهای روزانه</p>
          </a>
        </div>

        <div className="card" style={{ marginTop: 24, textAlign: "center" }}>
          <h3>سریع‌ترین راه</h3>
          <p className="muted mt-sm">
            حساب رایگان بسازید و اولین بسته‌ی محتوا را همین امروز ببینید —
            بدون کارت بانکی و بدون تماس فروش.
          </p>
          <a href={`${site.panelUrl}/register`} className="btn btn-primary" style={{ marginTop: 18 }}>
            شروع رایگان →
          </a>
        </div>
      </div>
    </section>
  );
}
