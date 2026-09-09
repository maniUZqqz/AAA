# گزارش باگ دور اول (نسخهٔ ۱) — بایگانی

> این متن اصلیِ `beter.md` نسخهٔ ۱ است و فقط برای تاریخچه نگه داشته شده.
> گزارش دور دوم در `beter.md` و پاسخ کامل به هر دو در `FIXED.md` است.

---


1 چت های پشتیبانی ذخیره بشه و بشه از فرانت چت های قبلی رو دید ولی خود چت درست کار میکنه 


2  لودینگ ها درست بشه برای تحلیل محصول و کارای صفحه http://localhost:5173/products/{i} لودینگ های درستی نداره و کارای هوش مصنوعی لاما یکی درمون کار می کنه ! و بعضی  وقت ها تسک داره و یهو مرخص میشه  چه تحلیل محصول چه تحلیل مجدد 
یا دفعه اول کار می کنه 


3 تحلیل رقاب بیاد رقیت ها رو هم نشون بده هم برند رقیب هم محصول اش و مقایشه بکنه


4 درست کردن کردن پوستر و عکس دو تا مشکل اساسی داره 
الف : محصول اصلا اون نیست و یه چیز دیگه رو ساخته 
ب : مت.ن فارسی قرار بود روش باشه عربی نامعلوم نوشته بهتره با یک برنامه کد بیایم پوستر رو اضافه کنیم 



5 بخش کپشن ارور داره 

Model qwq:32b returned non-JSON output (2317 chars) Watching for file changes with StatReloader 2026-08-28 19:10:15,380 INFO [django.utils.autoreload] Watching for file changes with StatReloader Performing system checks... System check identified no issues (0 silenced). August 28, 2026 - 19:10:15 Django version 5.2.17, using settings 'config.settings' Starting development server at http://0.0.0.0:8000/ Quit the server with CTRL-BREAK. WARNING: This is a development server. Do not use it in a production setting. Use a production WSGI or ASGI server instead. For more information on production servers see: https://docs.djangoproject.com/en/5.2/howto/deployment/ [28/Aug/2026 19:10:28] "GET /api/docs/ HTTP/1.1" 200 4645 C:\Users\Dragon\AppData\Roaming\Python\Python312\site-packages\jwt\api_jwt.py:368: InsecureKeyLengthWarning: The HMAC key is 28 bytes long, which is below the minimum recommended length of 32 bytes for SHA256. See RFC 7518 Section 3.2. decoded = self.decode_complete( [28/Aug/2026 19:10:30] "GET /api/v1/auth/me/ HTTP/1.1" 200 97 [28/Aug/2026 19:10:30] "GET /api/v1/auth/me/ HTTP/1.1" 200 97 [28/Aug/2026 19:10:30] "GET /api/v1/notifications/?unread=true HTTP/1.1" 200 69 [28/Aug/2026 19:10:30] "GET /api/v1/stores/ HTTP/1.1" 200 518 [28/Aug/2026 19:10:30] "GET /api/v1/notifications/?unread=true HTTP/1.1" 200 69 [28/Aug/2026 19:10:30] "GET /api/v1/stores/ HTTP/1.1" 200 518 [28/Aug/2026 19:10:48] "GET /api/v1/notifications/?unread=true HTTP/1.1" 200 69 [28/Aug/2026 19:10:48] "GET /api/v1/auth/me/ HTTP/1.1" 200 97 [28/Aug/2026 19:10:48] "GET /api/v1/auth/me/ HTTP/1.1" 200 97 [28/Aug/2026 19:10:48] "GET /api/v1/notifications/?unread=true HTTP/1.1" 200 69 [28/Aug/2026 19:10:48] "GET /api/v1/products/2/ HTTP/1.1" 200 907 [28/Aug/2026 19:10:48] "GET /api/v1/notifications/?unread=true HTTP/1.1" 200 69 [28/Aug/2026 19:10:48] "GET /api/v1/products/2/ HTTP/1.1" 200 907 [28/Aug/2026 19:10:48] "GET /api/v1/products/2/image-studio/ HTTP/1.1" 200 1389 [28/Aug/2026 19:10:48] "GET /api/v1/products/2/intelligence/ HTTP/1.1" 200 3509 Not Found: /api/v1/products/2/video-script/ [28/Aug/2026 19:10:48] "GET /api/v1/products/2/captions/ HTTP/1.1" 200 2 2026-08-28 19:10:48,804 WARNING [django.request] Not Found: /api/v1/products/2/video-script/ [28/Aug/2026 19:10:48] "GET /api/v1/products/2/video-script/ HTTP/1.1" 404 33 [28/Aug/2026 19:10:48] "GET /api/v1/products/2/market-analysis/ HTTP/1.1" 200 3453 [28/Aug/2026 19:10:48] "GET /api/v1/products/2/image-studio/ HTTP/1.1" 200 1389 [28/Aug/2026 19:10:48] "GET /api/v1/products/2/intelligence/ HTTP/1.1" 200 3509 [28/Aug/2026 19:10:48] "GET /api/v1/products/2/captions/ HTTP/1.1" 200 2 Not Found: /api/v1/products/2/video-script/ 2026-08-28 19:10:48,827 WARNING [django.request] Not Found: /api/v1/products/2/video-script/ [28/Aug/2026 19:10:48] "GET /api/v1/products/2/video-script/ HTTP/1.1" 404 33 [28/Aug/2026 19:10:48] "GET /api/v1/products/2/market-analysis/ HTTP/1.1" 200 3453 [28/Aug/2026 19:10:49] "GET /media/generated/images/57eafacd7d7048318e1d2d0ec3f4fd77_product_2_00001_.png HTTP/1.1" 304 0 [28/Aug/2026 19:10:49] "GET /api/v1/auth/me/ HTTP/1.1" 200 97 [28/Aug/2026 19:10:49] "GET /api/v1/auth/me/ HTTP/1.1" 200 97 [28/Aug/2026 19:10:49] "GET /api/v1/notifications/?unread=true HTTP/1.1" 200 69 [28/Aug/2026 19:10:49] "GET /api/v1/products/2/ HTTP/1.1" 200 907 [28/Aug/2026 19:10:49] "GET /api/v1/notifications/?unread=true HTTP/1.1" 200 69 [28/Aug/2026 19:10:49] "GET /api/v1/products/2/ HTTP/1.1" 200 907 [28/Aug/2026 19:10:49] "GET /api/v1/products/2/intelligence/ HTTP/1.1" 200 3509 [28/Aug/2026 19:10:49] "GET /api/v1/products/2/market-analysis/ HTTP/1.1" 200 3453 [28/Aug/2026 19:10:49] "GET /api/v1/products/2/image-studio/ HTTP/1.1" 200 1389 [28/Aug/2026 19:10:49] "GET /api/v1/products/2/captions/ HTTP/1.1" 200 2 Not Found: /api/v1/products/2/video-script/ 2026-08-28 19:10:49,944 WARNING [django.request] Not Found: /api/v1/products/2/video-script/ [28/Aug/2026 19:10:49] "GET /api/v1/products/2/video-script/ HTTP/1.1" 404 33 [28/Aug/2026 19:10:49] "GET /api/v1/products/2/intelligence/ HTTP/1.1" 200 3509 [28/Aug/2026 19:10:49] "GET /api/v1/products/2/market-analysis/ HTTP/1.1" 200 3453 Not Found: /api/v1/products/2/video-script/ 2026-08-28 19:10:49,962 WARNING [django.request] Not Found: /api/v1/products/2/video-script/ [28/Aug/2026 19:10:49] "GET /api/v1/products/2/image-studio/ HTTP/1.1" 200 1389 [28/Aug/2026 19:10:49] "GET /api/v1/products/2/video-script/ HTTP/1.1" 404 33 [28/Aug/2026 19:10:49] "GET /api/v1/products/2/captions/ HTTP/1.1" 200 2 [28/Aug/2026 19:11:19] "GET /api/v1/notifications/?unread=true HTTP/1.1" 200 69 [28/Aug/2026 19:11:49] "GET /api/v1/notifications/?unread=true HTTP/1.1" 200 69 [28/Aug/2026 19:12:19] "GET /api/v1/notifications/?unread=true HTTP/1.1" 200 69 [28/Aug/2026 19:12:49] "GET /api/v1/notifications/?unread=true HTTP/1.1" 200 69 [28/Aug/2026 19:13:19] "GET /api/v1/notifications/?unread=true HTTP/1.1" 200 69 [28/Aug/2026 19:13:49] "GET /api/v1/notifications/?unread=true HTTP/1.1" 200 69 [28/Aug/2026 19:14:19] "GET /api/v1/notifications/?unread=true HTTP/1.1" 200 69 [28/Aug/2026 19:14:49] "GET /api/v1/notifications/?unread=true HTTP/1.1" 200 69 [28/Aug/2026 19:15:19] "GET /api/v1/notifications/?unread=true HTTP/1.1" 200 69 [28/Aug/2026 19:15:49] "GET /api/v1/notifications/?unread=true HTTP/1.1" 200 69 [28/Aug/2026 19:16:19] "GET /api/v1/notifications/?unread=true HTTP/1.1" 200 69 [28/Aug/2026 19:16:49] "GET /api/v1/notifications/?unread=true HTTP/1.1" 200 69 [28/Aug/2026 19:17:19] "GET /api/v1/notifications/?unread=true HTTP/1.1" 200 69 [28/Aug/2026 19:17:49] "GET /api/v1/notifications/?unread=true HTTP/1.1" 200 69 [28/Aug/2026 19:18:19] "GET /api/v1/notifications/?unread=true HTTP/1.1" 200 69 [28/Aug/2026 19:18:50] "GET /api/v1/notifications/?unread=true HTTP/1.1" 200 69 [28/Aug/2026 19:19:20] "GET /api/v1/notifications/?unread=true HTTP/1.1" 200 69 [28/Aug/2026 19:20:12] "GET /api/v1/notifications/?unread=true HTTP/1.1" 200 69 2026-08-28 19:21:00,377 ERROR [apps.content.tasks] Caption job 83 failed Traceback (most recent call last): File "C:\Users\Dragon\Desktop\UpMarket\backend\services\ai\ollama.py", line 266, in generate_json return json.loads(raw), raw ^^^^^^^^^^^^^^^ File "C:\Program Files\Python312\Lib\json\__init__.py", line 346, in loads return _default_decoder.decode(s) ^^^^^^^^^^^^^^^^^^^^^^^^^^ File "C:\Program Files\Python312\Lib\json\decoder.py", line 337, in decode obj, end = self.raw_decode(s, idx=_w(s, 0).end()) ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ File "C:\Program Files\Python312\Lib\json\decoder.py", line 353, in raw_decode obj, end = self.scan_once(s, idx) ^^^^^^^^^^^^^^^^^^^^^^ json.decoder.JSONDecodeError: Expecting ',' delimiter: line 27 column 4 (char 2317) During handling of the above exception, another exception occurred: Traceback (most recent call last): File "C:\Users\Dragon\Desktop\UpMarket\backend\apps\content\tasks.py", line 67, in generate_captions_task parsed, request_row = recorded_json_call( ^^^^^^^^^^^^^^^^^^^ File "C:\Users\Dragon\Desktop\UpMarket\backend\apps\ai\services.py", line 28, in recorded_json_call parsed, raw = provider.generate_json(model, prompt, system=system, images=images) ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ File "C:\Users\Dragon\Desktop\UpMarket\backend\services\ai\ollama.py", line 274, in generate_json raise OllamaMalformedOutput( services.ai.ollama.OllamaMalformedOutput: Model qwq:32b returned non-JSON output (2317 chars) 2026-08-28 19:21:00,458 INFO [celery.app.trace] Task apps.content.tasks.generate_captions_task[2ea396b3-d6f7-4bce-8f30-c724ab42c96e] succeeded in 596.2649999999994s: {'error': 'Model qwq:32b returned non-JSON output (2317 chars)'} [28/Aug/2026 19:21:00] "POST /api/v1/products/2/captions/ HTTP/1.1" 202 431 [28/Aug/2026 19:21:03] "GET /api/v1/jobs/83/ HTTP/1.1" 200 411 [28/Aug/2026 19:21:12] "GET /api/v1/notifications/?unread=true HTTP/1.1" 200 69 [28/Aug/2026 19:22:12] "GET /api/v1/notifications/?unread=true HTTP/1.1" 200 69 [28/Aug/2026 19:23:07] "GET /api/v1/notifications/?unread=true HTTP/1.1" 200 69 [28/Aug/2026 19:23:20] "GET /api/v1/notifications/?unread=true HTTP/1.1" 200 69 [28/Aug/2026 19:23:50] "GET /api/v1/notifications/?unread=true HTTP/1.1" 200 69 [28/Aug/2026 19:24:51] "GET /api/v1/notifications/?unread=true HTTP/1.1" 200 69 [28/Aug/2026 19:25:52] "GET /api/v1/notifications/?unread=true HTTP/1.1" 200 69


6 بخش تولید ویدیو رو تست نتونستن بگیرم 
چون بعد ساخت سنریو ارور داد 
تولید ویدیو در حالت synchronous ممکن نیست — Redis و Celery worker را روشن کنید (CELERY_TASK_ALWAYS_EAGER=false).

که احتمالا از منابع هستش یعنی مدل لاما روشنه و دیگه مدل ویدیو کار نمی کنه !


7 کیفیت خروجی رو با پرامپت های بهتر بهتر کن 


8 روی لودینگ ها چیزایی که منتظر هوش مصنوعی می مونه کار کن که کاربر بدونه اتفاقی داره اون پشت می افته و سیستم کرش نکرده


9 ببین ما سیستم محدود داریم باید مدل های اولاما که دو تا هستند و یک مدل عکس و یک مدل ویدیو رو جوری تنظیم کنی منابع اذیت نشن یعنی من دارم منابع کم میارم که این ها با هم اجرا میشن باید جوری باشه یکی کار می کنه اون یکی متوقف بشه و یک جور هندل بشه 
در حدی که من فکر می کنم بعضی وقت ها که کار می کنه میگم خراب شده !



10 ارور
Download the React DevTools for a better development experience: https://reactjs.org/link/react-devtools
react-router-dom.js?v=534a7695:4417 ⚠️ React Router Future Flag Warning: React Router will begin wrapping state updates in `React.startTransition` in v7. You can use the `v7_startTransition` future flag to opt-in early. For more information, see https://reactrouter.com/v6/upgrading/future#v7_starttransition.
warnOnce @ react-router-dom.js?v=534a7695:4417
react-router-dom.js?v=534a7695:4417 ⚠️ React Router Future Flag Warning: Relative route resolution within Splat routes is changing in v7. You can use the `v7_relativeSplatPath` future flag to opt-in early. For more information, see https://reactrouter.com/v6/upgrading/future#v7_relativesplatpath.
warnOnce @ react-router-dom.js?v=534a7695:4417
:5173/api/v1/products/2/video-script/:1  Failed to load resource: the server responded with a status of 404 (Not Found)
:5173/api/v1/products/2/video-script/:1  Failed to load resource: the server responded with a status of 404 (Not Found)
:5173/api/v1/video-scripts/1/generate/:1  Failed to load resource: the server responded with a status of 503 (Service Unavailable)

که 
generate
video-script 
نیست اش

