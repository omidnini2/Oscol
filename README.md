# Voice Cloning Website (PHP + Coqui XTTS)

> راه‌اندازی کامل وب‌سایت کلون‌صدای چندزبانه، بدون محدودیت، مخصوص استفاده خانوادگی

## فهرست مطالب
1. معرفی پروژه و معماری
2. پیش‌نیازها
3. نصب و اجرا (Docker)
4. استفاده از سایت
5. افزودن زبان یا مدل جدید
6. امنیت و استفاده فقط در شبکهٔ شخصی
7. نکات بهبود کیفیت صدا
8. توسعه آینده

---

## 1. معرفی پروژه و معماری

![diagram](docs/architecture.png)

| سرویس | پورت | توضیح |
|-------|-------|---------|
| **web (PHP-Apache)** | 8080 | رابط کاربری، تم دارک/لایت، ضبط یا آپلود صدا، ارسال متن |
| **tts (Python-Flask)** | 5000 | موتور TTS مدل XTTS v1 (Coqui) + langdetect؛ کلون صدا و خواندن متن |

هر دو سرویس در شبکهٔ داخلی «voicenet» (Docker) قرار دارند.

## 2. پیش‌نیازها
- Docker 24.x + docker compose v2
- حداقل ۸ GB RAM (GPU اختیاری ولی سرعت را ↑ می‌کند)
- سیستم‌عامل Linux/macOS/Windows (یا WSL)

## 3. نصب و اجرا
```bash
# دریافت سورس
$ git clone https://github.com/<YOUR_USER>/voice-clone-php.git
$ cd voice-clone-php

# اولین اجرا (دانلود ایمیج‌ها و مدل XTTS ~1.5GB)
$ docker compose up --build
```
پس از آماده شدن کانتینرها:
- http://localhost:8080 → رابط وب
- http://localhost:5000 → API سرور (مسیرهای /clone و /tts)

## 4. استفاده از سایت
1. روی «🎤 Record» بزنید یا یک فایل صوتی (۴–۶ ثانیه تمیز) آپلود کنید.
2. «Clone Voice» → سرور فایل را ذخیره و یک شناسه برمی‌گرداند.
3. متن دلخواه را (هر زبانی) در textarea بنویسید.
4. «Speak» → خروجی wav تولید و پخش می‌شود.

> XTTS v1 فعلاً ۱۳ زبان اصلی را با کیفیت بالا پشتیبانی می‌کند (en, es, fr, de, it, pt, pl, ru, nl, cz, tr, ar, zh). برای فارسی/آذری کیفیت متوسط است.

## 5. افزودن زبان یا مدل جدید
- **مدل فارسی VITS**: در `tts-backend/app.py` نام مدل را تغییر دهید:
  ```python
  MODEL_NAME = "tts_models/fa/custom/vits"
  ```
- **سوئیچ خودکار**: می‌توانید دیکشنری `language -> model_name` تعریف و بر اساس خروجی `langdetect` انتخاب کنید.

## 6. امنیت و شبکهٔ‌ خصوصی
- اگر فقط LAN: پورت‌ها را روی روتر محدود کنید.
- احراز هویت پایه در Apache:
  ```apache
  AuthType Basic
  AuthName "Family Only"
  AuthUserFile /var/www/.htpasswd
  Require valid-user
  ```
- ایجاد کاربر: `docker compose exec web htpasswd -c /var/www/.htpasswd youruser`

## 7. نکات کیفیت صدا
- نمونهٔ مرجع ۳–۶ ثانیه، بدون نویز محیط.
- متن ≤ ۲۵۰ کاراکتر؛ اعداد را به حروف بنویسید.
- برای حروف اختصاری (F B I) حروف را با فاصله بنویسید.

## 8. توسعه آینده
- پشتیبانی GPU (Nvidia): `docker compose up --build --compatibility --gpus all`
- استریم زنده (WebSocket + FastAPI)
- ذخیرهٔ پروفایل‌ها در SQLite + رابط مدیریت

---

<p align="center">با عشق ❤️ توسط خانوادهٔ ما</p>