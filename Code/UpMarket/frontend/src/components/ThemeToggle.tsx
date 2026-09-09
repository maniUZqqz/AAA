import { useEffect, useState } from "react";

const KEY = "upmarket-theme";

/** Light ⇄ dark for the panel, remembered per browser. */
export default function ThemeToggle() {
  const [dark, setDark] = useState(
    () => (localStorage.getItem(KEY) ?? "light") === "dark",
  );

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", dark ? "dark" : "light");
    try {
      localStorage.setItem(KEY, dark ? "dark" : "light");
    } catch {
      /* private mode — the choice just will not persist */
    }
  }, [dark]);

  return (
    <button
      onClick={() => setDark((v) => !v)}
      className="u-btn u-btn-ghost u-btn-sm"
      aria-label={dark ? "تم روشن" : "تم تیره"}
      title={dark ? "تم روشن" : "تم تیره"}
    >
      {dark ? "☀️" : "🌙"}
    </button>
  );
}
