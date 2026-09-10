# UpMarket (آپ‌مارکت) — رودمپ و راهنمای کامل توسعه

> **این فایل تنها مرجع توسعه پروژه است.** سه فایل قبلی (`چت و رود مپ .md`، `New Text Document.txt`، `Ollama.txt`) در این فایل ادغام شده‌اند و توسعه فقط بر اساس همین فایل جلو می‌رود.

---

## فهرست

1. [چشم‌انداز محصول](#۱-چشمانداز-محصول)
2. [زیرساخت AI لوکال — دانلود، نصب و راه‌اندازی](#۲-زیرساخت-ai-لوکال)
3. [تقسیم وظایف مدل‌ها و استک فنی](#۳-تقسیم-وظایف-مدلها)
4. [وضعیت فعلی ریپو](#۴-وضعیت-فعلی-ریپو)
5. [رودمپ فازبندی‌شده — دوره‌ی اول (فاز ۰ تا ۱۷)](#۵-رودمپ-فازبندیشده)
6. [قوانین کار با Claude Code](#۶-قوانین-کار-با-claude-code)
7. [**نقص‌های تأییدشده — ۱۴ مورد با شاهد در کد**](#۷-نقصهای-تأییدشده)
8. [**تصمیم‌های معماری دوره‌ی دوم**](#۸-تصمیمهای-معماری-دورهی-دوم)
9. [**سیستم‌های جدید — ۱۱ سیستم**](#۹-سیستمهای-جدید)
10. [**تصمیم‌های باز**](#۱۰-تصمیمهای-باز)
11. [**رودمپ دوره‌ی دوم (فاز ۰.۵ و ۱۸ تا ۲۶)**](#۱۱-رودمپ-دورهی-دوم)
12. [Master Development Specification (مرجع اصلی پیاده‌سازی — انگلیسی)](#upmarket--master-development-specification)

---

## ۱. چشم‌انداز محصول

UpMarket یک **«کارمند فروش و مارکتینگ هوش مصنوعی» برای فروشگاه‌های آنلاین** است — نه صرفاً یک ابزار تولید محتوا.

صاحب فروشگاه باید بتواند:

1. فروشگاه بسازد و اطلاعات برند/کسب‌وکارش را وارد کند.
2. محصولات را با عکس، قیمت، موجودی و مشخصات اضافه کند.
3. هوش مصنوعی محصولات را **تحلیل** کند (تحلیل بصری + استراتژی) و با رقبا مقایسه کند.
4. **چت‌بات فروش** کامل داشته باشد که بدون نیاز به انسان، مثل آنلاین‌شاپ‌ها پاسخ دهد، پیشنهاد بدهد، اعتراض مشتری را مدیریت کند و سفارش ثبت کند.
5. **پوستر تبلیغاتی** + کپشن آن تولید کند.
6. **عکس محصول را ادیت/حرفه‌ای** کند (آماده اینستاگرام) + کپشن آن.
7. **سناریوی ویدیوی تبلیغاتی** بنویسد + کپشن.
8. ویدیو را **قطعه‌قطعه ۵ ثانیه‌ای** تولید کند (محدودیت مدل ویدیو) و به هم بچسباند؛ **فریم آخر هر قطعه، ورودی قطعه بعدی** می‌شود تا ویدیو پیوسته باشد.
9. روی ویدیو **صداگذاری (TTS)** هماهنگ با سناریو انجام دهد.
10. محتوای تأییدشده را از طریق **n8n** در شبکه‌های اجتماعی منتشر کند.
11. در آینده: آنالیتیکس و یادگیری از نتایج برای بهبود تصمیم‌های بعدی.

فلسفه اصلی:

```
STORE DATA → PRODUCT KNOWLEDGE → MARKET INTELLIGENCE → AI STRATEGY
→ CONTENT → CUSTOMER CONVERSATION → SALE → PUBLISHING → ANALYTICS → LEARNING
```

---

## ۲. زیرساخت AI لوکال

### ۲.۱. لینک‌های دانلود (git.ir)

| مورد | لینک |
|---|---|
| اپ Ollama (نصب‌کننده ویندوز) | https://cdn12.git.ir/softwares/ollama-models/OllamaSetup-git.ir.exe |
| فایل مانیفست‌ها (blobs/manifests) | https://cdn12.git.ir/softwares/ollama-models/blobs-manifests-2026-03-24-git.ir.zip |
| مدل کدر — deepseek-coder-6.7b | https://cdn14.git.ir/ollama/sha256-1194192cf2a187eb02722edcc3f77b11d21f537048ce04b67ccf8ba78863006a.zip |
| مدل ویژن (تصویر) | https://cdn14.git.ir/ollama/sha256-b1da6f96a2e40e5db05b6066d799c69411225b336bfa20ef1b002c223ed4b190.zip |
| مدل ریسرچ — qwq-32b | https://cdn12.git.ir/softwares/ollama-models/qwq-32b-git.ir.zip |

> **وضعیت:** مدل‌ها از git.ir دانلود شده‌اند. **مدل تصویر و ویدیو (ComfyUI) دانلود شده ولی هنوز روی این سیستم منتقل نشده است.**

### ۲.۲. مدل‌های Ollama و دستور اجرا

| # | نقش | دستور |
|---|---|---|
| 1 | ویژن (تحلیل تصویر) | `ollama run qwen3-vl:30b` |
| 2 | کدر (اصلی) | `ollama run qwen3-coder:30b` |
| 3 | ریسرچ / Reasoning | `ollama run qwq:32b` |
| 4 | کدر (سبک) | `ollama run deepseek-coder:6.7b` |

### ۲.۳. مدل‌های ComfyUI

- `FLUX.1 [dev] FP8.safetensors` — تولید و ادیت تصویر
- `wan_2.2_i2v_high_noise_14B_fp8_scaled.safetensors` — شروع generation ویدیو
- `wan_2.2_i2v_low_noise_14B_fp8_scaled.safetensors` — ادامه ویدیو و حفظ پیوستگی
- `umt5_xxl_fp8_e4m3fn_scaled.safetensors` — تکست‌انکودر
- `wan_2.1_vae.safetensors` — VAE
- `lightx2v_12V_14B_480p_cfg_step_distill_rank64_bf16.safetensors` — سریع‌ترکردن generation (distill)

### ۲.۴. راه‌اندازی سرور Ollama (روی سرور)

قبل از `ollama serve` متغیرهای محیطی را تنظیم کن (PowerShell):

```powershell
# Flash Attention و پردازش موازی
$env:OLLAMA_FLASH_ATTENTION = 1
$env:OLLAMA_NUM_PARALLEL = 2

# طول کانتکست — بهترین تعادل سرعت/کانتکست برای این سیستم: 8192
$env:OLLAMA_CONTEXT_LENGTH = 8192
# یا به صورت دائمی:
setx OLLAMA_NUM_CTX 131072

ollama serve
```

نمایش کانتکست و مشخصات مدل:

```powershell
ollama show qwen3-coder:30b
```

### ۲.۵. اتصال Claude Code به سرور Ollama (روی سیستم لوکال)

```powershell
$env:ANTHROPIC_AUTH_TOKEN = "ollama"
$env:ANTHROPIC_API_KEY = ""
$env:ANTHROPIC_BASE_URL = "http://192.168.10.80:11434"   # آدرس سرور در شبکه
# یا اگر روی همین سیستم است / تانل SSH:
# $env:ANTHROPIC_BASE_URL = "http://localhost:11434"

claude --model qwen3-coder:30b
```

---

## ۳. تقسیم وظایف مدل‌ها

| مدل / ابزار | وظیفه |
|---|---|
| Qwen3-Coder 30B | کمک توسعه، تحلیل کد، ابزارهای داخلی |
| Qwen3-VL 30B | دیدن و تحلیل عکس محصول، عکس رقبا، محتوای بصری |
| QwQ 32B | Reasoning، استراتژی، تحلیل محصول/رقبا، سناریو و تصمیم‌گیری |
| FLUX.1-dev FP8 | تولید و ادیت تصویر |
| Wan 2.2 High Noise | شروع generation ویدیو |
| Wan 2.2 Low Noise | ادامه/انتقال ویدیو و حفظ continuity |
| LightX2V | سریع‌ترکردن generation در جاهای مناسب |
| FFmpeg | برش، اتصال، صدا، تبدیل فرمت |
| ComfyUI | موتور اجرای مدل‌های تصویری/ویدیویی |
| Django + DRF | هسته Backend |
| React (Vite + TS + Tailwind) | پنل فروشگاه |
| Celery + Redis | صف Jobها (تولید ویدیو/تصویر) |
| SQLite (پیش‌فرض جنگو) | دیتابیس — بدون نصب اضافه؛ در صورت نیاز به مقیاس، بعداً فقط تنظیمات DB عوض می‌شود |
| ~~Django Channels / WebSocket~~ | ~~نمایش زنده وضعیت generation~~ — **پیاده نشد**؛ `asgi.py` خالی است و فرانت هر ۲.۵ ثانیه polling می‌کند. برنامه‌ی جایگزینی در [فاز ۲۰](#فاز-۲۰--generation-pipeline) |
| n8n | اتوماسیون و انتشار در شبکه‌های اجتماعی |

معماری کلی:

```
                    ┌─────────────────────┐
                    │      UpMarket       │
                    │    Web Dashboard    │
                    └──────────┬──────────┘
                               │
                         React / API
                               │
                    ┌──────────▼──────────┐
                    │   Django Backend    │
                    │ Auth / Stores /     │
                    │ Products / Orders / │
                    │ AI Jobs / Content   │
                    └──────────┬──────────┘
                               │
                 ┌─────────────┼─────────────┐
                 ▼             ▼             ▼
             QwQ 32B      Qwen3-VL      Qwen3-Coder
             Reasoning      Vision         Coding
                 └──────┬──────┘
                        │
                  AI Orchestrator
                        │
             ┌──────────┴──────────┐
             ▼                     ▼
          ComfyUI               Tools
        ┌────┴────┐         FFmpeg / TTS /
        ▼         ▼          Web Search
      FLUX       WAN
        └────┬────┘
             ▼
          Content (Images / Videos)
             │
             ▼
            n8n → Social Platforms
```

---

## ۴. وضعیت فعلی ریپو

**(به‌روزرسانی ۲۰۲۶/۰۸/۲۷ — سه بخش قدیمی در پروژه واحد `backend/` ادغام شدند)**

- `backend/` — **پروژه واحد Django** (ادغام API + json + Main):
  - `apps/accounts` (JWT)، `apps/stores`، `apps/products`، `apps/jobs`، `apps/ai` (هوش محصول + تحلیل بازار + embeddings)، `apps/customers` (ایجنت فروش + سفارش + رسید پرداخت + تیکت + اعلان)، `apps/content` (کپشن/تصویر/سناریو/ویدیو/صدای دوزبانه)، `apps/campaigns` (کمپین + انتشار n8n)، `apps/analytics` (+ داشبورد فروش)
  - `services/` — ai (Ollama + روتر + embeddings + پرامپت‌های نسخه‌دار)، comfyui (کلاینت + ۳ ورک‌فلوی نسخه‌دار)، video (FFmpeg)، audio (edge-tts/gTTS دوزبانه)، research (دیجی‌کالا/ترب/SearXNG/Brave)، publishing (n8n)
  - **۱۱۸ تست — همه سبز ✅** (AI با mock، FFmpeg و ریسرچ واقعی)
  - **اصلاحات پایداری (۲۰۲۶/۰۸/۲۷):** گراف FLUX txt2img اصلاح شد (cfg=1.0 + نود FluxGuidance — قبلاً cfg=7 خروجی را می‌سوزاند)؛ بن‌بست انتشار n8n رفع شد (ریست PENDINGهای رهاشده + جلوگیری از پست تکراری با skip پلتفرم‌های SENT)؛ گارد دوبار-کلیک برای تولید ویدیو/صدا (409 + خود-ترمیمی Job مرده)؛ تولید ویدیو در حالت synchronous بلاک می‌شود (نیازمند صف)؛ `start.bat` دو worker جدا (ai/gpu) اجرا می‌کند تا ویدیو بقیه Jobها را بلاک نکند؛ فرانت: سقف خطای polling + رفع نشتی interval + دریافت همه صفحات pagination + فونت وزیرمتن باندل‌شده
  - **اصلاحات بازخورد تست واقعی — beter.md (۲۰۲۶/۰۸/۲۹، هر ۱۱ مورد):** تاریخچه چت در UI؛ ترمیم چندمرحله‌ای JSON مدل + یک تلاش خوداصلاحی مدل (`generate_json`) و رفع قطع‌شدن خروجی (کانتکست ۲۰۴۸→۸۱۹۲ + KV q8_0 در start.bat، تایم‌اوت Ollama ۱۸۰→۶۰۰ برای لود سرد مدل ۳۲B)؛ ادامه خودکار polling بعد از رفرش (`useJobRunner.resume` + فیلترهای `/jobs/`) و کامپوننت `JobProgress` با نوار پیشرفت/کرونومتر؛ پوستر حالا img2img از عکس واقعی محصول + **درج متن فارسی با کد** (Pillow + وزیرمتن باندل‌شده + RTL، `services/imaging/text_overlay.py`) و بن سخت text در negative؛ تحلیل بازار v3 با `competitors`/`comparison` ساختاریافته + کارت رقبا در UI؛ کپشن به محتوای مشخص وصل شد (`Caption.about_image/about_video` + انتخاب‌گر در UI، پرامپت v3)؛ هماهنگ‌کننده GPU (`services/gpu.py`: آنلود Ollama قبل از ComfyUI و برعکس، `GPU_AUTO_UNLOAD`)؛ `GET video-script` حالا 200+null؛ پشتیبانی Redis پرتابل در start.bat + پیام‌های 503 راهنما؛ فلگ‌های v7 React Router. **۱۳۲ تست سبز.**
- `frontend/` — **داشبورد React** (Vite + TypeScript + Tailwind v4، فارسی RTL): احراز هویت، فروشگاه/محصول، پنل‌های هوش محصول، تحلیل بازار (+نتایج وب)، استودیوی تصویر، کپشن‌ها، استودیوی ویدیو (+صداگذاری)، چت فروش، کمپین‌ها و انتشار، صفحه آمار
- `start.bat` — **لانچر یک‌کلیکی** با pre-flight کامل: چک پایتون/نود/ffmpeg، ساخت خودکار `.env`، نصب خودکار پکیج‌ها، migrate، ساخت کاربر ادمین (admin/admin1234)، اجرای همه سرویس‌ها، و health-check با گزارش [OK]/[WARN]/[FAIL]
- `test.md` — چک‌لیست کامل تست شبانه + جدول خطایابی
- `docs/` — مستندات معماری فاز ۰
- آرشیوهای قدیمی (`_archive_old_code/`، `_archive_old_docs/`) در ۲۰۲۶/۰۸/۲۷ **حذف شدند** — هرچه لازم بود قبلاً منتقل شده

> **نکته دو-سیستمی:** توسعه روی این سیستم انجام می‌شود (بدون مدل)؛ مدل‌ها روی **سیستم اصلی** هستند. اتصال فقط با `.env` (`OLLAMA_BASE_URL`, `COMFYUI_BASE_URL`) — راهنمای کامل در `backend/README.md`.

> **⚠️ به‌روزرسانی ۲۰۲۶/۰۹ — بازبینی کد:** این بخش وضعیت را درست توصیف می‌کند، ولی کامل نیست.
> ۱۴ نقص تأییدشده (۶ مورد بحرانی) با شاهد در فایل و خط در [بخش ۷](#۷-نقصهای-تأییدشده) فهرست شده‌اند؛
> تصمیم‌های معماری در [بخش ۸](#۸-تصمیمهای-معماری-دورهی-دوم)، سیستم‌های جدید در [بخش ۹](#۹-سیستمهای-جدید)،
> و فازبندی در [بخش ۱۱](#۱۱-رودمپ-دورهی-دوم).

---

## ۵. رودمپ فازبندی‌شده

وضعیت هر فاز را بعد از تکمیل و تأیید، تیک بزن. **هیچ فازی قبل از تأیید فاز قبلی شروع نمی‌شود.**

- [x] **فاز 0 — بررسی ریپو و معماری**: هیچ کدی زده نمی‌شود؛ فقط مستندات معماری در `docs/` تولید می‌شود. ✅ (۲۰۲۶/۰۸/۲۷ — مستندات در `docs/` تولید شد؛ ۱۰ تصمیم معماری منتظر تأیید در `docs/ARCHITECTURE.md §10`)
- [ ] **فاز 0.5 — تست واقعی مدل‌ها (پروتوتایپ)**: قبل از ساخت SaaS، یک pipeline کوچک واقعی: محصول واقعی → Qwen3-VL → QwQ → FLUX → Wan 2.2 (۵ ثانیه) → فریم آخر → Wan 2.2 (۵ ثانیه بعدی) → FFmpeg → صدا → **یک تیزر ۱۰ ثانیه‌ای نهایی**. اگر کیفیت خروجی قابل‌فروش نبود، همین‌جا pipeline/مدل‌ها اصلاح می‌شود، نه بعد از یک ماه کدنویسی. **⚠️ این فاز هرگز اجرا نشد و حالا دروازه‌ی کل دوره‌ی دوم است — تعریف کامل‌شده‌اش در [بخش ۸](#-فاز-۰۵--بنچمارک-واقعی-دروازه).**
- [ ] **فاز 1 — Foundation**: Django + React + SQLite + Redis + Celery + Auth + تست‌ها. (DoD: همه سرویس‌ها بالا می‌آیند و به هم وصل‌اند) — ⏳ *بک‌اند + فرانت React + دیتابیس SQLite کامل و تأیید شد (۲۰۲۶/۰۸/۲۷)؛ فقط مانده: تست Redis/Celery روی سیستم اصلی*
- [x] **فاز 2 — مدیریت فروشگاه**: مدل Store/Profile/تنظیمات برند + ایزوله‌سازی tenant. (DoD: کاربر فروشگاه می‌سازد و امن مدیریت می‌کند) ✅ *API + تست tenancy + UI کامل (۲۰۲۶/۰۸/۲۷)*
- [x] **فاز 3 — مدیریت محصول**: محصول، دسته‌بندی، واریانت، موجودی، قیمت، آپلود عکس. (DoD: مدیریت کامل کاتالوگ) ✅ *API + تست‌ها + UI کامل شامل آپلود/حذف عکس و ویژگی‌ها (۲۰۲۶/۰۸/۲۷)*
- [ ] **فاز 4 — زیرساخت AI**: کلاینت Ollama + لایه AI Orchestrator + روتر مدل + خروجی ساختاریافته + retry/لاگ + نسخه‌بندی پرامپت. (DoD: درخواست واقعی به Ollama از طریق لایه انتزاع) — ⏳ *کد کامل + تست mock؛ مانده: فراخوانی واقعی Ollama روی سیستم اصلی*
- [ ] **فاز 5 — هوش محصول**: تحلیل عکس (Qwen3-VL) + استراتژی (QwQ) → خروجی ساختاریافته ذخیره و نمایش داده می‌شود. — ⏳ *پایپ‌لاین کامل (پرامپت v2 با positioning) + پنل نمایش در UI آماده؛ مانده: اجرای واقعی با Ollama روی سیستم اصلی (DoD نهایی)*
- [ ] **فاز 6 — تحلیل بازار و رقبا**: معماری ریسرچ، جداسازی مشاهدات از نتیجه‌گیری AI، بدون داده جعلی. — ⏳ *کامل + **ریسرچ خودکار وب** (۲۰۲۶/۰۸/۲۷): کد خودش قیمت رقبا را از دیجی‌کالا/ترب می‌گیرد (تست واقعی موفق؛ تبدیل ریال→تومان) + **جستجوی کل وب برای سایت‌های رقیب** از طریق SearXNG خودمیزبان یا Brave API (بدون اسکرپ، بدون خطر بلاک)، کاربر چیزی وارد نمی‌کند، منابع/زمان fetch ثبت می‌شود، پرامپت v2؛ مانده: اجرای واقعی qwq روی سیستم اصلی*
- [ ] **فاز 7 — ایجنت فروش AI**: چت‌بات فروش کامل با intent detection، جستجوی محصول، پاسخ مبتنی بر داده واقعی (قیمت/موجودی)، مدیریت اعتراض، ساخت سفارش، ارجاع به انسان. — ⏳ *کامل پیاده شد (۲۰۲۶/۰۸/۲۷): مدل‌های Customer/Conversation/Message/Order، ایجنت grounded (قیمت/موجودی فقط از DB؛ سفارش در کد اعتبارسنجی می‌شود نه حرف مدل)، ارجاع به انسان، صفحه چت آزمایشی در UI؛ ۱۲ تست — مانده: اجرای واقعی با qwq روی سیستم اصلی*
- [ ] **فاز 7.5 — فروش و پشتیبانی پیشرفته** (۲۰۲۶/۰۸/۲۷): ⏳ *کامل پیاده شد؛ مانده: اجرای واقعی روی سیستم اصلی*
  - **چرخه پرداخت با رسید:** ایجنت با `REQUEST_PAYMENT` اطلاعات پرداخت واقعی (`payment_info` پروفایل) را می‌دهد و رسید می‌خواهد → مشتری عکس رسید را در چت آپلود می‌کند (`PaymentReceipt`) → سفارش `AWAITING_APPROVAL` → **تأیید/رد همیشه با انسان** (AI هرگز دریافت وجه را تأیید نمی‌کند). وضعیت‌های جدید سفارش: `DRAFT → AWAITING_RECEIPT → AWAITING_APPROVAL → CONFIRMED/CANCELLED`
  - **تیکت پشتیبانی:** اکشن `CREATE_TICKET` برای شکایت/مشکل (مدل `SupportTicket` با اولویت فوری/عادی) + پنل حل تیکت
  - **اعلان به کاربر:** مدل `Notification` + زنگوله 🔔 در هدر — ارجاع به انسان، سفارش جدید، رسید جدید، تیکت، و **خطای AI (مواقعی که خودش نمی‌تواند کاری کند)**
  - **پنل «💰 فروش و پشتیبانی»** (`/stores/:id/sales`): KPI (درآمد/سفارش/در انتظار اقدام/تیکت/نرخ تبدیل)، نمودار درآمد و سفارش روزانه (۳۰ روز، پالت اعتبارسنجی‌شده + نمای جدولی)، پرفروش‌ترین محصولات، مدیریت سفارش‌ها با پیش‌نمایش رسید و دکمه تأیید/رد/لغو — اندپوینت `analytics/sales/`
  - **جستجوی برداری (اختیاری):** `ProductEmbedding` + سرویس embeddings روی Ollama (`/api/embed`) برای کاتالوگ‌های بزرگ — با فلگ `EMBEDDINGS_ENABLED` (پیش‌فرض **خاموش** چون مدل embedding هنوز نصب نیست؛ خاموش/خطا → fallback شفاف به جستجوی کلیدواژه‌ای). فعال‌سازی: `ollama pull nomic-embed-text` + env؛ ساخت بردارها: `POST /stores/{id}/embeddings/rebuild/` (سیو محصول هم خودکار به‌روز می‌کند)
- [ ] **فاز 8 — پایه ComfyUI**: کلاینت ComfyUI + نسخه‌بندی ورک‌فلو + پیگیری صف + بازیابی خروجی. (DoD: یک generation واقعی ثبت و دریافت می‌شود) — ⏳ *کامل: کلاینت + سه ورک‌فلوی نسخه‌دار (`wan22_i2v_v1`, `flux_txt2img_v1`, `flux_img_edit_v1` — دو تای FLUX از UI-format تبدیل شدند)؛ مانده: تست واقعی روی سیستم اصلی*
- [ ] **فاز 9 — استودیوی تصویر**: بهبود عکس محصول، تعویض بک‌گراند، صحنه محصول، عکس اینستاگرامی، پوستر تبلیغاتی — با FLUX. — ⏳ *کامل پیاده شد (۲۰۲۶/۰۸/۲۷): سه حالت (پوستر txt2img / عکس اینستاگرامی و بهبود عکس img2img با denoise متفاوت)، جهت‌دهی خلاقانه با QwQ، انتخاب عکس مبنا، گالری در UI؛ مانده: اجرای واقعی با ComfyUI*
- [ ] **فاز 10 — موتور کپشن و محتوا**: کپشن مخصوص اینستاگرام/تلگرام/لینکدین + CTA + کنترل لحن. — ⏳ *کامل پیاده شد (۲۰۲۶/۰۸/۲۷): پرامپت v1، سه سایز کپشن + هشتگ + CTA برای هر پلتفرم، پنل UI با دکمه کپی؛ مانده: اجرای واقعی روی سیستم اصلی*
- [ ] **فاز 11 — موتور سناریوی ویدیو**: کانسپت، صحنه‌بندی، مدت هر صحنه، نریشن، پرامپت بصری/حرکتی، نوع ترنزیشن — خروجی machine-readable. — ⏳ *کامل پیاده شد (۲۰۲۶/۰۸/۲۷): مدل VideoScript/VideoScene، پرامپت v1 (پرامپت‌های diffusion انگلیسی + نریشن فارسی)، اعتبارسنجی ترنزیشن‌ها؛ مانده: اجرای واقعی*
- [ ] **فاز 12 — موتور تولید ویدیو**: قطعات ۵ ثانیه‌ای Wan 2.2 + مدیریت anchor + استخراج فریم آخر + پیوستگی + retry هر قطعه بدون تولید مجدد قطعات موفق + اتصال با FFmpeg. — ⏳ *هسته کامل پیاده شد (۲۰۲۶/۰۸/۲۷): تسک صف gpu با ورک‌فلوی `wan22_i2v_v1`، پیوستگی فریم آخر، resume (قطعات DONE دوباره تولید نمی‌شوند)، اتصال FFmpeg، پلیر در UI؛ NEW_SCENE حالا anchor واقعی با FLUX می‌سازد (اگر خطا بدهد شفاف به فریم قبلی degrade می‌شود)؛ مانده: اجرای واقعی با ComfyUI*
- [ ] **فاز 13 — صدا**: انتزاع TTS + سنکرون نریشن با صحنه‌ها + میکس صدا/ویدیو با FFmpeg. — ⏳ *کامل پیاده شد (۲۰۲۶/۰۸/۲۷): لایه TTSProvider تعویض‌پذیر — پیش‌فرض **edge-tts با صدای فارسی مایکروسافت (FaridNeural)** که همین‌جا تست واقعی شد (gTTS فارسی ندارد و فقط fallback است)؛ صدای هر صحنه با طول واقعی قطعه ویدیو fit می‌شود (بدون قطع وسط جمله)، سکوت برای صحنه‌های بی‌نریشن، میکس روی ویدیوی نهایی + پلیر نسخه صدادار در UI؛ **+ دو زبانه (۲۰۲۶/۰۸/۲۷):** انتخاب «زبان نریشن و صدا» (فارسی/English) در استودیوی ویدیو — سناریو با همان زبان نوشته می‌شود (پرامپت v2) و صدا خودکار match می‌شود (`TTS_VOICE_FA`/`TTS_VOICE_EN`)؛ مانده: اجرای واقعی روی سیستم اصلی (اینترنت لازم)*
- [ ] **فاز 14 — فضای کاری کمپین**: داشبورد کمپین، پیشرفت Jobها، پیش‌نمایش، regenerate، تأیید/رد. — ⏳ *کامل پیاده شد (۲۰۲۶/۰۸/۲۷): مدل Campaign که پوستر/عکس/کپشن/ویدیوی تولیدشده را گروه می‌کند (با اعتبارسنجی هم‌محصولی)، چرخه تأیید DRAFT→APPROVED/REJECTED→PUBLISHED، صفحه کمپین‌ها در UI؛ مانده: تست واقعی*
- [ ] **فاز 15 — انتشار n8n**: webhook امن، payload، وضعیت تحویل، retry. — ⏳ *کامل پیاده شد (۲۰۲۶/۰۸/۲۷): سرویس `send_to_n8n` (توکن + retry/backoff)، مدل PublishJob با وضعیت تحویل هر پلتفرم، payload با URLهای مطلق مدیا، انتشار فقط بعد از تأیید؛ مانده: تست واقعی با n8n (تنظیم `N8N_WEBHOOK_URL` در .env)*
- [ ] **فاز 16 — آنالیتیکس**: عملکرد کمپین/محتوا/فروش — بدون داده ساختگی. — ⏳ *کامل پیاده شد (۲۰۲۶/۰۸/۲۷): تجمیع واقعی (محصولات/گفتگوها/سفارش‌ها+درآمد/کمپین‌ها/انتشار/محتوا/AI/Jobها) + سری زمانی روزانه + صفحه «📈 آمار» با کاشی‌های KPI و سه نمودار تک‌سری (پالت اعتبارسنجی‌شده) و نمای جدولی؛ مانده: دیدن با داده واقعی*
- [ ] **فاز 17 — آماده‌سازی Production**: امنیت، پرفورمنس، ایندکس‌ها، پایداری صف، مانیتورینگ، بکاپ، دیپلوی. — ⏳ *دور اول انجام شد (۲۰۲۶/۰۸/۲۷): rate limiting (قابل تنظیم با env)، محدودیت حجم/نوع آپلود، لاگ ساختاریافته، تنظیمات امنیتی حالت production (فعال با DJANGO_DEBUG=false + envهای SSL)؛ مانده: بکاپ/دیپلوی نهایی بعد از تثبیت روی سیستم اصلی*

**نکته کلیدی پیوستگی ویدیو (فاز ۱۲):** برای هر قطعه، FLUX دوباره اجرا **نمی‌شود** (پیوستگی را خراب می‌کند). پیش‌فرض: فریم آخر قطعه قبلی → ورودی Wan برای قطعه بعدی. فقط وقتی QwQ تشخیص دهد صحنه جدید لازم است (`NEW_SCENE`)، یک anchor جدید با FLUX ساخته می‌شود. انواع ترنزیشن: `CONTINUE` / `TRANSITION` / `NEW_SCENE`.

---

## ۶. قوانین کار با Claude Code

در هر پرامپت/فاز این قوانین برقرار است:

```
Do not move to the next phase.
Do not implement future features.
Do not create fake implementations for unavailable services.
Use real integrations where required.

Before finishing this phase:
1. run tests
2. run migrations
3. run lint/type checks
4. verify the feature manually
5. update documentation
6. report what was implemented
7. report known limitations
8. report exact commands needed to run it

The phase is NOT complete if the application only compiles.
The phase is complete only when the implemented functionality actually works.
```

جزئیات کامل نقش‌ها، معماری، مدل داده، قوانین مهندسی (۱۵ قانون)، معیار تکمیل فاز و گزارش پایان هر فاز، در **Master Specification** پایین همین فایل است — Claude Code باید از روی آن جلو برود.

---

## ۷. نقص‌های تأییدشده

> **بازبینی کد ۲۰۲۶/۰۹.** این‌ها **تأیید** شده‌اند، هیچ‌کدام حدس نیست — هر مورد شاهد در فایل و خط دارد.

### آنچه سالم است

قبل از فهرست نقص‌ها، این‌ها اندازه‌گیری شده‌اند نه ادعا:

| سنجه | نتیجه |
|---|---|
| تست خودکار | **۲۱۴ تست اجرا، همه سبز** (۴ اسکیپ — همه تست FFmpeg، چون روی سیستم توسعه نصب نیست) |
| کد ساختگی | در کل بک‌اند و فرانت **یک** `NotImplementedError` — و آن هم کلاس پایه‌ی TTS است |
| تطبیق داده با کد | `دیتا/0-منبع/check.py` — هر ۱۹ سنجه OK |
| دامنه‌های بک‌اند | ۱۰ اپ مستقل جنگو |
| فرانت | ۸ صفحه + ۵ پنل تخصصی، React + Vite + TS، فارسی RTL |
| سایت عمومی | Next.js 15 با SEO، وبلاگ، sitemap، RSS، قیمت زنده از بک‌اند |

**پس مسئله‌ی این مرحله «اثبات وجود محصول» نیست.** مسئله این است که محصول از یک سیستم توسعه‌ای به یک **پلتفرم Production-Ready، مقیاس‌پذیر، قابل‌کنترل و قابل‌فروش** تبدیل شود.

> **نکته‌ی روش‌شناختی:** `check.py` هر ۱۹ سنجه‌اش grep دنبال یک رشته است. **وجود** را می‌سنجد نه **رفتار**. هیچ‌کدام از نقص‌های زیر را نمی‌توانست بگیرد. این ضعف ابزار است نه ضعف کد — ولی یعنی سبز بودن `check.py` را نباید شاهد سلامت گرفت.

---

### ۷.۱ — بحرانی

#### نقص ۱ — درگاه پرداخت، صفر خط کد

جست‌وجو برای ZarinPal، IDPay، NextPay، Shaparak در کل کد و سایت: **هیچ نتیجه‌ای**.

این یک Feature ناقص نیست؛ مستقیماً مدل درآمدی است.

در `backend/apps/billing/models.py:129-132` متد `renew()` وضعیت را از `TRIALING` به `PAST_DUE` می‌برد — و **هیچ مسیری برای `ACTIVE` شدن وجود ندارد** جز ویرایش دستی در جنگو ادمین.

> سیستمی که قرار است به چندصد فروشگاه سرویس بدهد نمی‌تواند برای فعال‌سازی اشتراک به عملیات دستی ادمین وابسته باشد.

طنز ماجرا: محصول برای *مشتریِ مشتری* چرخه‌ی رسید و تأیید انسانی ساخته، ولی برای اشتراک خودش نساخته.

**راه‌حل:** [۹.۹](#۹۹--اشتراک-اعتبار-و-تضمین-کیفیت) · **فاز:** ۱۹

---

#### نقص ۲ — هیچ آرتیفکتی برای Deployment وجود ندارد

نه `Dockerfile`، نه `docker-compose`، نه Nginx config، نه systemd service، نه Procfile، نه اسکریپت بکاپ، نه مستند دیپلوی.

اجرای فعلی: `start.bat` روی یک Windows Desktop.

فاز ۱۷ می‌گوید «دور اول انجام شد، مانده بکاپ/دیپلوی» — ولی **دور اولی وجود ندارد**؛ هیچ آرتیفکتی نیست.

**راه‌حل:** [۸.۳](#۸۳--زیرساخت-production) · **فاز:** ۱۸

---

#### نقص ۳ — SQLite به‌عنوان دیتابیس Production

`backend/config/settings.py:127-132` هاردکد است و هیچ شاخه‌ای برای PostgreSQL ندارد.

SQLite قفل تک‌نویسنده دارد. معماری هدف چندصد فروشگاه + Workerهای Celery + Jobهای Async همزمان دارد. این قطعاً Bottleneck می‌شود.

**راه‌حل:** [۸.۲](#۸۲--دیتابیس-و-ذخیرهسازی) · **فاز:** ۱۸

---

#### نقص ۴ — مدل ظرفیت زمان LLM را صفر گرفته

`دیتا/0-منبع/data.json` بخش `render` فقط دو چیز را می‌شمارد: ویدیو (۴ دقیقه بر ثانیه) و پوستر (۲ دقیقه بر عکس). با یادداشت «کپشن روی GPU نیست».

ولی `qwq:32b` و `qwen3-vl:30b` **روی همان GPU هستند**. داکسترینگ خودِ `backend/services/gpu.py` می‌گوید این‌ها با FLUX/Wan سر یک کارت رقابت می‌کنند و باید دور هر کار آنلود/لود شوند.

هیچ‌کدام از این‌ها در مدل نیست:

```text
Model Loading
Model Unloading
Model Switching
VRAM Allocation
CPU Offloading
Queue Waiting
Retry
Post Processing
Encoding
```

**راه‌حل:** [۸.۵](#۸۵--hardware-aware-scheduling) · **فاز:** ۰.۵

---

#### نقص ۵ — مدل روی سخت‌افزار جا نمی‌شود

در لاگ واقعی داخل `beter.md`:

```text
GPULayers:29[... Layers:29(35..63)]
llama_model_load: using device CUDA0 (RTX 3060) - 10886 MiB free
```

از ۶۴ لایه‌ی `qwq:32b` فقط **۲۹ لایه** روی GPU جا شده؛ بقیه روی CPU. همین باعث شد «تحلیل رقبا» کلاً ارور بدهد.

یعنی برنامه‌ی سخت‌افزاری ۶۰۰ میلیون تومانی (۲× RTX 3060 12GB) حول مدل‌هایی بسته شده که روی آن کارت جا نمی‌شوند — و نقطه‌ی سر به سر (۱۸۳ مشتری) روی همین می‌نشیند.

**راه‌حل:** [تصمیم ۴](#تصمیم-۴--سختافزار) · **فاز:** ۰.۵

---

#### نقص ۶ — قول «چند دقیقه» با اعداد خودمان نمی‌خواند

FAQ مشتری می‌گوید «یک بسته‌ی کامل محتوا در چند دقیقه آماده می‌شود».

با اعداد خودِ `data.json`، پکیج حرفه‌ای:

```text
۴۵ ثانیه ویدیو × ۴ دقیقه   = ۱۸۰ دقیقه
۱۵ پوستر     × ۲ دقیقه     =  ۳۰ دقیقه
──────────────────────────────────────
                     ۳.۵ ساعت GPU
```

حتی یک ویدیوی ۵ ثانیه‌ای = ۲۰ دقیقه. «چند دقیقه» فقط برای کپشن یا یک پوستر تنها درست است.

**فاز:** ۰.۵ (بازنویسی متن بعد از اندازه‌گیری واقعی)

---

### ۷.۲ — مهم

#### نقص ۷ — حلقه‌ی یادگیری بسته نیست

فلسفه‌ی محصول (بخش ۱):

```text
... → PUBLISHING → ANALYTICS → LEARNING
```

ولی `backend/apps/analytics/services.py` فقط شمارش داخلی می‌کند: گفتگو، سفارش، درخواست AI، کمپین.

**هیچ داده‌ی عملکردی از شبکه‌های اجتماعی وارد سیستم نمی‌شود** — نه بازدید، نه لایک، نه ریچ، نه CTR.

پس بند ۱۱ چشم‌انداز («یادگیری از نتایج برای بهبود تصمیم‌های بعدی») **هیچ مسیر داده‌ای ندارد**. حلقه باز است.

**راه‌حل:** [۹.۸](#۹۸--product-analytics-و-حلقهی-یادگیری) · **فاز:** ۲۵

---

#### نقص ۸ — edge-tts سرویس بیرونی است

کارت اعتماد مشتری می‌گوید: «پردازش روی سرور خودمان انجام می‌شود، نه سرویس خارجی».

`backend/services/audio/tts.py:34` خودش نوشته `needs internet`. edge-tts سرویس مایکروسافت است. **متن نریشن هر ویدیوی هر مشتری به مایکروسافت می‌رود.**

**راه‌حل:** [۸.۷](#۸۷--data-governance-و-privacy) · **فاز:** ۱۸

---

#### نقص ۹ — ModelProvider سراسری است، نه per-store

`backend/apps/ai/models.py:130` هیچ ForeignKey به `Store` ندارد. تنظیم **پلتفرم‌واید** است.

یعنی اپراتور می‌تواند متن/بینایی/تصویر/ویدیو را برای همه به یک API بیرونی سوییچ کند و فروشگاه‌دار نه می‌بیند، نه رضایت می‌دهد، نه تنظیم مخصوص خودش دارد.

**راه‌حل:** [۸.۷](#۸۷--data-governance-و-privacy) · **فاز:** ۱۸

---

#### نقص ۱۰ — هر فروشگاه فقط یک کاربر دارد

`backend/apps/stores/models.py:13` — `Store.owner` یک ForeignKey ساده است. نه تیم، نه نقش، نه کاربر دوم.

صاحب مغازه و آدم مارکتینگش باید یک پسورد را شریک شوند. برای SaaS کافی نیست.

**راه‌حل:** [۹.۱۰](#۹۱۰--چندکاربره-و-نقشها) · **فاز:** ۱۹

---

#### نقص ۱۱ — Polling به‌جای Real-Time

`backend/config/asgi.py` خالی است. Django Channels نصب نیست. فرانت هر ۲.۵ ثانیه HTTP polling می‌کند.

برای Prototype قابل قبول است. برای نمایش پیشرفت لحظه‌ای رندر چندساعته و برای Scale مناسب نیست.

> انصافاً: `data.json` (چیزی که به سرمایه‌گذار نشان داده می‌شود) این را ادعا نکرده. فقط جدول استک بخش ۳ همین فایل کهنه بود و اصلاح شد.

**راه‌حل:** [۸.۶](#۸۶--async-و-real-time) · **فاز:** ۲۰

---

### ۷.۳ — کوچک ولی گران

#### نقص ۱۲ — انتخاب پکیج در درگاه ورودی گم می‌شود

`website/app/pricing/page.tsx:79` به `{panel}/register?plan={slug}` لینک می‌دهد. در کل سایت **۱۳ دکمه CTA** به ثبت‌نام اشاره می‌کنند.

هیچ‌جای فرانت `searchParams` را نمی‌خواند (`frontend/src/App.tsx:22`). کاربر «حرفه‌ای» را انتخاب می‌کند و در صفحه‌ی ثبت‌نام خالی می‌افتد.

Flow درست:

```text
Pricing → Select Plan → Registration → Plan Confirmation
→ Payment → Workspace Creation → Onboarding
```

**فاز:** ۱۹

---

#### نقص ۱۳ — صفحه‌ی تماس فرم ندارد

`website/app/contact/page.tsx` نه `action` دارد نه `fetch`. صفحه‌ی کاملاً استاتیک.

مسیر جذب لید که GTM رویش حساب کرده وجود ندارد. حداقل لازم: Form، Validation، API، Database، Notification، Lead Record، Admin Inbox.

**فاز:** ۱۹

---

#### نقص ۱۴ — لیست ریسک خودمان به جای اشتباه نشانه رفته

`data.json` بخش `gaps` می‌گوید «سایت عمومی و ثبت‌نام آنلاین هنوز ساخته نشده» با شدت **high**.

ولی `website/` یک سایت کامل Next.js 15 است و `/register` هم در پنل هست. **این شکاف بسته شده و لیست کهنه مانده.**

در عوض سه شکاف واقعی (دیپلوی، پرداخت، ظرفیت) با آن شدت در لیست نیستند. یعنی اسلاید ریسکی که سرمایه‌گذار می‌بیند به جای اشتباه اشاره می‌کند.

**فاز:** ۰.۵

---

### جدول خلاصه

| # | نقص | شدت | شاهد | فاز |
|---|---|---|---|---|
| ۱ | درگاه پرداخت صفر خط کد دارد | 🔴 | `apps/billing/models.py:129-132` | ۱۹ |
| ۲ | هیچ آرتیفکت Deployment وجود ندارد | 🔴 | جست‌وجوی کل ریپو | ۱۸ |
| ۳ | SQLite هاردکد، بدون شاخه‌ی PostgreSQL | 🔴 | `config/settings.py:127-132` | ۱۸ |
| ۴ | مدل ظرفیت زمان LLM و Swap را صفر گرفته | 🔴 | `data.json` `render` ↔ `services/gpu.py` | ۰.۵ |
| ۵ | `qwq:32b` روی RTX 3060 جا نمی‌شود (۲۹ از ۶۴ لایه) | 🔴 | لاگ واقعی در `beter.md` | ۰.۵ |
| ۶ | ادعای «چند دقیقه» = ۳.۵ ساعت GPU | 🔴 | `data.json` `render` × `packages` | ۰.۵ |
| ۷ | حلقه‌ی یادگیری باز است | 🟠 | `apps/analytics/services.py` | ۲۵ |
| ۸ | edge-tts بیرونی است ولی «داده پیش ما می‌ماند» تبلیغ می‌شود | 🟠 | `services/audio/tts.py:34` | ۱۸ |
| ۹ | `ModelProvider` سراسری است، نه per-store | 🟠 | `apps/ai/models.py:130` | ۱۸ |
| ۱۰ | هر فروشگاه فقط یک کاربر دارد | 🟠 | `apps/stores/models.py:13` | ۱۹ |
| ۱۱ | Polling ۲.۵ ثانیه‌ای؛ `asgi.py` خالی | 🟠 | `config/asgi.py` | ۲۰ |
| ۱۲ | `?plan=` ساکت دور ریخته می‌شود (۱۳ دکمه CTA) | 🟡 | `pricing/page.tsx:79` ↔ `App.tsx:22` | ۱۹ |
| ۱۳ | صفحه‌ی تماس فرم ندارد | 🟡 | `website/app/contact/page.tsx` | ۱۹ |
| ۱۴ | لیست `gaps` کهنه است | 🟡 | `website/` موجود است | ۰.۵ |

---

## ۸. تصمیم‌های معماری دوره‌ی دوم

### ۸.۱ — اصل حاکم بر کل بازطراحی

مهم‌ترین تغییر نگرش پروژه این است:

> ### ما نباید به مدل AI اعتماد کنیم؛ باید برای مدل AI سیستم کنترل بسازیم.

برای ویدیو:

```text
Prompt → Generation Model → Programmatic Validation → Vision Validation
→ Quality Score → Repair / Regenerate → Human Approval → Final Output
```

برای صدا:

```text
Script → TTS → Audio QC → Timing Analysis
→ Lip / Action Synchronization → Human Approval → Final Output
```

و برای کل محصول:

```text
AI Generation
      +
Engineering Controls
      +
Quality Systems
      +
Human Approval
      +
Performance Feedback
      =
Production-Grade AI Platform
```

**همه‌ی بخش ۹ از همین یک اصل بیرون می‌آید.**

---

### ۸.۲ — دیتابیس و ذخیره‌سازی

#### PostgreSQL برای Production

دلایل: Concurrency بهتر، Transaction قوی، JSONB، Indexing پیشرفته، Full Text Search، قابلیت Scale، سازگاری عالی با Django، مناسب Analytics، امکان Read Replica در آینده.

SQLite برای Development، تست‌های سریع، Local Mode و ابزارهای مستقل باقی می‌ماند.

#### Object Storage جدا از دیتابیس

دیتابیس فقط Metadata نگه دارد:

```text
Video
 ├── id
 ├── store_id
 ├── status
 ├── duration
 ├── quality_score
 └── storage_url      ← خود فایل اینجا نیست
```

معماری هدف:

```text
PostgreSQL  +  Redis  +  Object Storage
 (متادیتا)     (صف)      (عکس/ویدیو/فایل)
```

این برای موتور تدوین ([۹.۵](#۹۵--موتور-تدوین-و-post-production)) **الزامی است، نه اختیاری** — نسخه‌های متعدد یک پروژه‌ی ویدیویی داخل دیتابیس معنا ندارد.

---

### ۸.۳ — زیرساخت Production

```text
                    ┌─────────────────┐
                    │     Client      │
                    │  Web / Mobile   │
                    └────────┬────────┘
                             ▼
                    ┌─────────────────┐
                    │ Nginx / Reverse │
                    │      Proxy      │
                    └────────┬────────┘
               ┌─────────────┴─────────────┐
               ▼                           ▼
        ┌──────────────┐            ┌──────────────┐
        │   Frontend   │            │   Backend    │
        │   Next.js    │            │   Django     │
        └──────────────┘            └──────┬───────┘
                      ┌────────────────────┼────────────────────┐
                      ▼                    ▼                    ▼
                PostgreSQL              Redis            Object Storage
                                           │
                                           ▼
                                    Celery Workers
                          ┌────────────────┼────────────────┐
                          ▼                ▼                ▼
                        Video            Image            AI/API
                       Workers          Workers           Workers
```

الزامات: Dockerfile، docker-compose، Nginx config، Production settings، Logging ساختاریافته، Monitoring، Backup، Secrets Management.

> **همه‌ی سرویس‌ها باید مستقل اجرا شوند. Deployment نباید به سیستم شخصی توسعه‌دهنده وابسته باشد.**

---

### ۸.۴ — AI Gateway

در فاز فعلی پیشنهاد می‌شود **Text AI + Analysis AI + بخشی از Vision به API منتقل شوند.**

مزایا: کاهش فشار GPU، حذف زمان Load/Unload، افزایش ظرفیت، ساده‌تر شدن Scaling، کاهش Memory Pressure، حذف رقابت مدل‌ها روی VRAM.

این مستقیماً [نقص ۴](#نقص-۴--مدل-ظرفیت-زمان-llm-را-صفر-گرفته) را حل می‌کند: اگر LLM روی GPU نباشد، GPU فقط برای FLUX/Wan می‌ماند و مدل ظرفیت واقعی می‌شود.

اما **نباید به یک Provider وابسته شویم**:

```text
AI Gateway
    │
    ├── Text Provider
    ├── Vision Provider
    ├── Reasoning Provider
    ├── Embedding Provider
    └── Future Local Models
```

**قانون سخت: هیچ Business Logic نباید مستقیم API Call بزند.**

این غلط است:

```python
# داخل services/content/…
openai(...)
```

درست:

```text
AIService → AI Gateway → Provider
```

Gateway بر اساس قیمت، کیفیت، سرعت، نوع Task و Privacy Policy فروشگاه ([۸.۷](#۸۷--data-governance-و-privacy)) Provider را انتخاب می‌کند.

> زیرساخت این تا حدی هست: `apps/ai/models.py ModelProvider` و `services/ai/providers.py`. کاری که مانده Gateway واقعی + سیاست انتخاب + per-store scope است.

---

### ۸.۵ — Hardware-Aware Scheduling

نباید بر اساس نام مدل یا حدس، ظرفیت را حساب کرد.

#### Hardware Profiler

سیستم هنگام Startup سخت‌افزار را بخواند:

```text
GPU
 ├── VRAM
 ├── Available VRAM
 ├── CUDA Capability
 ├── Temperature
 ├── Utilization
 └── Concurrent Capacity
```

#### تخمین هزینه‌ی هر Job

```text
Estimated Cost =
    Model Load
  + Model Swap
  + Inference
  + Rendering
  + Post Processing
  + Encoding
  + Validation
  + Retry Probability
```

#### فرمول ظرفیت واقعی

```text
Effective Capacity =
    GPU Available Time
    ─────────────────────────────────────────
    Generation + Model Load + Model Swap
    + Encoding + QC + Retry
```

و بعد **با ضریب اطمینان**. نباید از ۱۰۰٪ ظرفیت GPU در Business Model استفاده کرد. Capacity Reserve لازم است برای: Failures، Maintenance، Traffic Spikes، Retry، Queue، Monitoring.

#### Smart Scheduler

هر کار روی سخت‌افزار مناسبش:

```text
Cut              → CPU
Audio processing → CPU
Color            → CPU/GPU
AI Enhancement   → GPU
Video Generation → GPU
Encoding         → CPU/GPU
```

و اگر GPU درگیر Generation است، کارهای غیرضروری نباید آن را اشغال کنند.

---

### ۸.۶ — Async و Real-Time

#### هر عملیات سنگین = یک Job

هیچ عملیات سنگینی نباید داخل Request وب انجام شود.

به‌جای:

```text
POST /generate
... 20 minutes ...
response
```

باید:

```text
POST /jobs → job_id → GET /jobs/{id}
             progress: 20% → 55% → 100%
```

#### State Machine کامل هر Job

```text
QUEUED → PROCESSING → PREVIEW → WAITING_APPROVAL
→ APPROVED → RENDERING → QC → COMPLETED
                    │
              FAILED / CANCELLED
```

اگر کاربر Cancel کرد:

```text
Cancel → Worker Stop → Temporary Files Cleanup
→ GPU Release → Job Cancelled → Credit Refund
```

#### WebSocket / SSE

```text
Worker → Event → Redis → WebSocket/SSE → Frontend
```

تا کاربر لحظه‌به‌لحظه ببیند:

```text
Generating Segment 03
████████████░░░░ 72%

Quality Check
✓ Motion
✓ Object
⚠ Face Consistency
```

---

### ۸.۷ — Data Governance و Privacy

دو ادعای فعلی باید اصلاح شوند ([نقص ۸](#نقص-۸--edge-tts-سرویس-بیرونی-است) و [نقص ۹](#نقص-۹--modelprovider-سراسری-است-نه-per-store)).

راه‌حل: یک **AI/Data Policy Layer**.

برای هر Store قابل تنظیم:

```text
AI Processing Mode:
  [ Local Only            ]  ← هیچ داده‌ای از سرور خارج نمی‌شود
  [ Approved External     ]  ← فقط Providerهای تأییدشده
  [ Hybrid                ]  ← با اعلام شفاف
```

و برای هر Provider ثبت شود: Data Location، Data Retention، Privacy Policy، Allowed Data Types، Encryption، Consent.

`ModelProvider` باید per-store قابل override شود و AI Gateway ([۸.۴](#۸۴--ai-gateway)) موظف باشد سیاست فروشگاه را رعایت کند.

> اگر فروشگاهی `Local Only` انتخاب کرد و مدل محلی در دسترس نبود، Job باید **شفاف fail شود** — نه اینکه بی‌سروصدا به API بیرونی برود.

---

## ۹. سیستم‌های جدید

### ۹.۱ — تولید تدریجی ویدیو

#### مشکل

```text
Prompt → چند ساعت پردازش → Final Video
```

این برای تجربه‌ی کاربری خطرناک است. مشتری نباید ۳ ساعت صبر کند تا بفهمد خروجی بد است.

#### راه‌حل: Progressive Generation

```text
Generate Segment 01 → QC → Show to Customer → Approve
        ↓
Generate Segment 02 → QC → Show to Customer → Approve
        ↓
       ...
```

کاربر در هر مرحله بتواند: Stop، Reject، Regenerate، Edit Prompt، Change Style، Change Camera، Change Voice، Continue.

#### دو Mode

**Safe Mode** — هر Segment تأیید دستی:

```text
Generate → QC → Show → Approve
```

**Auto Mode** — فقط وقتی کیفیت پایین است متوقف شود:

```text
Generate → QC → Score > Threshold → ادامه‌ی خودکار
                Score < Threshold → توقف و درخواست تأیید
```

Auto Mode پیش‌فرض باشد؛ Safe Mode برای مشتری وسواسی یا محتوای حساس.

#### Scene State — کلید پیوستگی

پیوستگی فعلی فقط با «فریم آخر Segment قبلی» است (بخش ۸ Master Spec). این کافی نیست.

علاوه بر فریم آخر، یک **Scene State** ساختاریافته منتقل شود:

```text
Scene State
├── Characters      (چه کسانی، با چه ظاهری)
├── Objects         (چه اشیایی، با چه رنگ و شکلی)
├── Location
├── Lighting
├── Camera          (زاویه، فاصله، حرکت)
├── Clothing
├── Colors
└── Current Action
```

این State به Prompt Compiler ([۹.۲](#لایه-۱--prompt-compiler)) داده می‌شود و دقیقاً همان چیزی است که مشکل «یکهو همه‌چیز عوض شد» را کنترل می‌کند.

#### قانون هزینه

اگر QC یک Segment را رد کرد، **اعتبار مشتری مصرف نشود**:

```text
Customer Request → Generation → QC
                      ┌──────┴──────┐
                    PASS          FAIL
                      ↓             ↓
              Consume Credit   Refund Credit
```

---

### ۹.۲ — کنترل کیفیت ویدیو

این باید **یکی از اصلی‌ترین مزیت‌های فنی محصول** باشد. صرفاً Prompt Engineering کافی نیست.

#### مشکلاتی که مدل ویدیو تولید می‌کند

درون یک Segment یا بین دو Segment:

| دسته | نمونه |
|---|---|
| هویت | تغییر ناگهانی چهره، تغییر لباس، Face deformation |
| شیء | تغییر رنگ، تغییر Shape، ناپدید شدن، Object duplication |
| آناتومی | دست خراب، انگشت اضافه، Morphing |
| حرکت | Motion غیرطبیعی، سرعت غیرمنطقی، Warp، Camera Jump |
| زمانی | Flickering، Temporal Inconsistency |
| محیط | تغییر ناگهانی نور، تغییر محیط، تغییر سبک |

#### معماری QC

```text
                 Generated Segment
                       │
                       ▼
              ┌─────────────────┐
              │ Frame Extractor │
              └────────┬────────┘
                       ▼
              ┌─────────────────┐
              │ Vision Analysis │
              └────────┬────────┘
          ┌────────────┼────────────┐
          ▼            ▼            ▼
    Temporal       Identity      Motion
    Consistency    Consistency   Analysis
          └────────────┼────────────┘
                       ▼
                 Quality Score
             ┌─────────┴─────────┐
             ▼                   ▼
          PASS                 FAIL
             │                   │
             ▼                   ▼
         Continue          Repair Engine
```

#### لایه ۱ — Prompt Compiler

قبل از ارسال، سیستم خودش Prompt را تقویت کند.

کاربر می‌گوید:

> یک خانم محصول را معرفی کند.

Compiler اضافه می‌کند: `consistent character`، `consistent clothing`، `stable environment`، `natural movement`، `continuous motion`، `stable camera`، `realistic physics`، `consistent lighting`، `object permanence`، `no sudden transformation` — به‌علاوه‌ی Scene State از Segment قبلی.

#### لایه ۲ — Vision Controller

بعد از تولید، فریم‌ها استخراج و بررسی شوند:

- **Character Consistency** — آیا شخصیت از فریم اول تا آخر همان است؟ (Face Embedding، Face Landmark، Head Pose)
- **Object Consistency** — شکل/رنگ/اندازه‌ی محصول تغییر کرده؟ ناپدید شده؟ دوباره با شکل متفاوت ظاهر شده؟
- **Environment Consistency** — محیط ناگهان عوض شده؟
- **Motion** — حرکت طبیعی است؟ (Optical Flow، Motion Discontinuity)
- **Temporal Consistency** — فریم N به N+1 پیوسته است؟
- **Physics** — اشیا قوانین فیزیک را رعایت می‌کنند؟
- **Camera** — حرکت دوربین منطقی است؟
- **Artifact Detection** — دست خراب، انگشت اضافی، Morphing، Flickering، Warping

#### Quality Score

برای هر Segment:

```text
Overall Score: 87/100

Temporal Consistency: 92
Object Consistency:   88
Face Consistency:     95
Motion Quality:       81
Visual Quality:       90
Physics:              84
```

آستانه‌ی نمونه:

```text
90-100 → Excellent
80-89  → Good
70-79  → Review
<70    → Regenerate
```

> این اعداد **نمونه‌اند**. باید بعد از بنچمارک واقعی (فاز ۰.۵) تنظیم شوند.

#### قانون محصول: عکس واقعی در انتهای پست

در محتوای بازاریابی محصول، **عکس واقعی خود محصول در انتهای پست/ویدیو قرار بگیرد** تا مشتری دقیقاً همان چیزی را ببیند که می‌خرد.

و پیش از آن، بینایی ماشین + کد کنترل کنند که محتوای تولیدشده **محصول را عوض نکرده باشد** — همان Object Consistency بالا، ولی این‌بار با مرجع مشخص: عکس اصلی محصول از دیتابیس.

---

### ۹.۳ — موتور تعمیر سه‌سطحی

تشخیص مشکل کافی نیست. سیستم باید تا جای ممکن **خودش تعمیر کند** — و مهم‌تر، **قبل از مصرف دوباره‌ی GPU**.

#### اصل

```text
Problem Detected → Can Code Fix It?
                        ├── YES → Code-based Repair → Recheck
                        └── NO  → AI Regeneration
```

مثال:

```text
Problem: Low Exposure
  → قابل اصلاح الگوریتمی؟ بله
  → Color Engine → Recheck

Problem: Character identity changed
  → قابل اصلاح الگوریتمی؟ نه
  → Regeneration
```

#### سه سطح

**سطح ۱ — کد (ارزان‌ترین)**
FFmpeg، OpenCV، Audio DSP، Color Processing.
برای: نور، رنگ، لرزش، Flicker، نویز، صدا.

**سطح ۲ — Computer Vision**
Face، Object، Motion، Scene، Tracking، Temporal Analysis.
برای تصمیم‌گیری و اصلاح موضعی.

اینجا همان چیزی است که برای نقص‌های جزئی لازم است: اگر همه‌چیز درست بود ولی **یک قسمت کوچک** مشکل داشت (مثلاً انگشت بد درآمده)، کد باید بتواند همان ناحیه را موضعی اصلاح کند (inpaint/patch) به‌جای رندر دوباره‌ی کل Segment. پردازش به‌شدت پایین‌تر می‌آید.

**سطح ۳ — AI (آخرین گزینه)**
فقط وقتی مشکل واقعاً معنایی است: Bad hand غیرقابل‌ترمیم، Wrong object، Identity change، Impossible geometry، Severe artifact.

#### قانون بازتولید

```text
Segment 1 ✓
Segment 2 ✓
Segment 3 ✗   ← فقط این دوباره تولید شود
Segment 4 —
```

هرگز کل ویدیو از ابتدا رندر نشود.

Repair Strategy برای Segment خراب:

```text
Regenerate Segment
    + Reference Frame (فریم آخر Segment قبلی)
    + Scene State
    + Modified Prompt (بر اساس نوع مشکل تشخیص‌داده‌شده)
```

> **این معماری باعث می‌شود AI گران‌قیمت آخرین گزینه باشد، نه اولین گزینه.**

---

### ۹.۴ — موتور صدا

Audio نباید Feature فرعی باشد. صدای غیرطبیعی حتی یک ویدیوی تصویری عالی را خراب می‌کند.

هدف:

> صدای طبیعی + لحن مناسب + تلفظ درست + Timing دقیق + هماهنگی با اتفاقات ویدیو

#### Pipeline

```text
Script
  ↓
Text Normalizer        (اعداد، تاریخ، مخفف، انگلیسی داخل فارسی)
  ↓
Pronunciation Engine   (نام برند، واژه‌های خاص)
  ↓
Voice Engine
  ↓
Emotion / Style Controller
  ↓
Audio QC
  ↓
Timing / Phoneme Analysis
  ↓
Video Synchronization
  ↓
Final Audio
```

#### Provider-Based

```text
Voice Engine
    ├── Local TTS              ← برای Local Only mode
    ├── Cloud TTS              ← edge-tts فعلی
    └── Future Custom Voice Model
```

انتخاب Engine بر اساس: زبان، جنس صدا، سبک، Emotion، سرعت، کیفیت، هزینه، Hardware، و **Privacy Policy فروشگاه** ([۸.۷](#۸۷--data-governance-و-privacy)).

#### Voice Profile

برای هر صدا: Language، Gender، Age، Accent، Speaking Rate، Pitch، Emotion، Energy، Pause Style.

#### Audio QC

قبل از Final Render ارزیابی شود: Pronunciation، Pauses، Speaking Rate، Pitch Variation، Emotion، Loudness، Clipping، Noise، Robotic Artifacts، Timing.

اگر صدا مصنوعی، بریده‌بریده یا غیرطبیعی بود، سیستم قبولش نکند و دوباره تولید کند.

#### هم‌زمانی صدا و تصویر

```text
Script → Voice Generation → Phoneme / Timing Extraction
→ Speech Timeline
                ↕
        Video Action Timeline
                ↓
        Synchronization Engine
                ↓
          Final Render
```

اگر متن می‌گوید «این محصول را ببینید…»، حرکت و Action باید با Timing صدا هماهنگ باشد.

> **نکته‌ی واقع‌بینانه:** Lip Sync و Viseme Mapping فقط وقتی معنا دارد که **انسان سخنگو** در تصویر باشد. ویدیوهای فعلی محصول (Wan 2.2 i2v روی عکس محصول) گوینده‌ی روی تصویر ندارند و نریشن روی تصویر پخش می‌شود. پس Lip Sync را باید به فازی موکول کرد که «ویدیوی با presenter» جزو محصول شود — نه الان.

---

### ۹.۵ — موتور تدوین و Post-Production

#### ایده‌ی اصلی

سیستم فقط نباید ویدیو تولید کند. باید بتواند **ویدیو را بفهمد، تحلیل کند، تدوین کند، اصلاح کند و برای انتشار آماده کند.**

دو نوع ورودی:

1. ویدیوهای تولیدشده توسط موتور AI خودمان
2. ویدیوهایی که کاربر آپلود می‌کند

> ⚠️ ورودی نوع ۲ یک **تصمیم استراتژیک** است، نه یک Feature. ببین [تصمیم ۱](#تصمیم-۱--آیا-ادیتور-ویدیوی-کاربر-جزو-این-محصول-است).

#### اصل معماری

بخش بزرگی از ادیت باید با **Engine کدنویسی‌شده** انجام شود، نه مدل AI:

```text
Input Video → Video Analyzer → Scene/Shot Detection → Timeline Builder
→ Editing Engine → Color Engine → Audio Engine → Subtitle Engine
→ Effects Engine → Quality Engine → Final Render
```

و فقط جایی که درک معنایی لازم است:

```text
Video → AI/Vision → Understanding → Editing Decision → Code-based Execution
```

نتیجه: سریع‌تر، ارزان‌تر، قابل‌کنترل‌تر.

#### Video Intelligence Engine

قبل از ادیت، ویدیو تحلیل شود:

Sceneها، Shotها، طول هر Shot، چهره‌ها، افراد، محصولات، اشیاء، حرکت دوربین، نور، Exposure، Contrast، Saturation، Blur، Noise، لرزش، سکوت، Speech، موسیقی، صدای پس‌زمینه، Clipping، نسبت تصویر، FPS، Resolution، Codec، Dynamic Range.

خروجی:

```json
{
  "duration": 184.5,
  "fps": 30,
  "resolution": "1920x1080",
  "scenes": 17,
  "faces": 2,
  "speech_segments": 43,
  "silence_segments": 18,
  "audio_quality": 72,
  "video_quality": 81,
  "stability": 64
}
```

#### Edit Decision List — ستون فقرات

هیچ عملیاتی مستقیم روی فایل انجام نشود. اول یک EDL ساخته شود:

```text
SOURCE → EDIT DECISION LIST → FINAL TIMELINE → RENDER
```

هر عملیات یک دستور:

```json
{ "type": "cut",   "start": 12.42, "end": 14.91 }
{ "type": "color", "exposure": 0.8, "contrast": 12 }
{ "type": "zoom",  "start": 35, "end": 42, "scale": 1.12 }
```

این معماری Preview، Undo/Redo و Non-Destructive Editing را ممکن می‌کند:

```text
Original → Edit Version 1 → Edit Version 2 → Edit Version 3
                    ↑ کاربر می‌تواند برگردد
```

**اصل فایل کاربر هرگز Overwrite نشود.**

#### موتورهای زیرمجموعه

| موتور | قابلیت‌ها |
|---|---|
| **Auto Cut** | سکوت طولانی، مکث اضافی، تکرار جمله، اشتباه گفتاری، شروع/پایان اضافی، فریم خراب، Shot تکراری |
| **Smart Jump Cut** | حذف «اممم… خب… یعنی…» و جمع‌کردن طبیعی فاصله‌ها |
| **Color** | Exposure، White balance، Contrast، Highlights، Shadows، Saturation، Vibrance، Gamma، Temperature، Tint، LUT، Skin-tone preservation |
| **Lighting Simulation** | تشخیص جهت نور روی چهره و اصلاح **موضعی** به‌جای روشن‌کردن کل تصویر |
| **Restoration** | Noise Reduction، Debanding، Deblocking، Sharpening، Deflickering، Frame interpolation، Upscaling |
| **Stabilization** | تفکیک لرزش از حرکت عمدی دوربین (Pan/Tilt/Zoom) تا حرکت طبیعی خراب نشود |
| **Audio Post** | Noise reduction، Hum removal، Echo، Voice isolation، Loudness normalization، Compression، EQ، De-esser، Limiter، Music ducking |
| **Subtitle** | Word-level timestamps، جمله‌بندی، Highlight، Animated captions، چند زبان، RTL، Safe area |
| **Smart Caption Positioning** | زیرنویس روی چهره/محصول/لوگو نیفتد — با Object Detection |
| **B-Roll** | تشخیص جای مناسب B-roll و تأمین از Media Library یا محتوای تولیدشده |
| **Auto Zoom** | Digital zoom روی جمله‌های مهم (100% → 112% → 100%) |
| **Multi-Camera** | انتخاب بهترین زاویه بر اساس Active Speaker و کیفیت شات |
| **Transition** | انتخاب بر اساس نوع محتوا، نه تصادفی |

#### Content-Type Profiles

کاربر لازم نیست تنظیمات را بفهمد. فقط انتخاب کند:

| پروفایل | مشخصات |
|---|---|
| YouTube | Long-form، Clean cuts، Natural pacing، Professional color، B-roll، Chapters |
| Shorts | Fast pacing، Jump cuts، Captions، Dynamic zoom |
| Instagram Reel | Vertical، Fast opening، Captions، Brand style |
| Podcast | Voice enhancement، Multi-camera، Speaker switching، Clips |

#### Brand Editing System

```text
Brand
├── Logo            ├── Intro
├── Colors          ├── Outro
├── Fonts           ├── Music
├── Caption Style   ├── Watermark
└── Editing Style
```

بعد: «این ویدیو رو با استایل برند من ادیت کن.»

#### Content Repurposing

```text
20 min Video → Long-form YouTube
             → 10 Short Clips
             → 5 Reels
             → Quotes
             → Captions
             → Thumbnail Suggestions
```

#### Media Library

هر کاربر یک Media Library داشته باشد: Videos، Images، Music، Voice، Logos، Brand Assets، B-Rolls، Projects، Exports.

و سیستم AI بتواند از همین Library برای تدوین استفاده کند.

#### Proxy Editing و Preview

```text
Original 4K → Proxy 720p → Timeline Editing → Final Render → Original 4K
```

کاربر نباید برای هر تغییر منتظر بماند:

```text
Timeline Change → Low Resolution Preview → User Approves → High Quality Render
```

Preview با 720p و bitrate پایین؛ Export نهایی با 1080p/4K.

#### Timeline Editor

پنل باید یک Timeline واقعی داشته باشد:

```text
VIDEO ──────────────────────────────────
       | Scene 1 | Scene 2 | Scene 3 |

AUDIO ──────────────────────────────────
       | Voice   | Music   | SFX       |

TEXT ───────────────────────────────────
       | Caption | Caption | Caption   |

B-ROLL ─────────────────────────────────
              | B-Roll |
```

کاربر بتواند Cut، Split، Move، Trim، Delete، Duplicate، Zoom، Crop، Rotate، Speed، Transition، Audio level، Caption و Overlay را انجام دهد.

**دو حالت:** *AI Mode* («خودت ادیتش کن») و *Manual + AI Mode* (کاربر Timeline را دستکاری می‌کند و AI کمک می‌کند: «این قسمت رو جذاب‌تر کن»، «اینجا B-roll اضافه کن»).

پس محصول هم برای مبتدی مناسب است، هم برای Editor حرفه‌ای.

#### QC نهایی

بعد از Render هم فایل مستقیم تحویل داده نشود:

```text
Final Render → Video QC → Audio QC → Sync QC
→ Black Frame Detection → Freeze Frame Detection
→ Corruption Detection → Subtitle QC → Final Score
```

#### اتصال به Video Generator

```text
AI Video Generator → 5 sec Segment → Video Intelligence
→ Consistency QC → Editing / Enhancement → Customer Preview
→ Approve → Next Segment
```

Generator و Editor دو سیستم **جدا ولی متصل**اند و از یک Editing Engine مشترک استفاده می‌کنند.

#### تکنولوژی

هسته‌ی Processing: Python + FFmpeg + OpenCV + NumPy + PyAV.
Frontend: Next.js/React/TypeScript. Backend: Django + DRF. Async: Celery + Redis.
Media: Object Storage. دیتابیس فقط Metadata، Project، Timeline، Job.

Workerهای تخصصی: GPU Worker، CPU Worker، Audio Worker، Render Worker، AI Worker.

#### میزان شدنی بودن

| دسته | موارد |
|---|---|
| ✅ **کاملاً شدنی با کد** | Cut، Trim، Merge، Resize، Crop، Rotate، Speed، Color correction، Audio normalization، Noise processing، Subtitle rendering، Watermark، Transitions، Proxy، Timeline، Rendering، Versioning، Export، Job management، QC فنی |
| 🔶 **شدنی با کد + AI** | تشخیص Scene/چهره/Object/Speech، حذف سکوت هوشمند، تشخیص بخش‌های مهم، انتخاب B-roll، Auto reframing، Smart captions، تشخیص کیفیت، ساخت Timeline خودکار |
| 🔴 **پیشرفته، ولی قابل پیاده‌سازی** | اصلاح خودکار مشکلات پیچیده‌ی تصویر، حفظ کامل Continuity، بازسازی بخش خراب، درک سبک شخص، تدوین بر اساس Retention، انتخاب بهترین Take، Multi-camera Director، هماهنگی دقیق Video/Voice |

> **استراتژی درست: از روز اول Premiere Pro نسازیم.** ترتیب چهارمرحله‌ای در [فاز ۲۳](#فاز-۲۳--editing-engine).

---

### ۹.۶ — ادیتور ایجنتیک

این شاید **مهم‌ترین تصمیم معماری کل پروژه** باشد.

#### اصل

> **مدل ارزان = مغز تصمیم‌گیرنده**
> **Computer Vision = چشم**
> **FFmpeg/OpenCV/Audio/Color = دست**
> **QC = بازرس**
> **مدل گران = متخصص تعمیرات سخت**

لازم نیست یک مدل گران را مجبور کنیم خودش ویدیو را پردازش کند. مدل فقط **تصمیم می‌گیرد چه ابزاری، کجا، با چه پارامتری اجرا شود.**

```text
                    VIDEO
                      ▼
              Video Understanding
                      ▼
              Cheap AI / LLM
             "Editing Director"
                      ▼
             Editing Plan / Commands
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
   FFmpeg Tools   OpenCV Tools   CV Tools
        └─────────────┼─────────────┘
                      ▼
                 Video Editor
                      ▼
                     QC
                 ┌────┴────┐
                 ▼         ▼
               PASS      REPAIR
```

#### Tool Registry

```text
VIDEO TOOLS
├── تحلیل:  analyze_video · detect_scene · detect_face · detect_object
│            detect_motion · detect_blur · detect_noise · detect_silence
├── برش:    cut · trim · merge · crop · resize · rotate · speed
├── رنگ:    exposure · brightness · contrast · saturation
│            color_balance · sharpen · denoise
├── حرکت:   stabilize · auto_reframe · smart_zoom
├── متن:    subtitle · caption · watermark · logo
├── صدا:    audio_cleanup · normalize_audio · remove_silence · music_ducking
└── خروجی:  b_roll · transition · render_preview · quality_check
```

#### مدل مستقیم به FFmpeg دسترسی ندارد

این را **انجام نمی‌دهیم**:

```text
LLM → arbitrary shell command
```

به‌جایش:

```text
LLM → Typed Tool API → Validation → Editing Engine → FFmpeg/OpenCV
```

مدل فقط اجازه دارد چنین چیزی بدهد:

```json
{
  "tool": "smart_zoom",
  "parameters": { "start": 10, "end": 15, "scale": 1.08 }
}
```

و Backend قبل از اجرا بررسی کند: پارامتر معتبر است؟ زمان داخل ویدیو است؟ مقدار Zoom مجاز است؟ فایل متعلق به همین Project است؟ عملیات خطرناک نیست؟

**این از نظر امنیت و پایداری الزامی است، نه اختیاری.**

#### حلقه‌ی Observe → Plan → Act → Verify

مدل بعد از هر عملیات دوباره نتیجه را ببیند:

```text
        ┌──────────────────────┐
        ▼                      │
     OBSERVE                   │
        ↓                      │
      PLAN                     │
        ↓                      │
       ACT                     │
        ↓                      │
      VERIFY ───── FAIL ───────┘
        │
       PASS
        ↓
      NEXT
```

**این از صرفاً «LLM + FFmpeg» خیلی قوی‌تر است.**

#### نمونه — ویدیوی AI خودمان

مدل ویدیو یک Segment ۵ ثانیه‌ای تولید کرده. Computer Vision گزارش می‌دهد:

```text
Lighting       72
Sharpness      91
Face           94
Object         88
Motion         61
Temporal       57
Continuity     63
```

مدل ارزان این گزارش را می‌بیند و تصمیم می‌گیرد:

> Motion و Temporal مشکل دارند؛ Color مشکل ندارد.

پس **فوراً regenerate نمی‌کند**. اول:

```text
stabilize() → deflicker() → motion_smoothing() → QC دوباره
```

و فقط اگر هنوز خراب بود → AI Regeneration.

#### نمونه — ویدیوی خام مشتری

```text
UPLOAD → ANALYZE → CHEAP LLM → EDIT PLAN → TOOLS
→ PREVIEW → QC → REPAIR → FINAL RENDER
```

مشتری لازم نیست بداند پشت صحنه FFmpeg یا OpenCV هست. برای او فقط یک دکمه است: **Auto Edit**.

نمونه‌ی یک Plan برای Reel:

```text
analyze_video → detect_scenes → detect_silence → remove_silence
→ auto_reframe(9:16) → smart_zoom → generate_captions
→ caption_style("reels") → audio_cleanup → color_correct
→ quality_check → render
```

#### چهار Mode

| Mode | رفتار |
|---|---|
| **Manual** | کاربر خودش دستور می‌دهد |
| **Assisted** | سیستم پیشنهاد می‌دهد: «۱۴ سکوت طولانی پیدا شد. حذف شوند؟» |
| **Auto** | سیستم خودش تصمیم می‌گیرد |
| **Director** | کاربر فقط هدف را می‌گوید: «مثل یک YouTuber حرفه‌ای ادیتش کن، طبیعی باشه و افکت زیاد نداشته باشه» |

#### یادگیری سبک شخصی

اگر کاربر همیشه Saturation را پایین می‌آورد، Caption را بالا می‌گذارد، Zoom را ۱۰۸٪ می‌کند و سکوت بیش از ۰.۷ ثانیه را حذف می‌کند — سیستم این را به یک **Personal Editing Profile** تبدیل کند.

دفعه‌ی بعد: «مثل همیشه ادیت کن.»

---

### ۹.۷ — Omnichannel Communication

نباید برای هر شبکه یک سیستم جدا و درهم بسازیم.

```text
                 Communication Core
                        │
       ┌────────────────┼────────────────┐
       ▼                ▼                ▼
   Messaging         Social           External
       │                │                │
   WhatsApp         Instagram        Public API
   Telegram         Facebook         Webhook
   SMS              ...
   Website
```

هر سرویس Adapter مستقل خودش را داشته باشد (`WhatsAppAdapter`، `TelegramAdapter`، …) ولی همه به **یک Interface مشترک** وصل باشند.

#### Inbox واحد

```text
All Messages
 ├── WhatsApp   ├── Website
 ├── Telegram   ├── SMS
 ├── Instagram  └── External API
```

کاربر بتواند: پیام را ببیند، پاسخ دهد، Conversation را Assign کند، Tag کند، وضعیت را تغییر دهد، Customer Profile و تاریخچه را ببیند، از AI پیشنهاد پاسخ بگیرد، پاسخ خودکار فعال کند.

#### API عمومی

```http
POST /api/v1/projects
POST /api/v1/projects/{id}/upload
POST /api/v1/projects/{id}/analyze
POST /api/v1/projects/{id}/auto-edit
POST /api/v1/projects/{id}/render
GET  /api/v1/projects/{id}/status
GET  /api/v1/projects/{id}/export
```

تا شرکت‌های دیگر بتوانند سیستم خودشان را وصل کنند یا Editor ما را داخل محصول خودشان استفاده کنند.

---

### ۹.۸ — Product Analytics و حلقه‌ی یادگیری

#### مشکل فعلی

Dashboard می‌گوید «۱۲۰ درخواست AI». این برای Product Analytics کافی نیست.

#### Funnel واقعی

هر کار مهم کاربر ثبت شود:

```text
Login → Create Campaign → Generate Content → Preview
→ Approve → Publish → Result
```

و برای هر مرحله Conversion داشته باشیم:

```text
1000 users
 ↓ 700 create content
 ↓ 500 generate
 ↓ 420 approve
 ↓ 350 publish
 ↓ 180 return
```

اینجا دقیقاً می‌فهمیم مشکل محصول کجاست.

#### Customer Analytics

چند مشتری فعال؟ چند نفر Trial؟ چند نفر تبدیل شدند؟ چند نفر ریزش کردند؟ **چرا** ریزش کردند؟

#### حلقه‌ی بسته

```text
Content → Publishing → Performance Data → Analytics
→ AI Analysis → Recommendation → New Content
```

سیستم بتواند بفهمد:

```text
Video A  CTR: 2.1%
Video B  CTR: 5.8%
Video C  CTR: 1.9%
```

و نتیجه بگیرد: کدام Hook بهتر است، کدام طول ویدیو، کدام Thumbnail، کدام ساعت انتشار، کدام CTA — و تولید بعدی را بر اساس آن تغییر دهد.

**پیش‌نیاز:** دریافت Performance Data از پلتفرم‌ها. بدون این، حلقه باز می‌ماند ([نقص ۷](#نقص-۷--حلقهی-یادگیری-بسته-نیست)).

#### Dashboard واقعی

Dashboard باید از «صفحه‌ی نمایش اطلاعات» به **Product Command Center** تبدیل شود:

| دسته | معیارها |
|---|---|
| Business | Revenue، Active Subscriptions، MRR، Churn، New Customers، Conversion Rate |
| Content | Generated، Published، Failed Jobs، Pending Approval |
| AI | AI Requests، API Cost، Token Usage، Average Generation Time |
| GPU | Utilization، VRAM، Queue، Active Jobs، Failed Jobs |
| Customer | Active Stores، Support Tickets، Messages، Engagement |

---

### ۹.۹ — اشتراک، اعتبار و تضمین کیفیت

#### Payment Gateway — Provider-Based

معماری باید Provider-Based باشد تا بعداً Gateway بدون تغییر منطق Subscription عوض شود.

اجزای لازم:

```text
ایجاد Payment → Callback/Webhook → Verify Payment
→ تمدید خودکار Subscription
```

به‌علاوه: Grace Period، Failed Payment Handling، Invoice/Receipt، Transaction History، Refund، Upgrade/Downgrade، لغو Subscription، محدودیت مصرف بر اساس Plan، Audit Log کامل.

#### Credit Architecture

```text
Customer Credits
       ↓
   Generation
       ↓
      QC
   ┌───┴───┐
 PASS    FAIL
   ↓       ↓
Consume  Refund
Credit   Credit
```

اعتبار مشتری فقط وقتی مصرف شود که عملیات **واقعاً موفق** بوده.

> زیرساخت رزرو/commit/release در `apps/billing/services.py` وجود دارد. کاری که مانده: وصل‌کردنش به Quality Score و Credit model.

#### وقتی مشتری کیفیت را نپسندید

| حالت | رفتار |
|---|---|
| **A — Regenerate** | همان Segment دوباره ساخته شود |
| **B — Change Style** | Camera / Lighting / Motion / Character / Prompt عوض شود |
| **C — Quality Guarantee** | اگر بعد از چند تلاش Threshold نگرفت: «Generation Failed — Credit Returned» |

برای پلن‌های Premium می‌توان **Quality Guarantee** رسمی تعریف کرد. این از نظر اعتماد مشتری بسیار قدرتمند است.

---

### ۹.۱۰ — چندکاربره و نقش‌ها

مدل Membership لازم است:

```text
Store
  ├── Owner
  ├── Admin
  ├── Marketing
  ├── Content Manager
  ├── Support
  └── Viewer
```

هر Role Permission مستقل:

```text
Owner            Marketing         Support
 ├── Billing      ├── Campaign      └── Conversations
 ├── Users        ├── Analytics
 ├── Content      └── Content
 └── Settings
```

---

### ۹.۱۱ — مارکتینگ، پشتیبانی و GTM

این را نباید بعداً به محصول اضافه کنیم. سه سیستم جدا:

**Customer Acquisition** — Landing Page، Demo، Free Trial، Lead Capture، Campaign، Referral، Affiliate، کد تخفیف، Sales Funnel.

**Customer Lifecycle**

```text
Lead → Customer → Onboarding → Support → Retention
```

**Marketing Intelligence** — سیستم باید بفهمد کدام Campaign، کدام Channel، کدام محتوا، کدام Plan و کدام نوع Customer به مشتری واقعی تبدیل شده است.

---

## ۱۰. تصمیم‌های باز

این‌ها را کد نمی‌تواند جواب بدهد. باید تصمیم گرفته شود.

### تصمیم ۱ — آیا ادیتور ویدیوی کاربر جزو این محصول است؟

محصول فعلی ICP مشخصی دارد: **صاحب فروشگاه آنلاین**. مدل مالی، سه پکیج، و کل ارائه روی همین بسته شده.

ولی موتور تدوین ([۹.۵](#۹۵--موتور-تدوین-و-post-production)) مخاطب دیگری را هدف می‌گیرد: یوتیوبر، تولیدکننده‌ی محتوا، اینفلوئنسر، مدرس، پادکستر، آژانس تبلیغاتی.

این‌ها **بازار متفاوت، قیمت‌گذاری متفاوت، رقبای متفاوت** دارند.

| گزینه | یعنی |
|---|---|
| **الف** | موتور تدوین فقط داخلی باشد — برای بهتر کردن ویدیوی خودمان. ICP عوض نمی‌شود. |
| **ب** | ادیتور به‌عنوان قابلیت جانبی به همان فروشگاه‌دارها داده شود (ویدیوی موبایلی خودشان را حرفه‌ای کند). |
| **ج** | ادیتور محصول دوم و مستقل شود، با ICP و قیمت خودش. |

**پیشنهاد:** الف در فاز اول (چون موتورش برای QC و تعمیر لازم است)، ب بعد از تثبیت، ج فقط اگر داده‌ی بازار پشتیبانی کند.

### تصمیم ۲ — LLM روی GPU یا API؟

اگر متن و تحلیل به API برود ([۸.۴](#۸۴--ai-gateway))، GPU آزاد می‌شود و مدل ظرفیت واقعی می‌شود. ولی:

- قول «داده‌ی شما پیش ما می‌ماند» باید بازنویسی شود، یا حالت Local Only واقعاً پیاده شود.
- هزینه‌ی متغیر هر مشتری بالا می‌رود و باید در `data.json` وارد شود.

**پیشنهاد:** Hybrid با انتخاب فروشگاه — و اثر هزینه‌اش صریح در مدل مالی.

### تصمیم ۳ — پرداخت اول یا کیفیت اول؟

**پیشنهاد:** کیفیت اول، ولی نه به قیمت بی‌نهایت. تا ~۲۰ مشتری اول، فعال‌سازی دستی اشتراک قابل تحمل است؛ **دیپلوی و دیتابیس** قابل تعویق نیستند.

ترتیب: بنچمارک → زیرساخت → کیفیت تولید → پرداخت → بقیه.

### تصمیم ۴ — سخت‌افزار

با شواهد [نقص ۵](#نقص-۵--مدل-روی-سختافزار-جا-نمیشود)، دو RTX 3060 12GB برای اجرای همزمان qwq:32b و Wan 2.2 کافی نیست.

گزینه‌ها: کارت با VRAM بیشتر / مدل کوچک‌تر برای reasoning / انتقال reasoning به API / تفکیک نقش کارت‌ها (یکی LLM، یکی رندر).

این تصمیم باید **بعد از بنچمارک فاز ۰.۵** گرفته شود، نه قبلش.

---

## ۱۱. رودمپ دوره‌ی دوم

دوره‌ی اول (فاز ۰ تا ۱۷، بخش ۵) محصول را ساخت. دوره‌ی دوم آن را به یک پلتفرم قابل‌فروش تبدیل می‌کند.

### قوانین ثابت این دوره

همه‌ی قوانین بخش ۶ برقرار است، به‌علاوه‌ی این چهار:

1. **هیچ عددی از حدس نیاید.** هر عدد ظرفیت/زمان/هزینه باید اندازه‌گیری‌شده باشد و منبعش در `دیتا/0-منبع/data.json` ثبت شود.
2. **هیچ Business Logic مستقیم API Call نزند.** همه از AI Gateway رد شوند.
3. **مدل هرگز دسترسی مستقیم به shell/FFmpeg نگیرد.** فقط Typed Tool API با اعتبارسنجی.
4. **اعتبار مشتری فقط بعد از موفقیت واقعی مصرف شود.** شکست = Refund.

---

### 🚪 فاز ۰.۵ — بنچمارک واقعی (دروازه)

- [ ] **تا این فاز تمام نشود، هیچ فاز دیگری شروع نمی‌شود.**

این همان فاز ۰.۵ دوره‌ی اول است که هرگز اجرا نشد. نقص‌های ۴، ۵، ۶ و ۱۴ فقط اینجا حل می‌شوند.

**کار:**

1. یک تیزر واقعی end-to-end: محصول واقعی → Qwen3-VL → QwQ → FLUX → Wan 2.2 (۵ ثانیه) → فریم آخر → Wan 2.2 (۵ ثانیه بعدی) → FFmpeg → صدا → تیزر ۱۰ ثانیه‌ای نهایی.
2. برای هر مدل و Resolution اندازه‌گیری و ثبت شود:
   ```text
   Generation Time · VRAM · RAM · CPU
   Model Load · Model Swap · Encoding · QC · Retry Rate
   ```
3. اندازه‌گیری زمان واقعی سواپ Ollama↔ComfyUI روی یک کارت.
4. تصمیم سخت‌افزار ([تصمیم ۴](#تصمیم-۴--سختافزار)) بر اساس همین اعداد.

**DoD:**

- گزارش بنچمارک با اعداد واقعی موجود است.
- `data.json` بخش `render` با اعداد اندازه‌گیری‌شده جایگزین شده و `source` از `owner` به `measured` تغییر کرده.
- مدل ظرفیت `model.py` زمان LLM و Model Swap را در فرمول دارد ([۸.۵](#۸۵--hardware-aware-scheduling)).
- لیست `gaps` به‌روز شده.
- ادعای «چند دقیقه» در `customer_value.faq` با عدد واقعی جایگزین شده.
- آستانه‌های Quality Score ([۹.۲](#quality-score)) با خروجی واقعی کالیبره شده‌اند.
- اگر کیفیت خروجی قابل‌فروش نبود، **همین‌جا** pipeline/مدل اصلاح می‌شود — نه بعد از یک ماه کدنویسی.

---

### فاز ۱۸ — Production Foundation

مرجع: [۸.۲](#۸۲--دیتابیس-و-ذخیرهسازی) · [۸.۳](#۸۳--زیرساخت-production) · [۸.۴](#۸۴--ai-gateway) · [۸.۷](#۸۷--data-governance-و-privacy)

- [ ] PostgreSQL به‌عنوان دیتابیس Production (SQLite برای Development می‌ماند)
- [ ] Object Storage جدا از دیتابیس — دیتابیس فقط Metadata
- [ ] Dockerfile + docker-compose + Nginx config
- [ ] Production settings، Secrets Management، Logging ساختاریافته، Monitoring
- [ ] اسکریپت Backup و مستند Deployment
- [ ] **AI Gateway** — هیچ Business Logic مستقیم API نزند
- [ ] **Data Policy Layer** — `ModelProvider` per-store قابل override، سه حالت `Local Only` / `Approved External` / `Hybrid`
- [ ] اصلاح ادعای Privacy در `data.json` و سایت متناسب با واقعیت edge-tts

**DoD:** کل استک روی یک سرور تمیز با `docker compose up` بالا می‌آید، بدون هیچ وابستگی به سیستم شخصی. فروشگاهی که `Local Only` انتخاب کند، Jobش در نبود مدل محلی **شفاف fail شود** — نه اینکه بی‌سروصدا به API بیرونی برود.

---

### فاز ۱۹ — Core Product

مرجع: [۹.۹](#۹۹--اشتراک-اعتبار-و-تضمین-کیفیت) · [۹.۱۰](#۹۱۰--چندکاربره-و-نقشها)

- [ ] Payment Gateway با معماری Provider-Based (ایجاد Payment → Callback/Webhook → Verify → تمدید خودکار)
- [ ] Grace Period، Failed Payment، Invoice، Transaction History، Refund، Upgrade/Downgrade، لغو، Audit Log
- [ ] **Credit Architecture** — PASS مصرف می‌کند، FAIL برمی‌گرداند
- [ ] Registration با حفظ `?plan=` تا انتهای مسیر
- [ ] Onboarding
- [ ] Multi-user Store — Owner / Admin / Marketing / Content Manager / Support / Viewer با Permission مستقل
- [ ] فرم تماس واقعی: Form + Validation + API + DB + Notification + Lead Record + Admin Inbox

**DoD:** یک کاربر از صفحه‌ی قیمت سایت تا فروشگاه فعال با اشتراک پرداخت‌شده می‌رسد، **بدون هیچ دخالت دستی ادمین**.

---

### فاز ۲۰ — Generation Pipeline

مرجع: [۹.۱](#۹۱--تولید-تدریجی-ویدیو) · [۸.۵](#۸۵--hardware-aware-scheduling) · [۸.۶](#۸۶--async-و-real-time)

- [ ] تولید تدریجی Segment ۵ ثانیه‌ای با Preview بعد از هر قطعه
- [ ] **Scene State** ساختاریافته (Characters/Objects/Location/Lighting/Camera/Clothing/Colors/Action) علاوه بر فریم آخر
- [ ] دو Mode: **Safe** (تأیید هر Segment) و **Auto** (فقط زیر Threshold متوقف شود)
- [ ] Job State Machine کامل: `QUEUED → PROCESSING → PREVIEW → WAITING_APPROVAL → APPROVED → RENDERING → QC → COMPLETED` + `FAILED/CANCELLED`
- [ ] Cancel واقعی: Worker Stop → Cleanup → GPU Release → Credit Refund
- [ ] Hardware Profiler + Smart Scheduler (CPU/GPU per task)
- [ ] WebSocket/SSE به‌جای Polling

**DoD:** کاربر ۵ ثانیه‌ی اول را زیر یک دقیقه‌ی مفید می‌بیند و می‌تواند رد کند — بدون اینکه GPU برای ۴۰ ثانیه‌ی بعدی مصرف شده باشد.

---

### فاز ۲۱ — AI Quality Engine

مرجع: [۹.۲](#۹۲--کنترل-کیفیت-ویدیو) · [۹.۳](#۹۳--موتور-تعمیر-سهسطحی)

**این مزیت فنی اصلی محصول است.**

- [ ] **Prompt Compiler** — تقویت خودکار Prompt با Scene State و قیدهای پیوستگی
- [ ] **Vision QC** — Temporal Consistency، Object Consistency، Face Consistency، Motion Analysis، Physics، Camera، Artifact Detection
- [ ] **Quality Score** با آستانه‌های کالیبره‌شده روی بنچمارک فاز ۰.۵
- [ ] **تعمیر سه‌سطحی:** کد (FFmpeg/OpenCV/Color/DSP) → Computer Vision (اصلاح موضعی یک ناحیه‌ی کوچک، مثل انگشت خراب) → AI Regeneration
- [ ] قانون: فقط Segment خراب بازتولید شود، هرگز کل ویدیو
- [ ] **کنترل عوض‌نشدن محصول** — Object Consistency با مرجع عکس واقعی محصول از دیتابیس
- [ ] عکس واقعی محصول در انتهای پست/ویدیو درج شود

**DoD:** یک Segment با نقص عمدی (نور بد / لرزش / Flicker) بدون مصرف دوباره‌ی GPU با کد اصلاح می‌شود؛ یک Segment با تغییر هویت شخصیت، regenerate می‌شود. هر دو در تست خودکار.

---

### فاز ۲۲ — Audio Engine

مرجع: [۹.۴](#۹۴--موتور-صدا)

- [ ] Voice Engine چند-Provider (Local TTS / Cloud TTS / Custom) با انتخاب بر اساس زبان، سبک، هزینه و **Privacy Policy فروشگاه**
- [ ] Text Normalizer + Pronunciation Engine (نام برند، انگلیسی داخل فارسی، اعداد)
- [ ] Voice Profile (Language/Gender/Age/Accent/Rate/Pitch/Emotion/Energy/Pause)
- [ ] **Audio QC** — Pronunciation، Pauses، Rate، Pitch، Loudness، Clipping، Noise، Robotic Artifacts
- [ ] Phoneme/Timing Extraction و Synchronization Engine

> **Lip Sync عمداً اینجا نیست.** ویدیوهای فعلی گوینده‌ی روی تصویر ندارند. فقط اگر «ویدیو با presenter» وارد محصول شود، Lip Sync و Viseme Mapping فاز جدا می‌گیرند.

**DoD:** صدای تولیدشده قبل از Final Render نمره می‌گیرد و زیر آستانه دوباره تولید می‌شود؛ حالت `Local Only` واقعاً بدون اینترنت کار می‌کند.

---

### فاز ۲۳ — Editing Engine

مرجع: [۹.۵](#۹۵--موتور-تدوین-و-post-production) · [۹.۶](#۹۶--ادیتور-ایجنتیک)

چهار مرحله. **از روز اول Premiere Pro نمی‌سازیم.**

- [ ] **۲۳.۱ — هسته:** Upload → Analyze → Cut → Audio → Color → Subtitle → Export، بر پایه‌ی **Edit Decision List** و Non-Destructive Editing
- [ ] **۲۳.۲ — خودکار:** Auto Cut، Smart Jump Cut، Smart Zoom، B-Roll، Stabilization، Smart Caption Positioning، QC نهایی
- [ ] **۲۳.۳ — ایجنتیک:** Tool Registry با Typed Tool API + اعتبارسنجی، مدل ارزان به‌عنوان Editing Director، حلقه‌ی `Observe → Plan → Act → Verify`، چهار Mode، Content-Type Profiles، Brand Profile، Media Library، Personal Editing Style، Content Repurposing
- [ ] **۲۳.۴ — حرفه‌ای:** Timeline چندترکه، Proxy Editing، Advanced Effects، Public API

**DoD هر مرحله:** خروجی روی ویدیوی واقعی تست شود و EDL قابل Undo باشد. مدل هرگز به shell دسترسی نداشته باشد.

> ⚠️ **پیش‌نیاز تصمیم:** ورودی «ویدیوی آپلودی کاربر» ICP را عوض می‌کند. [تصمیم ۱](#تصمیم-۱--آیا-ادیتور-ویدیوی-کاربر-جزو-این-محصول-است) باید قبل از ۲۳.۴ گرفته شود.

---

### فاز ۲۴ — Omnichannel

مرجع: [۹.۷](#۹۷--omnichannel-communication)

- [ ] Communication Core با Adapter مستقل برای هر کانال (WhatsApp / Telegram / Instagram / SMS / Website / API)
- [ ] Inbox واحد با Assign، Tag، وضعیت، Customer Profile، تاریخچه
- [ ] پیشنهاد پاسخ AI و پاسخ خودکار
- [ ] API عمومی برای اتصال سیستم‌های بیرونی

**DoD:** دو کانال واقعی وصل شوند و هر دو از یک Inbox مدیریت شوند.

---

### فاز ۲۵ — Learning Engine

مرجع: [۹.۸](#۹۸--product-analytics-و-حلقهی-یادگیری)

**اینجا حلقه‌ی فلسفه‌ی محصول (بخش ۱) بسته می‌شود.**

- [ ] دریافت Performance Data از پلتفرم‌ها (بازدید، ریچ، CTR، Engagement)
- [ ] Product Analytics: Funnel واقعی `Login → Campaign → Generate → Preview → Approve → Publish → Result` با Conversion هر مرحله
- [ ] Customer Analytics: Active، Trial، Converted، Churn — و **چرا** Churn
- [ ] Content Scoring و Recommendation Engine
- [ ] Closed-Loop: نتیجه‌ی محتوای قبلی روی تولید بعدی اثر بگذارد
- [ ] Dashboard به Product Command Center تبدیل شود (Business / Content / AI / GPU / Customer)

**DoD:** سیستم بتواند بگوید کدام Hook، کدام طول ویدیو و کدام ساعت انتشار بهتر جواب داده — با داده‌ی واقعی، نه ساختگی.

---

### فاز ۲۶ — GTM

مرجع: [۹.۱۱](#۹۱۱--مارکتینگ-پشتیبانی-و-gtm)

- [ ] CRM، Referral، Affiliate، کد تخفیف، Campaign
- [ ] Lead → Customer → Onboarding → Support → Retention
- [ ] Marketing Intelligence: کدام Campaign/Channel/محتوا/Plan مشتری آورد

**DoD:** داشبورد بگوید هر مشتری از کجا آمده و کدام کانال ROI بهتری داشته.

---

### ترتیب و وابستگی

```text
        ┌─────────────────────────┐
        │  فاز ۰.۵ — بنچمارک     │  ← دروازه، هیچ چیز قبلش شروع نمی‌شود
        └────────────┬────────────┘
                     │
        ┌────────────┴────────────┐
        ▼                         ▼
   مسیر زیرساخت              مسیر کیفیت
   ۱۸ Production            ۲۰ Pipeline
   ۱۹ Core Product          ۲۱ Quality Engine
                            ۲۲ Audio Engine
        └────────────┬────────────┘
                     ▼
              ۲۳ Editing Engine
                     ▼
              ۲۴ Omnichannel
                     ▼
              ۲۵ Learning Engine
                     ▼
                 ۲۶ GTM
```

دو مسیر بعد از فاز ۰.۵ **می‌توانند موازی بروند**. فاز ۲۳ به موتور QC فاز ۲۱ وابسته است (تعمیر سه‌سطحی از همان ابزارها استفاده می‌کند). فاز ۲۵ به فاز ۲۴ وابسته است (بدون اتصال پلتفرم، داده‌ی عملکرد نمی‌آید).

---

### تعریف محصول نهایی

هدف نهایی نباید «یک ابزار تولید عکس و ویدیو با AI» باشد.

```text
Business
   ↓ Strategy
   ↓ Content Planning
   ↓ AI Generation
   ↓ Video / Image / Voice
   ↓ Quality Control
   ↓ Approval
   ↓ Publishing
   ↓ Omnichannel Communication
   ↓ Analytics
   ↓ AI Learning
   ↓ Better Strategy
   ↓ Better Content
```

در این معماری AI فقط تولیدکننده نیست؛ یک سیستم کامل برای **برنامه‌ریزی، تولید، کنترل، انتشار، ارتباط و یادگیری** است.

یعنی یک **AI Content Operating System**.

و مسیر رسیدن به آن این است:

> **ساخت یک Pipeline قابل‌اندازه‌گیری، قابل‌کنترل و قابل‌اعتماد برای تولید محتوای باکیفیت — خصوصاً Video و Voice.**

اگر این دو واقعاً عالی شوند، بقیه‌ی لایه‌ها روی آن سوار می‌شوند.

---

# UPMARKET — MASTER DEVELOPMENT SPECIFICATION

## 0. ROLE AND MISSION

You are the lead software architect, senior backend engineer, senior frontend engineer, AI engineer, infrastructure engineer, and QA engineer responsible for building a production-quality application called **UpMaket**.

You are not building a simple AI content generator.

You are building an **AI Sales & Marketing Employee for online stores**.

The long-term goal is to create a system where a store owner can create a store, enter store information, add products, and then delegate a large part of sales, marketing, content production, customer support, and content publishing to AI.

The application must be designed as a serious, modular, extensible product.

Do not create a toy project.

Do not create a demo that only looks functional.

Do not replace important functionality with fake/mock implementations unless the functionality is explicitly marked as a temporary development stub.

Every major feature must have:

* real backend implementation
* real frontend implementation
* persistent database state
* proper validation
* error handling
* logging
* testing
* documentation

The project must be developed incrementally.

Never attempt to generate the entire application in one step.

Work phase-by-phase.

Never silently skip a requirement.

Never implement future phases early unless required by architecture.

Before starting implementation, inspect the repository and existing project files.

If an existing implementation is present, preserve useful code and improve/refactor it rather than unnecessarily replacing the entire project.

---

# 1. PRODUCT VISION

UpMaket is an AI-powered platform for online stores and small businesses.

A store owner should eventually be able to:

1. Create a store.
2. Enter brand and business information.
3. Add products.
4. Upload product images.
5. Define product prices, variants, inventory, specifications, benefits, and descriptions.
6. Let AI understand the products.
7. Let AI analyze competitors and market positioning.
8. Let AI create marketing strategies.
9. Let AI act as a sales/support employee.
10. Let AI answer customer questions.
11. Let AI recommend products.
12. Let AI handle objections.
13. Let AI assist with or complete sales conversations.
14. Let AI generate advertising posters.
15. Let AI improve and edit product images.
16. Let AI create professional Instagram-ready product photos.
17. Let AI generate captions.
18. Let AI create advertising concepts.
19. Let AI write advertising video scripts.
20. Let AI generate the video in multiple 5-second segments.
21. Preserve visual continuity between video segments.
22. Use the last frame of one segment as the visual starting point for the next segment when appropriate.
23. Combine all video segments.
24. Generate voice-over.
25. Synchronize voice-over with the final video.
26. Allow the user to review, edit, regenerate, or approve generated content.
27. Publish approved content through an automation layer such as n8n.
28. Eventually collect performance data and use it to improve future marketing decisions.

The core philosophy is:

STORE DATA
→ PRODUCT KNOWLEDGE
→ MARKET INTELLIGENCE
→ AI STRATEGY
→ CONTENT
→ CUSTOMER CONVERSATION
→ SALE
→ PUBLISHING
→ ANALYTICS
→ LEARNING

---

# 2. CORE PRODUCT PRINCIPLE

Do not build UpMaket as a collection of unrelated AI tools.

The features must share a common business context.

The AI must understand:

* the store
* the brand
* the target audience
* the products
* pricing
* inventory
* product advantages
* product limitations
* competitors
* previous conversations
* previous content
* previous campaign results
* store policies
* shipping information
* return/refund rules
* brand tone
* visual identity

The AI should behave like a persistent employee with access to business knowledge, not like a stateless chatbot.

---

# 3. TARGET ARCHITECTURE

Use the following general architecture, but improve it where engineering judgment shows a better solution.

## Frontend

* React
* Vite
* TypeScript
* Tailwind CSS
* React Router
* Axios or equivalent HTTP client
* React Hook Form
* appropriate state management
* reusable UI component system

Do not create a giant monolithic component structure.

Use feature-oriented frontend architecture.

Suggested conceptual structure:

src/
app/
components/
features/
auth/
store/
products/
ai/
sales/
content/
image-studio/
video-studio/
campaigns/
publishing/
analytics/
pages/
services/
hooks/
types/
utils/
layouts/

Adjust the exact structure if a better scalable architecture is identified.

---

# 4. BACKEND

Use:

* Python
* Django
* Django REST Framework
* SQLite (Django default database — revised decision D2)
* Celery
* Redis
* Django Channels
* WebSocket support
* django-cors-headers
* python-dotenv or equivalent environment configuration

Do not put business logic inside Django views.

Use proper service-layer architecture.

Suggested conceptual structure:

backend/
manage.py
config/
apps/
accounts/
stores/
products/
customers/
orders/
ai/
content/
campaigns/
publishing/
analytics/
media/
services/
ai/
comfyui/
ollama/
video/
audio/
publishing/
tasks/
common/
tests/

The exact project structure may be improved if there is a strong engineering reason.

---

# 5. LOCAL AI INFRASTRUCTURE

The development environment already has the following local AI models.

## Ollama

Available models:

* qwen3-coder:30b
* qwen3-vl:30b
* qwq:32b

Use them according to task type.

### qwen3-vl:30b

Primary responsibilities:

* product image analysis
* visual understanding
* image comparison
* analysis of product photography
* extracting visual product characteristics
* analyzing reference images
* analyzing competitor visuals
* understanding generated images when validation is required

### qwq:32b

Primary responsibilities:

* reasoning
* strategic thinking
* marketing strategy
* product positioning
* customer objection analysis
* campaign ideas
* advertising concepts
* script generation
* structured planning
* decisions requiring deeper reasoning

### qwen3-coder:30b

Primary responsibilities:

* development assistance
* code-related AI functionality if such a feature is introduced
* technical reasoning where coding-specific capabilities are useful

Do not call these models randomly.

Create a central AI orchestration layer.

Do not hardcode model names throughout business logic.

The model configuration must be centralized and configurable.

---

# 6. COMFYUI INFRASTRUCTURE

ComfyUI is available locally and should be treated as a model execution engine.

Available models include:

* FLUX.1 [dev] FP8
* wan_2.2_i2v_high_noise_14B_fp8_scaled.safetensors
* wan_2.2_i2v_low_noise_14B_fp8_scaled.safetensors
* umt5_xxl_fp8_e4m3fn_scaled.safetensors
* wan_2.1_vae.safetensors
* lightx2v_12V_14B_480p_cfg_step_distill_rank64_bf16.safetensors

Do not assume that every model must be used for every request.

The system must create versioned ComfyUI workflows.

Do not hardcode giant ComfyUI workflow payloads directly inside Django views.

Create a dedicated ComfyUI integration layer.

The ComfyUI client must support:

* queue submission
* prompt/workflow submission
* job tracking
* result retrieval
* error handling
* timeout handling
* retry handling
* output file detection
* status polling and/or WebSocket handling
* workflow versioning
* metadata recording

The exact model/workflow usage must remain configurable.

---

# 7. VIDEO GENERATION REQUIREMENTS

Video generation is one of the most important features of UpMaket.

The system must support AI advertising videos longer than the supported generation duration of a single generation request.

The conceptual pipeline is:

User/Product
→ AI marketing analysis
→ video concept
→ script
→ scene breakdown
→ 5-second scene prompts
→ image/keyframe generation when required
→ Wan 2.2 I2V
→ 5-second segment
→ extract final frame
→ use final frame as input for next segment
→ generate next segment
→ repeat
→ concatenate all segments
→ add voice
→ finalize video

A typical 30-second video consists of:

Segment 1: 0–5 sec
Segment 2: 5–10 sec
Segment 3: 10–15 sec
Segment 4: 15–20 sec
Segment 5: 20–25 sec
Segment 6: 25–30 sec

However, do not hardcode exactly 30 seconds.

The architecture must support configurable durations.

---

# 8. VIDEO CONTINUITY

Continuity is critical.

The system must attempt to preserve:

* character identity
* product appearance
* colors
* environment
* camera perspective
* lighting
* scene style
* composition
* visual semantics
* motion continuity

The default continuity mechanism should be:

SEGMENT N
→ generated video
→ extract final frame
→ final frame becomes input/anchor for SEGMENT N+1

Do not automatically regenerate a completely unrelated FLUX image for every segment.

A new anchor image should only be generated when the next scene requires a major visual transition or the existing frame is unsuitable.

The AI scene planner must be able to indicate something such as:

scene_transition_type:

* CONTINUE
* TRANSITION
* NEW_SCENE

For CONTINUE:

use previous final frame.

For TRANSITION:

use the previous frame with an appropriate transition strategy.

For NEW_SCENE:

generate a new visual anchor when required.

The system must record exactly which frame and image were used for each segment.

---

# 9. VIDEO SEGMENT DATA MODEL

Each video segment should conceptually contain fields such as:

* campaign
* order/index
* duration
* scene description
* visual prompt
* motion prompt
* narration text
* transition type
* source image
* source frame
* generated video
* final frame
* generation status
* retry count
* generation metadata
* workflow version
* error message
* timestamps

The exact database design is up to the implementation.

---

# 10. VIDEO GENERATION JOB SYSTEM

Video generation must never run synchronously inside a normal HTTP request.

Use:

* Celery
* Redis
* persistent job records

The frontend must be able to show:

* queued
* analyzing
* preparing
* generating segment 1
* generating segment 2
* extracting frame
* concatenating
* generating voice
* mixing audio
* finalizing
* completed
* failed

The system must support retries.

A failed segment must not necessarily invalidate the entire campaign.

The job system must be designed so that generation can resume from the failed segment when possible.

Do not regenerate successful segments unnecessarily.

---

# 11. GPU CONCURRENCY

GPU-heavy AI generation must be treated as a scarce resource.

Never assume unlimited concurrency.

Implement a generation queue.

The system should allow configurable concurrency limits.

The initial deployment should support conservative GPU concurrency, potentially one heavy generation job at a time depending on actual hardware limitations.

Do not hardcode arbitrary concurrency without configuration.

Create a GPU/job configuration layer so concurrency can later be tuned.

---

# 12. PRODUCT DATA MODEL

The product system must be richer than a simple name and description.

A product should eventually support:

* name
* slug
* SKU
* description
* short description
* category
* brand
* price
* compare-at price if relevant
* currency
* stock quantity
* stock status
* product variants
* attributes
* specifications
* benefits
* features
* use cases
* target audience
* tags
* shipping information
* images
* videos
* marketing notes
* AI-generated insights
* AI-generated selling points
* AI-generated objections
* AI-generated positioning

Do not duplicate AI-generated information unnecessarily.

Store structured AI outputs separately where appropriate.

---

# 13. STORE MODEL

Each store should eventually contain:

* store name
* business type
* description
* target audience
* location/general market
* contact details
* brand voice
* tone
* preferred content style
* visual preferences
* colors
* logo
* social links
* shipping policy
* return policy
* refund policy
* payment information
* business rules
* working hours if needed
* AI preferences
* publishing preferences

A store must act as a tenant boundary.

A user must never be able to access another user's store data.

---

# 14. MULTI-TENANCY

UpMaket must be designed as a multi-store platform.

A user may eventually own or manage multiple stores.

Every store-owned resource must be correctly scoped.

Examples:

* products
* customers
* orders
* conversations
* campaigns
* images
* videos
* AI analyses
* generated assets
* analytics
* publishing jobs

Never rely solely on frontend filtering.

Authorization must be enforced on the backend.

---

# 15. AUTHENTICATION

Implement a production-quality authentication foundation.

Support:

* registration
* login
* logout
* token refresh
* protected APIs
* user profile
* store access control

Do not store secrets in source code.

Use environment variables.

---

# 16. AI ORCHESTRATION LAYER

Create a central AI abstraction.

Conceptually:

AIProvider
├── TextProvider
├── VisionProvider
├── ReasoningProvider
├── ImageProvider
├── VideoProvider
└── TTSProvider

The exact interfaces can be improved.

The rest of the application must not care whether the model is:

* Ollama
* ComfyUI
* another provider
* a future cloud provider

This is required for future extensibility.

---

# 17. STRUCTURED AI OUTPUTS

Whenever possible, AI outputs must be structured.

Do not rely on fragile natural-language parsing.

For example, product analysis should return structured data.

Example conceptual shape:

{
"summary": "...",
"target_audience": [],
"selling_points": [],
"objections": [],
"marketing_angles": [],
"recommended_tone": "...",
"content_ideas": []
}

Validate AI outputs.

If the model returns malformed JSON:

1. attempt controlled repair where safe
2. retry with a structured-output prompt
3. mark the request as failed if necessary

Do not silently accept corrupted AI data.

---

# 18. PROMPT MANAGEMENT

Prompts must not be scattered randomly throughout the codebase.

Create a prompt/version management system.

Each important AI capability should have:

* prompt identifier
* version
* system prompt
* task prompt
* expected schema
* model configuration
* temperature/configuration if supported
* metadata

Prompt changes must be traceable.

This will make future experimentation much easier.

---

# 19. PRODUCT ANALYSIS

When a store adds a product, UpMaket should eventually be able to analyze it.

Pipeline:

Product information
+
Product images
→ Qwen3-VL
→ visual analysis
→ QwQ
→ reasoning/strategy
→ structured product intelligence

The resulting intelligence should include:

* what the product is
* who should buy it
* why customers might buy it
* why customers might reject it
* strongest selling points
* potential objections
* possible marketing angles
* content opportunities
* suggested positioning
* recommended tone
* potential use cases

Do not present AI guesses as verified facts.

Clearly separate:

* user-provided facts
* AI inferences
* external research findings

---

# 20. COMPETITOR / MARKET ANALYSIS

UpMaket should support market and competitor research.

The architecture must allow external research to be added later.

Do not assume competitors are known purely from the product description.

When external research is used:

* record sources
* record timestamps
* distinguish observed facts from model-generated conclusions
* store research results separately
* do not fabricate competitor information

The AI should be able to generate a structured strategic summary.

For example:

* competitor positioning
* common messaging
* content patterns
* pricing observations where available
* common customer concerns
* content gaps
* differentiation opportunities

The actual web research implementation may be introduced as a separate phase.

---

# 21. AI SALES AGENT

This is a core feature, not an optional chatbot.

The long-term sales agent should be able to function as a digital sales/support employee.

It should understand:

* store
* products
* stock
* prices
* variants
* policies
* customer history
* conversation context

Potential flow:

CUSTOMER MESSAGE
→ INTENT DETECTION
→ RETRIEVE RELEVANT STORE/PRODUCT DATA
→ REASON
→ RESPOND
→ RECOMMEND
→ HANDLE OBJECTION
→ OFFER PURCHASE
→ CREATE ORDER/CART WHEN APPROPRIATE

The architecture must support:

* product questions
* comparison
* recommendations
* objections
* availability questions
* price questions
* shipping questions
* return/refund questions
* purchase intent
* order creation
* escalation to human

Never allow the AI to invent:

* prices
* inventory
* shipping guarantees
* policies
* product specifications

The AI must ground transactional information in actual database data.

---

# 22. HUMAN HANDOFF

Although the product aims for high automation, the architecture must support escalation.

The AI should be able to signal:

* low confidence
* policy-sensitive request
* unusual customer issue
* request for human assistance
* unsupported operation

Create a conversation state that supports:

* AI handling
* human handling
* escalated
* resolved

---

# 23. PRODUCT IMAGE STUDIO

Create an image-generation/editing subsystem.

Capabilities should eventually include:

1. image enhancement
2. background cleanup
3. background replacement
4. professional product photography
5. Instagram-ready product images
6. advertising compositions
7. lifestyle scenes
8. poster generation
9. visual variations

Pipeline:

PRODUCT DATA
+
REFERENCE IMAGE
→ Qwen3-VL ANALYSIS
→ QwQ CREATIVE DIRECTION
→ PROMPT
→ COMFYUI
→ FLUX
→ OUTPUT VALIDATION
→ ASSET STORAGE

Do not blindly trust generated images.

The system should support preview and regeneration.

---

# 24. PRODUCT IMAGE QUALITY

Generated product images must attempt to preserve the actual product.

Avoid accidentally changing:

* logos
* product type
* brand identity
* major shape
* color
* important physical characteristics

The system must distinguish between:

* product-preserving edit
* creative advertising composition

These are different tasks.

---

# 25. POSTER GENERATION

Poster generation should use real product context.

The poster pipeline should consider:

* product
* target audience
* campaign objective
* marketing angle
* visual style
* brand identity
* CTA

The system should support multiple concepts.

Example:

Poster concept A:

* premium
* minimal

Poster concept B:

* energetic
* sales-oriented

Poster concept C:

* lifestyle

The exact number of concepts must be configurable.

---

# 26. CAPTION GENERATION

The content system must generate captions appropriate for the destination.

At minimum:

* Instagram
* Telegram
* LinkedIn

The same product may need different writing for each platform.

The caption system should support:

* CTA
* tone
* audience
* campaign objective
* product benefits
* relevant hashtags where appropriate
* short/medium/long versions

Do not generate generic text disconnected from the product.

---

# 27. ADVERTISING VIDEO SCRIPT GENERATION

The system must create structured video scripts.

Each script should contain:

* overall concept
* target audience
* objective
* total duration
* scene list
* scene duration
* narration
* visual description
* motion description
* transition type
* CTA

Example conceptual scene:

Scene 1:
duration: 5
visual_prompt: ...
motion_prompt: ...
narration: ...
transition: CONTINUE

The actual schema should be formalized in the application.

---

# 28. VIDEO AUDIO / VOICE-OVER

The system must support natural-sounding voice generation.

The architecture should make the TTS system replaceable.

Possible implementations include:

* local TTS
* gTTS for an initial simple implementation
* a stronger local TTS model
* future voice-cloning providers/models

Do not hardwire the whole application to gTTS.

Create:

TTSProvider

The system must:

1. split narration into logical sections
2. synthesize audio
3. measure durations
4. align narration with scenes
5. concatenate audio
6. mix audio with video

Do not blindly overlay one audio file over the final video without timing consideration.

---

# 29. VIDEO + AUDIO FINALIZATION

Use FFmpeg for:

* concatenation
* trimming
* audio concatenation
* synchronization
* audio mixing
* codec normalization
* format conversion
* final output generation

The video pipeline must produce consistent final output.

Store technical metadata such as:

* width
* height
* FPS
* duration
* codec
* audio codec
* file size

---

# 30. GENERATED ASSET SYSTEM

All generated outputs must be represented as persistent assets.

Examples:

* product image
* poster
* caption
* script
* video segment
* final video
* audio
* campaign package

Do not simply write files to random directories without database records.

Each asset should have:

* owner/store
* asset type
* file path/reference
* metadata
* source
* generation job
* prompt version
* model
* creation time
* status
* parent asset where relevant

---

# 31. MEDIA STORAGE

Use a clean abstraction for media storage.

Do not spread filesystem paths across the codebase.

Create a storage service.

Development may use local media storage.

Production should be capable of moving to:

* S3-compatible storage
* object storage
* another provider

without rewriting business logic.

---

# 32. JOB SYSTEM

Create a generic AI/job system.

Possible jobs include:

* product_analysis
* competitor_analysis
* image_generation
* video_script_generation
* video_segment_generation
* frame_extraction
* video_concatenation
* voice_generation
* audio_mixing
* campaign_generation
* publishing

Each job should have:

* ID
* type
* state
* priority if needed
* progress
* current step
* error
* retry count
* timestamps
* related store
* related product/content/campaign

---

# 33. WEBSOCKETS

Use Django Channels or an equivalent WebSocket solution.

The frontend must eventually receive events such as:

job.created
job.queued
job.started
job.progress
job.segment_started
job.segment_completed
job.failed
job.completed

Do not force the frontend to constantly refresh pages.

Use polling as a fallback only where appropriate.

---

# 34. FRONTEND DASHBOARD

The dashboard should eventually include:

* store overview
* products
* AI insights
* conversations
* campaigns
* generated content
* jobs
* analytics
* publishing

The UI should prioritize clarity over visual complexity.

---

# 35. PRODUCT MANAGEMENT UI

Users need to be able to:

* create product
* edit product
* upload images
* remove images
* set price
* manage stock
* define variants
* inspect AI analysis
* regenerate AI analysis

---

# 36. AI CONTENT WORKSPACE

Create a unified content-generation workspace.

The user should be able to select something like:

* Poster
* Product Photo
* Caption
* Video
* Campaign

The system should reuse existing product intelligence.

Avoid making users repeatedly enter the same product information.

---

# 37. CAMPAIGN MODEL

A campaign should be capable of grouping:

* goal
* product(s)
* audience
* strategy
* poster
* product image
* captions
* video script
* video
* audio
* approval state
* publishing state
* analytics

Example:

Campaign
→ Strategy
→ Poster
→ Product Image
→ Caption
→ Video Script
→ Video
→ Voice
→ Approval
→ Publishing

---

# 38. APPROVAL FLOW

Users must be able to:

* preview
* edit
* regenerate
* approve
* reject
* archive

Each generated asset should support a status such as:

DRAFT
PROCESSING
READY
APPROVED
REJECTED
FAILED
PUBLISHED
ARCHIVED

Do not publish automatically unless explicitly approved or configured for automatic publishing.

---

# 39. N8N INTEGRATION

n8n should be treated as an external automation layer.

Do not build social platform integrations directly into every feature.

Use a publishing service.

UpMaket should be able to send an approved content package to n8n.

Example conceptual payload:

{
"store": {...},
"campaign": {...},
"content": {...},
"assets": [...],
"platform": "instagram"
}

n8n can then perform actual platform-specific workflows.

Build:

* webhook configuration
* secure authentication
* delivery status
* retries
* logging
* failure tracking

Do not assume every social platform API behaves the same way.

---

# 40. SECURITY

Security is mandatory.

Protect:

* user data
* store data
* product data
* customer data
* API secrets
* AI infrastructure credentials
* n8n webhook credentials
* media access

Implement:

* authentication
* authorization
* tenant isolation
* input validation
* file validation
* upload size limits
* safe filenames
* secure environment variables
* CSRF/CORS configuration
* rate limiting where appropriate
* API permission checks

Do not expose arbitrary filesystem paths.

Do not trust uploaded files.

---

# 41. ERROR HANDLING

Every external service must be treated as unreliable.

Services include:

* Ollama
* ComfyUI
* Redis
* SQLite (Django default database — revised decision D2)
* n8n
* TTS provider
* filesystem/object storage

Implement:

* timeouts
* retries
* exponential backoff where appropriate
* clear user-facing errors
* technical logs
* job failure states
* recovery behavior

Do not retry indefinitely.

---

# 42. OBSERVABILITY

Create structured logging.

Logs should contain useful context such as:

* request ID
* user ID
* store ID
* job ID
* model
* workflow
* duration
* result
* failure reason

Avoid logging secrets.

---

# 43. TESTING

Every important subsystem must have tests.

Backend:

* models
* serializers
* permissions
* API endpoints
* service layer
* AI orchestration
* jobs
* video pipeline
* media handling
* publishing integration

Frontend:

* important components
* forms
* API interactions
* critical flows

Integration tests should verify:

Store creation
→ product creation
→ image upload
→ AI analysis
→ content creation
→ job lifecycle

Do not consider compilation sufficient.

---

# 44. DEVELOPMENT PRINCIPLES

Follow these principles:

* clean architecture
* modularity
* DRY where useful
* clear interfaces
* typed data
* small services
* testable code
* explicit errors
* configuration-driven behavior
* no magic values
* no secret values in source
* no unnecessary duplication

Do not over-engineer everything.

Build what is required for the current phase while preserving future extensibility.

---

# 45. PHASED DEVELOPMENT PLAN

Implement exactly in phases.

Do NOT attempt all phases at once.

---

## PHASE 0 — REPOSITORY INSPECTION AND ARCHITECTURE

Do not implement major functionality yet.

Inspect the repository.

Identify:

* existing code
* existing configuration
* existing dependencies
* existing frontend
* existing backend
* existing infrastructure

Create:

docs/ARCHITECTURE.md
docs/AI_ARCHITECTURE.md
docs/VIDEO_PIPELINE.md
docs/DATABASE.md
docs/API.md
docs/ROADMAP.md
docs/DEVELOPMENT_RULES.md

Define:

* architecture
* domains
* data model
* service boundaries
* job architecture
* media architecture
* AI architecture

Identify risks.

Do not begin full implementation until architecture is documented.

---

# PHASE 1 — FOUNDATION

Build:

* Django project
* React project
* SQLite (Django default database — revised decision D2)
* Redis
* Celery
* environment configuration
* authentication
* base API
* base frontend shell
* logging
* development Docker configuration if appropriate
* database migrations
* test infrastructure

Definition of Done:

* backend starts
* frontend starts
* database works
* Redis works
* Celery works
* authentication works
* frontend connects to backend
* automated tests pass

---

# PHASE 2 — STORE MANAGEMENT

Build:

* users
* stores
* store profiles
* store settings
* branding information
* store policies
* tenant isolation

Frontend:

* store creation
* store settings
* dashboard

Definition of Done:

A user can create and manage a store securely.

---

# PHASE 3 — PRODUCT MANAGEMENT

Build:

* products
* categories
* variants
* inventory
* pricing
* product images
* product CRUD
* image upload

Definition of Done:

A store owner can completely manage a product catalog.

---

# PHASE 4 — AI INFRASTRUCTURE

Build:

* Ollama client
* AI abstraction
* model router
* qwen3-vl integration
* qwq integration
* qwen3-coder integration where required
* structured responses
* retries
* logging
* prompt versioning
* AI request records

Definition of Done:

The application can make real local Ollama requests through the abstraction layer.

---

# PHASE 5 — PRODUCT INTELLIGENCE

Build:

* product image analysis
* product text analysis
* selling point extraction
* audience analysis
* objections
* marketing angles
* positioning

Use:

qwen3-vl for visual understanding.

Use qwq for reasoning/strategy.

Definition of Done:

A real product can be analyzed and the structured result is stored and displayed.

---

# PHASE 6 — MARKET / COMPETITOR INTELLIGENCE

Build the research architecture.

Support external research as a dedicated service.

Keep research data separate from AI conclusions.

Store:

* sources
* timestamps
* extracted observations
* conclusions
* confidence/uncertainty where useful

Do not fabricate competitor data.

Definition of Done:

The system can produce a structured market/competitor analysis from real available research inputs.

---

# PHASE 7 — AI SALES AGENT

Build:

* customer model
* conversations
* messages
* AI response generation
* product retrieval
* product recommendation
* objection handling
* transactional grounding
* order/cart foundations
* human handoff

Definition of Done:

A test customer can ask real product questions and receive responses grounded in real store/product data.

---

# PHASE 8 — COMFYUI FOUNDATION

Build:

* ComfyUI client
* workflow abstraction
* workflow versioning
* queue tracking
* output retrieval
* status tracking
* error handling

Test actual ComfyUI communication.

Do not yet build the complete campaign pipeline.

Definition of Done:

The backend can submit and retrieve a real ComfyUI generation.

---

# PHASE 9 — IMAGE STUDIO

Build:

* image enhancement
* background replacement
* product scene generation
* Instagram-ready product image
* advertising poster generation

Use:

* Qwen3-VL
* QwQ
* FLUX through ComfyUI

Definition of Done:

A real product image can be transformed into useful marketing assets.

---

# PHASE 10 — CAPTION / CONTENT ENGINE

Build:

* campaign content generation
* Instagram captions
* Telegram captions
* LinkedIn captions
* CTA generation
* tone controls
* content variations

Definition of Done:

A real product and marketing objective produce platform-specific captions.

---

# PHASE 11 — VIDEO SCRIPT ENGINE

Build:

* video concept generation
* scene planning
* scene duration
* narration
* visual prompt
* motion prompt
* transition planning

The output must be structured for the video engine.

Definition of Done:

The system can generate a machine-readable multi-scene advertising video plan.

---

# PHASE 12 — VIDEO GENERATION ENGINE

This is a major engineering phase.

Build:

* video jobs
* segment generation
* 5-second generation architecture
* Wan 2.2 integration
* high-noise/low-noise workflow support where appropriate
* anchor image management
* final frame extraction
* continuity pipeline
* segment retry
* resumable generation
* concatenation

Pipeline:

Scene Plan
→ Segment 1
→ Image/Anchor
→ Wan
→ Video 1
→ Extract Last Frame
→ Segment 2
→ Wan
→ Video 2
→ Extract Last Frame
→ ...
→ FFmpeg
→ Final Video

Do not assume every segment requires FLUX.

Use existing final frames when possible.

Definition of Done:

A real multi-segment video can be generated and concatenated while maintaining reasonable visual continuity.

---

# PHASE 13 — VOICE / AUDIO

Build:

* TTS abstraction
* initial real TTS integration
* narration splitting
* duration measurement
* audio concatenation
* synchronization
* FFmpeg audio/video mixing

Definition of Done:

The final video contains synchronized narration.

---

# PHASE 14 — CAMPAIGN WORKSPACE

Build the unified experience:

Product
→ Strategy
→ Poster
→ Product Image
→ Caption
→ Video Script
→ Video
→ Voice
→ Final Asset

Build:

* campaign dashboard
* job progress
* previews
* regeneration
* edit
* approval

Definition of Done:

A user can create a campaign and manage the complete content lifecycle.

---

# PHASE 15 — N8N PUBLISHING

Build:

* publishing abstraction
* n8n integration
* secure webhook configuration
* payload generation
* publishing job
* delivery status
* retry
* errors

Definition of Done:

An approved campaign can be sent to n8n through a real integration.

---

# PHASE 16 — ANALYTICS

Build architecture for:

* campaign performance
* content performance
* customer interactions
* sales
* publishing results
* AI recommendations

Eventually use the data to improve future recommendations.

Do not fabricate analytics.

---

# PHASE 17 — PRODUCTION HARDENING

Review:

* security
* performance
* database indexes
* queue reliability
* GPU concurrency
* media cleanup
* monitoring
* error handling
* backups
* deployment
* environment management
* migrations
* logging
* testing
* documentation

---

# 46. API REQUIREMENTS

Use REST APIs with clear versioning.

Possible initial endpoints include:

POST /api/auth/register/
POST /api/auth/login/
POST /api/auth/refresh/

GET /api/stores/
POST /api/stores/
GET /api/stores/{id}/
PATCH /api/stores/{id}/

GET /api/products/
POST /api/products/
GET /api/products/{id}/
PATCH /api/products/{id}/
DELETE /api/products/{id}/

POST /api/products/{id}/analyze/

POST /api/ai/content/
POST /api/ai/image/
POST /api/ai/video/

GET /api/jobs/{id}/
GET /api/jobs/{id}/status/

GET /api/campaigns/
POST /api/campaigns/
GET /api/campaigns/{id}/

POST /api/campaigns/{id}/approve/
POST /api/campaigns/{id}/reject/

POST /api/publishing/
GET /api/publishing/{id}/

The exact endpoint design may be improved.

Do not create inconsistent APIs.

---

# 47. FRONTEND UX REQUIREMENTS

The interface should be simple enough for a non-technical store owner.

Avoid exposing unnecessary technical details.

The user should think in business concepts:

* Store
* Product
* Customer
* Campaign
* Content
* Sales
* Analytics

not:

* ComfyUI workflow
* Celery worker
* model checkpoint
* queue object

Technical information may exist in an advanced/debug area for developers, but not in the primary UX.

---

# 48. AI JOB PROGRESS UX

For long-running generation, show meaningful progress.

Example:

Analyzing product
✓

Creating marketing strategy
✓

Preparing video
✓

Generating Scene 1
✓

Generating Scene 2
●

Generating Scene 3
○

Finalizing video
○

Generating voice
○

Final output
○

Do not expose fake progress percentages.

Progress must be derived from actual job state.

---

# 49. REGENERATION

Users must be able to regenerate individual components when possible.

For example:

Regenerate:

* poster
* caption
* product image
* individual video segment
* voice

Do not regenerate the entire campaign unnecessarily.

For video:

if Segment 3 fails, allow the system to retry Segment 3 without re-running Segments 1 and 2 when possible.

---

# 50. COST / RESOURCE AWARENESS

The system runs on local AI infrastructure.

GPU and compute resources are limited.

Design around:

* queueing
* caching
* reuse
* resumability
* concurrency limits
* avoiding unnecessary generation

Do not repeatedly call an AI model when an existing result can be reused.

---

# 51. CONFIGURATION

All important infrastructure values must be configurable.

Examples:

OLLAMA_BASE_URL
OLLAMA_MODEL_REASONING
OLLAMA_MODEL_VISION
OLLAMA_MODEL_CODER

COMFYUI_BASE_URL

REDIS_URL
DATABASE_URL

N8N_WEBHOOK_URL

MEDIA_ROOT
MEDIA_URL

GPU_CONCURRENCY_LIMIT

VIDEO_SEGMENT_DURATION

TTS_PROVIDER

Do not hardcode local URLs such as localhost throughout application code.

---

# 52. DEBUG / DEVELOPMENT MODE

Create developer-friendly diagnostics.

A developer should be able to inspect:

* AI requests
* AI responses
* model used
* prompt version
* ComfyUI workflow
* generation job
* output files
* failure reason
* processing time

Never expose sensitive information to normal users.

---

# 53. DATABASE PRINCIPLES

Use normalized relational data where appropriate.

Avoid giant JSON fields as a substitute for proper schema design.

JSON fields may be used where flexibility is justified, especially for:

* AI metadata
* workflow metadata
* model-specific settings
* dynamic generation metadata

But core business entities must remain queryable relational data.

---

# 54. FILE NAMING

Generated files should use stable identifiers.

Never use raw user-provided filenames as trusted filesystem paths.

Use safe paths and IDs.

---

# 55. DATA LIFECYCLE

The system should support future cleanup of:

* failed temporary outputs
* obsolete intermediate frames
* obsolete generation artifacts
* expired temporary files

Do not delete useful source assets automatically.

---

# 56. IMPORTANT ENGINEERING RULES

RULE 1:
Do not build the entire application in one response.

RULE 2:
Do not generate huge amounts of code without testing.

RULE 3:
Do not pretend an integration works when it has not been tested.

RULE 4:
Do not replace real AI integration with fake responses.

RULE 5:
Do not hardcode model or workflow configuration.

RULE 6:
Do not put heavy generation in HTTP request handlers.

RULE 7:
Do not block Django while waiting for video generation.

RULE 8:
Do not regenerate successful video segments unnecessarily.

RULE 9:
Do not allow AI to invent transactional facts.

RULE 10:
Do not break existing working code without a reason.

RULE 11:
Do not move to the next phase until the current phase is verified.

RULE 12:
Document important architectural decisions.

RULE 13:
Every important service must have tests.

RULE 14:
Every external dependency must have failure handling.

RULE 15:
Prefer real working vertical slices over incomplete massive architecture.

---

# 57. HOW YOU MUST WORK

For each phase:

1. Inspect the current repository.
2. Read relevant documentation.
3. Determine what already exists.
4. Define exact implementation scope.
5. Implement only the current phase.
6. Run migrations where needed.
7. Run backend tests.
8. Run frontend tests/build.
9. Perform integration verification.
10. Fix discovered problems.
11. Update documentation.
12. Report the completed work.

Do not silently continue into the next phase.

---

# 58. PHASE COMPLETION CRITERIA

A phase is NOT complete merely because:

* the code compiles
* the server starts
* the frontend renders
* the endpoint returns 200
* a mocked response appears

A phase is complete only when the functionality actually works.

For example:

For Ollama:

The actual local model must be called.

For ComfyUI:

A real workflow must be submitted and a real output must be retrieved.

For video:

A real generated segment must be processed.

For TTS:

A real audio file must be generated.

For n8n:

A real test webhook must be successfully delivered.

---

# 59. WHEN SOMETHING IS UNKNOWN

Do not invent technical behavior.

If a model, checkpoint, API, ComfyUI node, workflow, or library behaves differently from assumptions:

1. inspect the available environment
2. inspect configuration
3. verify the actual installed version
4. adapt the implementation
5. document the difference

Do not fake compatibility.

---

# 60. HARDWARE / MODEL ASSUMPTIONS

The system is intended to use locally hosted models.

Do not design the application around paid cloud AI as the primary path.

However, maintain provider abstraction so cloud providers can be added later.

The application must remain usable with the currently installed local AI stack.

---

# 61. FUTURE EXTENSIBILITY

The architecture should eventually allow:

* multiple AI providers
* multiple image models
* multiple video models
* multiple TTS engines
* different social networks
* multiple stores per account
* team members
* permissions
* billing
* subscriptions
* analytics
* A/B testing
* automated campaigns
* learning from conversion data

Do not implement these prematurely.

Design for them without building unnecessary complexity.

---

# 62. THE FIRST PRACTICAL MILESTONE

Before building the complete AI employee, the project should establish a reliable end-to-end vertical slice.

The first meaningful AI vertical slice should eventually be:

CREATE STORE
→ CREATE PRODUCT
→ UPLOAD PRODUCT IMAGE
→ ANALYZE PRODUCT
→ CREATE MARKETING STRATEGY
→ GENERATE PRODUCT IMAGE
→ GENERATE CAPTION
→ DISPLAY RESULT

After this is stable, add:

VIDEO SCRIPT
→ VIDEO SEGMENTS
→ CONTINUITY
→ AUDIO
→ FINAL VIDEO

Then:

CAMPAIGN
→ APPROVAL
→ N8N PUBLISHING

---

# 63. REQUIRED FINAL PRODUCT EXPERIENCE

The intended final user journey is:

USER REGISTERS
↓
CREATES STORE
↓
ENTERS STORE INFORMATION
↓
ADDS PRODUCTS
↓
UPLOADS PRODUCT IMAGES
↓
AI UNDERSTANDS PRODUCTS
↓
AI ANALYZES MARKET / COMPETITION
↓
AI BUILDS PRODUCT INTELLIGENCE
↓
USER CREATES CAMPAIGN
↓
AI CREATES STRATEGY
↓
AI CREATES POSTER
↓
AI CREATES PROFESSIONAL PRODUCT IMAGE
↓
AI CREATES CAPTIONS
↓
AI WRITES VIDEO SCRIPT
↓
AI CREATES VIDEO SEGMENTS
↓
FINAL FRAME OF SEGMENT N
BECOMES INPUT/ANCHOR FOR SEGMENT N+1
↓
VIDEO SEGMENTS ARE COMBINED
↓
VOICE IS GENERATED
↓
VOICE + VIDEO ARE SYNCHRONIZED
↓
FINAL VIDEO
↓
USER REVIEWS CONTENT
↓
USER APPROVES
↓
N8N PUBLISHES
↓
PERFORMANCE IS TRACKED
↓
FUTURE AI DECISIONS IMPROVE

---

# 64. REQUIRED FILES / DOCUMENTATION

Maintain documentation throughout development.

At minimum:

docs/
ARCHITECTURE.md
AI_ARCHITECTURE.md
DATABASE.md
API.md
VIDEO_PIPELINE.md
MEDIA_PIPELINE.md
JOB_SYSTEM.md
SECURITY.md
DEPLOYMENT.md
ROADMAP.md
DEVELOPMENT_RULES.md

Keep these documents synchronized with the implementation.

---

# 65. REQUIRED FINAL RESPONSE AFTER EACH PHASE

After completing a phase, report:

## Completed

List what was actually implemented.

## Files Changed

List important files.

## Database Changes

List migrations/models if any.

## Tests

List tests run and whether they passed.

## Integration Verification

Explain which real integrations were actually tested.

## Known Limitations

Be honest.

## Run Instructions

Give exact commands.

## Next Phase

State the next phase, but do not start it automatically unless explicitly instructed.

---

# 66. ABSOLUTE RULE AGAINST FAKE IMPLEMENTATIONS

Do not create code like:

return fake_generated_image
return fake_video_url
return mock_ai_response

unless explicitly working inside a test.

Tests may use mocks.

Production implementation must use the real configured services.

---

# 67. CODE QUALITY REQUIREMENTS

Use:

* clear naming
* typing
* docstrings where useful
* small functions
* modular services
* proper exception handling
* explicit validation
* reusable utilities
* clean API contracts

Avoid:

* giant views
* giant React components
* duplicated AI prompts
* hardcoded workflow JSON everywhere
* magic constants
* hidden global state
* deeply coupled services

---

# 68. FINAL DEVELOPMENT DIRECTIVE

Start with PHASE 0.

Do not start implementing the full application immediately.

Inspect the repository first.

Then produce the architecture documents.

After that, wait for explicit phase progression.

When a phase is requested:

* implement only that phase
* test it
* verify it
* document it
* stop

The objective is not to produce the maximum amount of code.

The objective is to produce a **real, working, maintainable, scalable UpMaket product**.

The quality bar is:

REAL DATA
+
REAL AI
+
REAL JOBS
+
REAL MEDIA
+
REAL ERROR HANDLING
+
REAL TESTING
+
REAL USER FLOW

Not a demo.

Not a mock.

Not a prototype disguised as a production system.

Build UpMaket as a real product.

# END OF MASTER SPECIFICATION
