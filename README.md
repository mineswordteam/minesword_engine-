# Minesword Engine 🚀
**موتور جستجوی پیشرفته و هوشمند ماین‌سورد**

`Minesword Engine` یک موتور جستجوی کاملاً مستقل، فوق‌العاده سریع و همه-چیز-تمام است که به طور کامل از زبان‌های **فارسی، عربی و انگلیسی** پشتیبانی می‌کند. این موتور به صورت ۱۰۰٪ از کتابخانه‌های استاندارد پایتون و موتور **SQLite FTS5** استفاده می‌کند؛ در نتیجه برای اجرا هیچ نیازی به بسته خارجی ندارد و در شرایط محدودیت اینترنت یا **شبکه ملی اطلاعات (اینترنت ملی در ایران)** کاملاً ایزوله و عالی کار می‌کند.

---

## 🌟 ویژگی‌های کلیدی Minesword Engine

1. **نرمال‌سازی پیشرفته متن (Persian/Arabic Text Normalization):**
   - یکسان‌سازی حروف (کاف `ك` به `ک`، یای `ي/ى` به `ی`، ة به ه، و ...)
   - حذف کامل اعراب و تنوین (Diacritics stripping)
   - مدیریت حرف نیم‌فاصله (ZWNJ `\u200c`) و مبدل اعداد عربی/فارسی به انگلیسی
   - پشتیبانی همزمان از کلمات فارسی، عربی و انگلیسی

2. **الگوریتم رتبه‌بندی فوق پیشرفته (Advanced Relevance Ranking):**
   - ترکیب نمره **BM25** دیتابیس با ضریب وزنی تطابق دقیق در عنوان (Title Boost)
   - پشتیبانی از عبارت‌های دقیق داخل گیومه `"عبارت دقیق"`
   - فیلتر دامنه‌ای جستجو مانند `site:varzesh3.com`
   - پیشنهاد هوشمند کلمات و تکمیل خودکار (Auto-completion / Suggestions)

3. **خزشگر قدرتمند وب (Multithreaded Web Crawler):**
   - خزش چندنخی (Multithreaded) بدون لایبرری خارجی
   - استخراج عنوان، متاتگ‌های توضیح (Meta Description)، محتوای اصلی و لینک‌ها
   - جلوگیری از ثبت محتوای تکراری با هش هوشمند SHA-256 (Deduplication)
   - کنترل عمق خزش (Crawl Depth Limit)

4. **واسط کاربری مدرن (Modern Web UI):**
   - طراحی کاملاً راست‌چین (RTL) و پاسخگو (Responsive)
   - پشتیبانی از تم تاریک و روشن (Dark / Light Mode)
   - جستجوی آنی و نمایش برجسته کلمات (Snippet Highlighting)
   - پنل اضافه کردن وبسایت و شروع خزش مستقیم از مرورگر

---

## 🚀 راهنمای سریع اجرا (Quick Start)

### ۱. اجرای وب سرور و واسط کاربری (Web UI & REST API)
```bash
python3 -m minesword serve --port 8080
```
سپس مرورگر خود را باز کرده و به آدرس `http://localhost:8080` بروید.

### ۲. خزش وبسایت جدید از طریق ترمینال (CLI Crawl)
```bash
python3 -m minesword crawl https://zoomit.ir --depth 2 --max-pages 50
```

### ۳. جستجوی مستقیم در ترمینال (CLI Search)
```bash
python3 -m minesword search "اینترنت ملی"
```

### ۴. اجرای تست‌های واحد (Run Tests)
```bash
python3 -m unittest discover tests
```

---

## 🏗️ ساختار پروژه

```
minesword_engine/
├── minesword/
│   ├── __init__.py
│   ├── __main__.py          # نقطه ورود اجرایی ماژول
│   ├── cli.py               # رابط خط فرمان (CLI)
│   ├── crawler.py           # خزشگر هوشمند وب و پارسر HTML
│   ├── db.py                # مدیریت SQLite FTS5 و پیشنهاد کلمات
│   ├── normalizer.py        # نرمال‌ساز متون فارسی، عربی و انگلیسی
│   ├── search_engine.py     # موتور پردازش پرس‌وجو و الگوریتم رتبه‌بندی
│   ├── server.py            # وب سرور WSGI و REST API
│   └── static/
│       └── index.html       # واسط کاربری مدرن HTML/CSS/JS (RTL)
└── tests/                   # تست‌های کامل واحد و یکپارچه‌سازی
    ├── test_db.py
    ├── test_normalizer.py
    ├── test_search_engine.py
    └── test_server_and_crawler.py
```
