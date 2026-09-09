import { useEffect, useState } from "react";
import { Link, Navigate, NavLink, Outlet, useLocation, useParams } from "react-router-dom";

import { api } from "../api/client";
import { useAuth } from "../features/auth/AuthContext";
import NotificationsBell from "./NotificationsBell";
import ThemeToggle from "./ThemeToggle";
import UsageWidget from "./UsageWidget";
import { Spinner } from "./ui";

type Store = { id: number; name: string };

/** Nav entries that need a store in the URL are hidden until one is chosen —
 *  a link that 404s is worse than a link that is not there. */
const storeNav = [
  { to: (id: string) => `/stores/${id}`, label: "فروشگاه", icon: "🏪", end: true },
  { to: (id: string) => `/stores/${id}/sales`, label: "فروش و پشتیبانی", icon: "💰" },
  { to: (id: string) => `/stores/${id}/chat`, label: "چت آزمایشی", icon: "💬" },
  { to: (id: string) => `/stores/${id}/campaigns`, label: "کمپین‌ها", icon: "🚀" },
  { to: (id: string) => `/stores/${id}/analytics`, label: "آمار", icon: "📈" },
  { to: (id: string) => `/stores/${id}/plan`, label: "پلن و مصرف", icon: "🧾" },
];

export default function Layout() {
  const { user, loading, logout } = useAuth();
  const location = useLocation();
  const params = useParams();
  const [stores, setStores] = useState<Store[]>([]);
  const [open, setOpen] = useState(false);

  // the store in the URL wins; otherwise remember the last one used so a
  // refresh on the dashboard still shows the right sidebar
  const urlStore = params.id && location.pathname.startsWith("/stores/") ? params.id : null;
  const [activeStore, setActiveStore] = useState<string | null>(
    urlStore ?? localStorage.getItem("last-store"),
  );

  useEffect(() => {
    if (urlStore) {
      setActiveStore(urlStore);
      localStorage.setItem("last-store", urlStore);
    }
  }, [urlStore]);

  useEffect(() => {
    if (!user) return;
    api
      .get("/stores/")
      .then(({ data }) => setStores(data.results ?? data ?? []))
      .catch(() => setStores([]));
  }, [user]);

  useEffect(() => setOpen(false), [location.pathname]);

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <Spinner size={30} />
      </div>
    );
  }
  if (!user) return <Navigate to="/login" replace />;

  const sidebar = (
    <aside
      className="flex w-64 shrink-0 flex-col gap-1 p-4"
      style={{ background: "var(--sidebar)", minHeight: "100dvh" }}
    >
      <Link
        to="/"
        className="mb-5 block text-xl font-extrabold text-white no-underline"
      >
        آپ‌مارکت
      </Link>

      {stores.length > 0 && (
        <select
          value={activeStore ?? ""}
          onChange={(e) => {
            const id = e.target.value;
            setActiveStore(id);
            localStorage.setItem("last-store", id);
            window.location.href = `/stores/${id}`;
          }}
          className="mb-4 w-full rounded-lg px-3 py-2 text-sm"
          style={{
            background: "rgb(255 255 255 / .07)",
            color: "#e2e8f0",
            border: "1px solid rgb(255 255 255 / .12)",
          }}
          aria-label="انتخاب فروشگاه"
        >
          {stores.map((s) => (
            <option key={s.id} value={s.id} style={{ color: "#000" }}>
              {s.name}
            </option>
          ))}
        </select>
      )}

      <NavLink to="/" end className={({ isActive }) => `u-nav-item ${isActive ? "active" : ""}`}>
        <span>🏠</span> داشبورد
      </NavLink>

      {activeStore && (
        <>
          <div
            className="mt-4 mb-1 px-3 text-xs font-semibold"
            style={{ color: "rgb(148 163 184 / .7)" }}
          >
            فروشگاه
          </div>
          {storeNav.map((item) => (
            <NavLink
              key={item.label}
              to={item.to(activeStore)}
              end={item.end}
              className={({ isActive }) => `u-nav-item ${isActive ? "active" : ""}`}
            >
              <span>{item.icon}</span> {item.label}
            </NavLink>
          ))}
        </>
      )}

      <div className="mt-auto pt-4">
        {activeStore && <UsageWidget storeId={activeStore} />}
        <div
          className="mt-3 flex items-center justify-between rounded-lg px-3 py-2"
          style={{ background: "rgb(255 255 255 / .05)" }}
        >
          <span className="truncate text-sm" style={{ color: "var(--sidebar-fg)" }}>
            {user.username}
          </span>
          <button
            onClick={logout}
            className="text-xs font-semibold"
            style={{ color: "#f87171", background: "none", border: "none", cursor: "pointer" }}
          >
            خروج
          </button>
        </div>
      </div>
    </aside>
  );

  return (
    <div className="flex" style={{ minHeight: "100dvh" }}>
      <div className="hidden lg:flex">{sidebar}</div>

      {open && (
        <div className="fixed inset-0 z-40 flex lg:hidden">
          <div
            className="absolute inset-0"
            style={{ background: "rgb(0 0 0 / .5)" }}
            onClick={() => setOpen(false)}
          />
          <div className="relative z-10">{sidebar}</div>
        </div>
      )}

      <div className="flex min-w-0 flex-1 flex-col">
        <header
          className="sticky top-0 z-30 flex items-center gap-3 px-4 py-3"
          style={{
            background: "color-mix(in srgb, var(--bg) 88%, transparent)",
            backdropFilter: "blur(10px)",
            borderBottom: "1px solid var(--line)",
          }}
        >
          <button
            onClick={() => setOpen(true)}
            className="u-btn u-btn-ghost u-btn-sm lg:hidden"
            aria-label="منو"
          >
            ☰
          </button>
          <div className="mr-auto flex items-center gap-2">
            <ThemeToggle />
            <NotificationsBell />
          </div>
        </header>

        <main className="mx-auto w-full max-w-7xl flex-1 px-4 py-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
