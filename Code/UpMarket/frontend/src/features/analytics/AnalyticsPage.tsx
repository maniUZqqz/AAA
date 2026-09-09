import { useCallback, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { api, errorMessage } from "../../api/client";
import { Card, ErrorBox, SectionTitle, Spinner } from "../../components/ui";

// Categorical palette — validated with the dataviz six-checks script on #fff
// (lightness band, chroma, CVD ΔE 12.5, normal-vision ΔE 24.3, contrast ≥3:1).
const SERIES = [
  { key: "conversations", label: "گفتگوها", color: "#7C3AED" },
  { key: "orders", label: "سفارش‌ها", color: "#0D9488" },
  { key: "ai_requests", label: "درخواست‌های AI", color: "#D97706" },
] as const;

interface Overview {
  products: { total: number; available: number };
  conversations: { total: number; by_state: Record<string, number>; messages: number };
  orders: {
    total: number;
    by_status: Record<string, number>;
    confirmed_revenue: string;
    draft_value: string;
  };
  campaigns: { total: number; by_state: Record<string, number> };
  publishing: { total: number; by_status: Record<string, number> };
  content: { generated_images: number; captions: number; videos_ready: number };
  ai: { requests: number; by_status: Record<string, number>; avg_latency_ms: number };
  jobs: { total: number; by_state: Record<string, number> };
}

interface DayPoint {
  date: string;
  conversations: number;
  orders: number;
  ai_requests: number;
}

function StatTile({ label, value, hint }: { label: string; value: string; hint?: string }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4">
      <p className="text-xs text-slate-500">{label}</p>
      <p className="mt-1 text-2xl font-extrabold text-slate-800" dir="ltr">
        {value}
      </p>
      {hint && <p className="mt-1 text-xs text-slate-400">{hint}</p>}
    </div>
  );
}

function MiniBarChart({
  title,
  color,
  points,
  seriesKey,
}: {
  title: string;
  color: string;
  points: DayPoint[];
  seriesKey: (typeof SERIES)[number]["key"];
}) {
  const [hover, setHover] = useState<number | null>(null);
  const values = points.map((p) => p[seriesKey]);
  const max = Math.max(...values, 1);
  const maxIndex = values.indexOf(Math.max(...values));

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4">
      <div className="mb-2 flex items-center gap-2">
        <span className="inline-block h-3 w-3 rounded-sm" style={{ background: color }} />
        <span className="text-sm font-bold text-slate-700">{title}</span>
        <span className="mr-auto text-xs text-slate-400">۱۴ روز اخیر</span>
      </div>
      <div className="relative flex h-28 items-end gap-[2px] border-b border-slate-200 pb-px">
        {points.map((point, i) => {
          const value = point[seriesKey];
          const height = value === 0 ? 2 : Math.max(4, (value / max) * 100);
          return (
            <div
              key={point.date}
              className="group relative flex h-full flex-1 items-end justify-center"
              onMouseEnter={() => setHover(i)}
              onMouseLeave={() => setHover(null)}
            >
              <div
                className="w-full max-w-[14px] rounded-t-[4px]"
                style={{
                  height: `${height}%`,
                  background: value === 0 ? "#e2e8f0" : color,
                }}
              />
              {(hover === i || (hover === null && i === maxIndex && max > 0 && values[maxIndex] > 0)) && (
                <div className="pointer-events-none absolute bottom-full mb-1 whitespace-nowrap rounded bg-slate-800 px-2 py-0.5 text-[10px] text-white">
                  {new Date(point.date).toLocaleDateString("fa-IR", {
                    month: "short",
                    day: "numeric",
                  })}
                  : {value.toLocaleString("fa-IR")}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default function AnalyticsPage() {
  const { id: storeId } = useParams<{ id: string }>();
  const [overview, setOverview] = useState<Overview | null>(null);
  const [series, setSeries] = useState<DayPoint[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [showTable, setShowTable] = useState(false);

  const load = useCallback(async () => {
    try {
      const [overviewRes, seriesRes] = await Promise.all([
        api.get<Overview>(`/stores/${storeId}/analytics/`),
        api.get<{ series: DayPoint[] }>(`/stores/${storeId}/analytics/timeseries/?days=14`),
      ]);
      setOverview(overviewRes.data);
      setSeries(seriesRes.data.series);
    } catch (err) {
      setError(errorMessage(err));
    }
  }, [storeId]);

  useEffect(() => {
    void load();
  }, [load]);

  if (!overview) {
    return (
      <div className="py-10 text-center">{error ? <ErrorBox message={error} /> : <Spinner />}</div>
    );
  }

  const fa = (n: number) => n.toLocaleString("fa-IR");

  return (
    <div className="space-y-6">
      <div>
        <Link to={`/stores/${storeId}`} className="text-sm text-violet-600 hover:underline">
          ← بازگشت به فروشگاه
        </Link>
        <h1 className="mt-1 text-2xl font-extrabold text-slate-800">📈 آمار فروشگاه</h1>
        <p className="text-xs text-slate-400">همه اعداد مستقیم از داده‌های واقعی دیتابیس.</p>
      </div>
      <ErrorBox message={error} />

      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <StatTile
          label="محصولات"
          value={fa(overview.products.total)}
          hint={`${fa(overview.products.available)} موجود`}
        />
        <StatTile
          label="گفتگوهای فروش"
          value={fa(overview.conversations.total)}
          hint={`${fa(overview.conversations.messages)} پیام`}
        />
        <StatTile
          label="سفارش‌ها"
          value={fa(overview.orders.total)}
          hint={`درآمد تأییدشده: ${Number(overview.orders.confirmed_revenue).toLocaleString("fa-IR")} تومان`}
        />
        <StatTile
          label="کمپین‌ها"
          value={fa(overview.campaigns.total)}
          hint={`${fa(overview.campaigns.by_state["PUBLISHED"] ?? 0)} منتشرشده`}
        />
        <StatTile
          label="تصاویر تولیدی"
          value={fa(overview.content.generated_images)}
        />
        <StatTile
          label="کپشن‌ها / ویدیوها"
          value={`${fa(overview.content.captions)} / ${fa(overview.content.videos_ready)}`}
          hint="کپشن / ویدیوی آماده"
        />
        <StatTile
          label="درخواست‌های AI"
          value={fa(overview.ai.requests)}
          hint={`میانگین تأخیر: ${fa(overview.ai.avg_latency_ms)}ms · خطا: ${fa(
            overview.ai.requests - (overview.ai.by_status["OK"] ?? 0),
          )}`}
        />
        <StatTile
          label="Jobها"
          value={fa(overview.jobs.total)}
          hint={`موفق: ${fa(overview.jobs.by_state["COMPLETED"] ?? 0)} · ناموفق: ${fa(
            overview.jobs.by_state["FAILED"] ?? 0,
          )}`}
        />
      </div>

      <Card>
        <div className="mb-3 flex items-center justify-between">
          <SectionTitle>روند ۱۴ روز اخیر</SectionTitle>
          <button
            onClick={() => setShowTable((v) => !v)}
            className="text-sm text-violet-600 hover:underline"
          >
            {showTable ? "نمایش نمودار" : "نمایش جدول"}
          </button>
        </div>
        {showTable ? (
          <div className="overflow-x-auto">
            <table className="w-full min-w-[420px] text-right text-sm">
              <thead>
                <tr className="border-b border-slate-200 text-xs text-slate-500">
                  <th className="py-2">تاریخ</th>
                  {SERIES.map((s) => (
                    <th key={s.key}>{s.label}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {series.map((point) => (
                  <tr key={point.date} className="border-b border-slate-100">
                    <td className="py-1.5 text-xs text-slate-500">
                      {new Date(point.date).toLocaleDateString("fa-IR")}
                    </td>
                    {SERIES.map((s) => (
                      <td key={s.key}>{point[s.key].toLocaleString("fa-IR")}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="grid gap-4 lg:grid-cols-3">
            {SERIES.map((s) => (
              <MiniBarChart
                key={s.key}
                title={s.label}
                color={s.color}
                points={series}
                seriesKey={s.key}
              />
            ))}
          </div>
        )}
      </Card>
    </div>
  );
}
