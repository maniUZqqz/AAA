import { useCallback, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { api, errorMessage, fetchAllPages } from "../../api/client";
import { Button, Card, Chip, EmptyState, ErrorBox, SectionTitle, Spinner } from "../../components/ui";
import { OrderInfo, OrderStatus, SalesData, TicketInfo } from "../../types";

// Same categorical palette as AnalyticsPage — validated with the dataviz
// six-checks script on #fff (CVD ΔE 12.5, normal-vision ΔE 24.3, contrast ≥3:1).
// Color follows the entity: revenue = violet, orders = teal (as in آمار).
const REVENUE_COLOR = "#7C3AED";
const ORDERS_COLOR = "#0D9488";

const STATUS_LABEL: Record<OrderStatus, string> = {
  DRAFT: "پیش‌نویس",
  AWAITING_RECEIPT: "منتظر رسید مشتری",
  AWAITING_APPROVAL: "منتظر تأیید شما",
  CONFIRMED: "تأییدشده",
  CANCELLED: "لغوشده",
};

const STATUS_STYLE: Record<OrderStatus, string> = {
  DRAFT: "bg-slate-100 text-slate-600",
  AWAITING_RECEIPT: "bg-sky-100 text-sky-800",
  AWAITING_APPROVAL: "bg-amber-100 text-amber-800",
  CONFIRMED: "bg-green-100 text-green-800",
  CANCELLED: "bg-red-100 text-red-700",
};

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

function DailyBarChart({
  title,
  color,
  caption,
  points,
}: {
  title: string;
  color: string;
  caption: string;
  points: { date: string; value: number }[];
}) {
  const [hover, setHover] = useState<number | null>(null);
  const values = points.map((p) => p.value);
  const max = Math.max(...values, 1);
  const maxIndex = values.indexOf(Math.max(...values));

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4">
      <div className="mb-2 flex items-center gap-2">
        <span className="inline-block h-3 w-3 rounded-sm" style={{ background: color }} />
        <span className="text-sm font-bold text-slate-700">{title}</span>
        <span className="mr-auto text-xs text-slate-400">{caption}</span>
      </div>
      <div className="relative flex h-28 items-end gap-[2px] border-b border-slate-200 pb-px">
        {points.map((point, i) => {
          const height = point.value === 0 ? 2 : Math.max(4, (point.value / max) * 100);
          return (
            <div
              key={point.date}
              className="group relative flex h-full flex-1 items-end justify-center"
              onMouseEnter={() => setHover(i)}
              onMouseLeave={() => setHover(null)}
            >
              <div
                className="w-full max-w-[14px] rounded-t-[4px]"
                style={{ height: `${height}%`, background: point.value === 0 ? "#e2e8f0" : color }}
              />
              {(hover === i ||
                (hover === null && i === maxIndex && values[maxIndex] > 0)) && (
                <div className="pointer-events-none absolute bottom-full mb-1 whitespace-nowrap rounded bg-slate-800 px-2 py-0.5 text-[10px] text-white">
                  {new Date(point.date).toLocaleDateString("fa-IR", {
                    month: "short",
                    day: "numeric",
                  })}
                  : {point.value.toLocaleString("fa-IR")}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default function SalesPage() {
  const { id: storeId } = useParams<{ id: string }>();
  const [sales, setSales] = useState<SalesData | null>(null);
  const [orders, setOrders] = useState<OrderInfo[]>([]);
  const [tickets, setTickets] = useState<TicketInfo[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [busyId, setBusyId] = useState<number | null>(null);
  const [showTable, setShowTable] = useState(false);
  const [showResolved, setShowResolved] = useState(false);

  const load = useCallback(async () => {
    try {
      const [salesRes, ordersList, ticketsList] = await Promise.all([
        api.get<SalesData>(`/stores/${storeId}/analytics/sales/?days=30`),
        fetchAllPages<OrderInfo>(`/stores/${storeId}/orders/`),
        fetchAllPages<TicketInfo>(`/stores/${storeId}/tickets/`),
      ]);
      setSales(salesRes.data);
      setOrders(ordersList);
      setTickets(ticketsList);
    } catch (err) {
      setError(errorMessage(err));
    }
  }, [storeId]);

  useEffect(() => {
    void load();
  }, [load]);

  const decideOrder = async (orderId: number, decision: "confirm" | "reject" | "cancel") => {
    setBusyId(orderId);
    setError(null);
    setNotice(null);
    try {
      await api.post(`/orders/${orderId}/${decision}/`);
      setNotice(
        decision === "confirm"
          ? `سفارش #${orderId} تأیید شد ✅`
          : decision === "reject"
            ? `رسید سفارش #${orderId} رد شد — مشتری باید رسید جدید بفرستد.`
            : `سفارش #${orderId} لغو شد.`,
      );
      await load();
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusyId(null);
    }
  };

  const resolveTicket = async (ticketId: number) => {
    setBusyId(ticketId);
    setError(null);
    try {
      await api.post(`/tickets/${ticketId}/resolve/`);
      await load();
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusyId(null);
    }
  };

  if (!sales) {
    return (
      <div className="py-10 text-center">{error ? <ErrorBox message={error} /> : <Spinner />}</div>
    );
  }

  const fa = (n: number) => n.toLocaleString("fa-IR");
  const toman = (v: string) => `${Number(v).toLocaleString("fa-IR")} تومان`;
  const openTickets = tickets.filter((t) => t.status !== "RESOLVED");
  const resolvedTickets = tickets.filter((t) => t.status === "RESOLVED");
  const needsAction = orders.filter((o) => o.status === "AWAITING_APPROVAL");
  const otherOrders = orders.filter((o) => o.status !== "AWAITING_APPROVAL");

  return (
    <div className="space-y-6">
      <div>
        <Link to={`/stores/${storeId}`} className="text-sm text-violet-600 hover:underline">
          ← بازگشت به فروشگاه
        </Link>
        <h1 className="mt-1 text-2xl font-extrabold text-slate-800">💰 فروش و پشتیبانی</h1>
        <p className="text-xs text-slate-400">
          سفارش‌ها را AI ثبت و رسیدها را جمع می‌کند؛ تأیید نهایی همیشه با شماست.
        </p>
      </div>
      <ErrorBox message={error} />
      {notice && (
        <div className="rounded-lg border border-green-200 bg-green-50 px-4 py-2 text-sm text-green-700">
          {notice}
        </div>
      )}

      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <StatTile
          label="درآمد تأییدشده"
          value={Number(sales.revenue.confirmed_total).toLocaleString("fa-IR")}
          hint={`${fa(sales.revenue.confirmed_orders)} سفارش تأییدشده · میانگین: ${toman(
            sales.revenue.avg_order_value,
          )}`}
        />
        <StatTile
          label="سفارش‌ها"
          value={fa(sales.orders.total)}
          hint={`تأییدشده: ${fa(sales.orders.by_status["CONFIRMED"] ?? 0)} · پیش‌نویس: ${fa(
            sales.orders.by_status["DRAFT"] ?? 0,
          )}`}
        />
        <StatTile
          label="در انتظار اقدام شما"
          value={fa(sales.pending.awaiting_approval)}
          hint={`${fa(sales.pending.receipts)} رسید در انتظار بررسی`}
        />
        <StatTile
          label="تیکت‌های باز / نرخ تبدیل"
          value={`${fa(sales.pending.open_tickets)} / ٪${sales.conversion.rate_percent.toLocaleString(
            "fa-IR",
          )}`}
          hint={`${fa(sales.conversion.conversations)} گفتگو → ${fa(sales.conversion.orders)} سفارش`}
        />
      </div>

      <Card>
        <div className="mb-3 flex items-center justify-between">
          <SectionTitle>روند ۳۰ روز اخیر</SectionTitle>
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
                  <th>سفارش‌ها</th>
                  <th>تأییدشده</th>
                  <th>درآمد (تومان)</th>
                </tr>
              </thead>
              <tbody>
                {sales.series.map((point) => (
                  <tr key={point.date} className="border-b border-slate-100">
                    <td className="py-1.5 text-xs text-slate-500">
                      {new Date(point.date).toLocaleDateString("fa-IR")}
                    </td>
                    <td>{fa(point.orders)}</td>
                    <td>{fa(point.confirmed_orders)}</td>
                    <td>{Number(point.revenue).toLocaleString("fa-IR")}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="grid gap-4 lg:grid-cols-2">
            <DailyBarChart
              title="درآمد روزانه (تومان)"
              caption="۳۰ روز اخیر"
              color={REVENUE_COLOR}
              points={sales.series.map((p) => ({ date: p.date, value: Number(p.revenue) }))}
            />
            <DailyBarChart
              title="سفارش‌های روزانه"
              caption="۳۰ روز اخیر"
              color={ORDERS_COLOR}
              points={sales.series.map((p) => ({ date: p.date, value: p.orders }))}
            />
          </div>
        )}
      </Card>

      {sales.top_products.length > 0 && (
        <Card>
          <SectionTitle>پرفروش‌ترین محصولات</SectionTitle>
          <div className="overflow-x-auto">
            <table className="w-full min-w-[360px] text-right text-sm">
              <thead>
                <tr className="border-b border-slate-200 text-xs text-slate-500">
                  <th className="py-2">محصول</th>
                  <th>تعداد فروش</th>
                  <th>درآمد</th>
                </tr>
              </thead>
              <tbody>
                {sales.top_products.map((row) => (
                  <tr key={row.name} className="border-b border-slate-100">
                    <td className="py-1.5 font-medium text-slate-700">{row.name}</td>
                    <td>{fa(row.quantity)}</td>
                    <td>{toman(row.revenue)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}

      <Card>
        <SectionTitle>
          سفارش‌ها {needsAction.length > 0 && <Chip>{fa(needsAction.length)} منتظر تأیید شما</Chip>}
        </SectionTitle>
        {orders.length === 0 ? (
          <EmptyState>هنوز سفارشی ثبت نشده — از چت فروش شروع می‌شود.</EmptyState>
        ) : (
          <div className="space-y-3">
            {[...needsAction, ...otherOrders].map((order) => (
              <div
                key={order.id}
                className={`rounded-xl border p-4 ${
                  order.status === "AWAITING_APPROVAL"
                    ? "border-amber-300 bg-amber-50/50"
                    : "border-slate-200"
                }`}
              >
                <div className="flex flex-wrap items-center gap-2">
                  <span className="font-bold text-slate-800">سفارش #{order.id}</span>
                  <span
                    className={`rounded-full px-2.5 py-0.5 text-xs ${STATUS_STYLE[order.status]}`}
                  >
                    {STATUS_LABEL[order.status]}
                  </span>
                  <span className="text-sm text-slate-500">{toman(order.total)}</span>
                  {order.customer?.name && (
                    <span className="text-xs text-slate-400">مشتری: {order.customer.name}</span>
                  )}
                  <span className="mr-auto text-xs text-slate-400">
                    {new Date(order.created_at).toLocaleString("fa-IR", {
                      month: "short",
                      day: "numeric",
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
                  </span>
                </div>
                <p className="mt-1 text-sm text-slate-600">
                  {order.items.map((it) => `${it.quantity}× ${it.product_name}`).join("، ")}
                </p>
                {(order.receipts?.length ?? 0) > 0 && (
                  <div className="mt-2 flex flex-wrap items-center gap-2">
                    {order.receipts!.map((receipt) => (
                      <a
                        key={receipt.id}
                        href={receipt.image}
                        target="_blank"
                        rel="noreferrer"
                        className="group relative"
                        title={`رسید #${receipt.id} — ${
                          receipt.status === "PENDING"
                            ? "در انتظار بررسی"
                            : receipt.status === "APPROVED"
                              ? "تأییدشده"
                              : `ردشده${receipt.review_note ? `: ${receipt.review_note}` : ""}`
                        }`}
                      >
                        <img
                          src={receipt.image}
                          alt={`رسید #${receipt.id}`}
                          className={`h-16 w-16 rounded-lg border-2 object-cover ${
                            receipt.status === "PENDING"
                              ? "border-amber-400"
                              : receipt.status === "APPROVED"
                                ? "border-green-400"
                                : "border-red-300 opacity-60"
                          }`}
                        />
                      </a>
                    ))}
                    <span className="text-xs text-slate-400">🧾 رسید(ها) — برای بزرگ‌نمایی کلیک کنید</span>
                  </div>
                )}
                {order.status !== "CONFIRMED" && order.status !== "CANCELLED" && (
                  <div className="mt-3 flex flex-wrap gap-2">
                    <Button
                      onClick={() => void decideOrder(order.id, "confirm")}
                      disabled={busyId === order.id}
                    >
                      ✅ تأیید سفارش
                    </Button>
                    {order.status === "AWAITING_APPROVAL" && (
                      <Button
                        variant="secondary"
                        onClick={() => void decideOrder(order.id, "reject")}
                        disabled={busyId === order.id}
                      >
                        ↩️ رد رسید
                      </Button>
                    )}
                    <Button
                      variant="danger"
                      onClick={() => void decideOrder(order.id, "cancel")}
                      disabled={busyId === order.id}
                    >
                      لغو
                    </Button>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </Card>

      <Card>
        <SectionTitle>
          تیکت‌های پشتیبانی {openTickets.length > 0 && <Chip>{fa(openTickets.length)} باز</Chip>}
        </SectionTitle>
        {openTickets.length === 0 ? (
          <EmptyState>تیکت بازی وجود ندارد. 🎉</EmptyState>
        ) : (
          <div className="space-y-3">
            {openTickets.map((ticket) => (
              <div
                key={ticket.id}
                className={`rounded-xl border p-4 ${
                  ticket.priority === "URGENT"
                    ? "border-red-300 bg-red-50/50"
                    : "border-slate-200"
                }`}
              >
                <div className="flex flex-wrap items-center gap-2">
                  {ticket.priority === "URGENT" && (
                    <span className="rounded-full bg-red-100 px-2.5 py-0.5 text-xs text-red-700">
                      🔴 فوری
                    </span>
                  )}
                  <span className="font-bold text-slate-800">{ticket.subject}</span>
                  {ticket.customer?.name && (
                    <span className="text-xs text-slate-400">مشتری: {ticket.customer.name}</span>
                  )}
                  <span className="mr-auto text-xs text-slate-400">
                    {new Date(ticket.created_at).toLocaleString("fa-IR", {
                      month: "short",
                      day: "numeric",
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
                  </span>
                </div>
                {ticket.description && (
                  <p className="mt-1 text-sm text-slate-600">{ticket.description}</p>
                )}
                <div className="mt-3 flex gap-2">
                  <Button
                    variant="secondary"
                    onClick={() => void resolveTicket(ticket.id)}
                    disabled={busyId === ticket.id}
                  >
                    ✔️ حل شد
                  </Button>
                  {ticket.conversation && (
                    <Link
                      to={`/stores/${storeId}/chat`}
                      className="rounded-lg px-4 py-2 text-sm font-semibold text-violet-600 hover:underline"
                    >
                      گفتگوی مرتبط #{ticket.conversation}
                    </Link>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
        {resolvedTickets.length > 0 && (
          <div className="mt-4 border-t border-slate-100 pt-3">
            <button
              onClick={() => setShowResolved((v) => !v)}
              className="text-sm text-violet-600 hover:underline"
            >
              {showResolved ? "بستن" : `تیکت‌های حل‌شده (${fa(resolvedTickets.length)})`}
            </button>
            {showResolved && (
              <ul className="mt-2 space-y-1">
                {resolvedTickets.map((ticket) => (
                  <li key={ticket.id} className="text-sm text-slate-500">
                    ✔️ {ticket.subject}
                    {ticket.resolution_note && (
                      <span className="text-xs text-slate-400"> — {ticket.resolution_note}</span>
                    )}
                  </li>
                ))}
              </ul>
            )}
          </div>
        )}
      </Card>
    </div>
  );
}
