# Qasem

**UpMarket (آپ‌مارکت)** — کارمند فروش و مارکتینگ هوش مصنوعی برای فروشگاه‌های آنلاین.

- 🚀 اجرا: دابل‌کلیک روی `start.bat` (فقط `COMFYUI_DIR` را داخلش تنظیم کن)
- 🗺️ رودمپ و مرجع کامل توسعه: [ROADMAP.md](ROADMAP.md)
- 🌙 چک‌لیست تست: [test.md](test.md)
- 🏗️ مستندات معماری: [docs/](docs/)
- 📡 مرجع API (همان چیزی که واقعاً ساخته شده): [docs/API.md](docs/API.md)
- ✅ تست کامل بدون مدل‌ها: [docs/VERIFICATION.md](docs/VERIFICATION.md)
- ⚙️ بک‌اند (Django + Celery + Ollama + ComfyUI): [backend/README.md](backend/README.md)
- 🖥️ فرانت‌اند (React + Vite + TS): [frontend/README.md](frontend/README.md)

## Self-check خودکار

`start.bat` قبل از بالا آوردن سرویس‌ها، کل برنامه را با **مدل‌های شبیه‌سازی‌شده**
اجرا می‌کند — از لاگین تا انتشار، شامل تولید ویدیو. حدود یک دقیقه، بدون نیاز به
GPU، Ollama یا ComfyUI:

```
[OK]   AI pipelines - analysis, market, captions, poster, script, video, chat
[OK]   API end-to-end - login, catalog, content, chat, orders, campaigns, publish
```

`[FAIL]` یعنی مشکل از **کد** است نه مدل‌ها. رد کردن: `start.bat /notest`.
تست‌های دستی و عمیق‌تر: [docs/VERIFICATION.md](docs/VERIFICATION.md).
