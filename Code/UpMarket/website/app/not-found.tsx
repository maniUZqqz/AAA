import Link from "next/link";

import { nav } from "@/lib/content";

export default function NotFound() {
  return (
    <section>
      <div className="wrap narrow center">
        <div style={{ fontSize: "4rem" }}>🧭</div>
        <h1 className="mt">این صفحه پیدا نشد</h1>
        <p className="lead mt">
          شاید نشانی عوض شده باشد. از این‌ها امتحان کنید:
        </p>

        <div className="row mt-md center-row">
          {nav.map((item) => (
            <Link key={item.href} href={item.href} className="tag-link">
              {item.label}
            </Link>
          ))}
        </div>

        <div className="mt-md">
          <Link href="/" className="btn btn-primary">بازگشت به صفحه‌ی اصلی</Link>
        </div>
      </div>
    </section>
  );
}
