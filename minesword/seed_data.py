"""Starter knowledge base and extensive pre-indexed Iranian web dataset for Minesword Engine."""

SEED_PAGES = [
    # --- فارسروید و دانلود بازی‌های اندروید (Farsroid - Games & Apps) ---
    {
        "url": "https://farsroid.com/call-of-duty-mobile-android/",
        "domain": "farsroid.com",
        "title": "دانلود بازی کال اف دیوتی موبایل Call of Duty Mobile برای اندروید + داتا - فارسروید",
        "description": "دانلود جدیدترین آپدیت بازی Call of Duty Mobile کال اف دیوتی موبایل با لینک مستقیم برای اندروید.",
        "raw_body": "دانلود بازی کال اف دیوتی موبایل (Call of Duty: Mobile) اندروید به همراه فایل دیتا. محبوب‌ترین بازی تفنگی و آنلاین شوتر اول شخص اکشن برای گوشی‌های هوشمند. دانلود کالاف دیوتی موبایل اندروید از فارسروید."
    },
    {
        "url": "https://farsroid.com/gta-san-andreas-android/",
        "domain": "farsroid.com",
        "title": "دانلود بازی GTA San Andreas جی تی ای ۵ برای اندروید - فارسروید",
        "description": "دانلود رایگان نسخه کامل و بدون حذفیات بازی جی تی ای سرقت بزرگ اتومبیل برای اندروید.",
        "raw_body": "دانلود بازی جی تی ای 5 (GTA San Andreas) برای اندروید با فایل دیتا و مود بی نهایت. بازی شوتر جهان باز شاهکار راک‌استار روی گوشی های هوشمند در فارسروید."
    },
    {
        "url": "https://farsroid.com/pubg-mobile-android/",
        "domain": "farsroid.com",
        "title": "دانلود بازی پابجی موبایل PUBG Mobile برای اندروید - فارسروید",
        "description": "دانلود بازی اکشن آنلاین پابجی موبایل اندروید با لینک مستقیم نیم‌بها.",
        "raw_body": "دانلود بازی پابجی موبایل (PUBG Mobile) برای اندروید. گرافیک فوق‌العاده کنسولی، نبردهای ۱۰۰ نفره آنلاین، بتل رویال شگفت‌انگیز در فارسروید."
    },

    # --- یاس دانلود (YasDL - Game & Software Downloads) ---
    {
        "url": "https://yasdl.com/download-call-of-duty-warzone-pc.html",
        "domain": "yasdl.com",
        "title": "دانلود بازی Call of Duty Warzone کال اف دیوتی وارزون برای کامپیوتر - یاس دانلود",
        "description": "دانلود بازی تفنگی اکشن کال اف دیوتی وارزون Call of Duty Warzone نسخه PC.",
        "raw_body": "دانلود بازی کال اف دیوتی وارزون (Call of Duty Warzone) برای کامپیوتر و سیستم با لینک مستقیم از یاس دانلود. جدیدترین نسخه بازی شوتر آنلاین رایگان نبرد رویال Call of Duty با بالاترین سرعت."
    },
    {
        "url": "https://yasdl.com/download-call-of-duty-black-ops-pc.html",
        "domain": "yasdl.com",
        "title": "دانلود بازی Call of Duty Black Ops 1, 2, 3, 4, 5 کال اف دیوتی - یاس دانلود",
        "description": "دانلود مجموعه کامل تمامی نسخه‌های بازی کال اف دیوتی بلک اپس برای کامپیوتر.",
        "raw_body": "دانلود بازی کال اف دیوتی بلک اپس Call of Duty Black Ops نسخه دوبله فارسی و اصلی برای PC. دانلود مستقیم شوتر اول شخص محبوب Call of Duty از یاس دانلود."
    },
    {
        "url": "https://yasdl.com/download-stronghold-crusader-pc.html",
        "domain": "yasdl.com",
        "title": "دانلود بازی جنگ‌های صلیبی ۱ و ۲ دوبله فارسی برای کامپیوتر - یاس دانلود",
        "description": "دانلود بازی استراتژیک جنگ های صلیبی Stronghold Crusader نسخه اصلی و نسخه فارسی.",
        "raw_body": "دانلود رایگان بازی جنگ های صلیبی (قلعه) نسخه ۱ و ۲ با دوبله کامل فارسی و صداپیشگان ایرانی. دانلود مستقیم بازی استراتژیک جنگ‌های صلیبی برای کامپیوتر با تمام مراحل و کدهای تقلب از یاس دانلود."
    },
    {
        "url": "https://yasdl.com/download-fifa-24-ea-fc-pc.html",
        "domain": "yasdl.com",
        "title": "دانلود بازی فیفا EA SPORTS FC 24 برای کامپیوتر - یاس دانلود",
        "description": "دانلود جدیدترین نسخه بازی فوتبال فیفا EA FC برای سیستم و کامپیوتر.",
        "raw_body": "دانلود بازی فیفا EA Sports FC 24 برای کامپیوتر با کرک معتبر و لینک مستقیم نیم‌بها. برترین بازی شبیه‌ساز فوتبال جهان در یاس دانلود."
    },

    # --- زومجی (Zoomg - Video Games & Movies) ---
    {
        "url": "https://zoomg.ir/game-reviews/call-of-duty-modern-warfare-3-review/",
        "domain": "zoomg.ir",
        "title": "بررسی بازی Call of Duty Modern Warfare 3؛ کال اف دیوتی جدید - زومجی",
        "description": "نقد و بررسی کامل بازی کال اف دیوتی مدرن وارفر ۳ و نمره‌دهی به بخش داستانی و آنلاین.",
        "raw_body": "زومجی در این مقاله به بررسی بازی جدید Call of Duty Modern Warfare 3 پرداخته است. داستان کاپیتان پرایس، گرافیک فوق‌العاده، کیفیت صداگذاری و نقد بخش چندنفره کال اف دیوتی."
    },

    # --- سافت ۹۸ (Soft98 - PC Games & Windows Software) ---
    {
        "url": "https://soft98.ir/game/1420-stronghold-crusader.html",
        "domain": "soft98.ir",
        "title": "دانلود بازی جنگ‌های صلیبی HD برای PC + فارسی - سافت ۹۸",
        "description": "دانلود بازی جنگ های صلیبی نسخه HD و دوبله فارسی خاطره انگیز.",
        "raw_body": "دانلود مستقیم بازی جنگ‌های صلیبی Stronghold Crusader HD نسخه کم حجم و فشرده FitGirl برای کامپیوتر. بازی قلعه جنگ های صلیبی یکی از برترین بازی‌های استراتژی نوستالژیک در ایران است."
    },
    {
        "url": "https://soft98.ir/game/call-of-duty-pc.html",
        "domain": "soft98.ir",
        "title": "دانلود رایگان تمامی نسخه های بازی کال اف دیوتی برای کامپیوتر - سافت ۹۸",
        "description": "دانلود بازی Call of Duty 1, 2, 4 Modern Warfare نسخه فشرده FitGirl.",
        "raw_body": "دانلود مستقیم بازی کال اف دیوتی (Call of Duty) برای کامپیوتر و PC با لینک مستقیم نیم بها. نسخه های کم حجم و فشرده FitGirl و Dodi بازی شوتر پرطرفدار Call of Duty در سافت ۹۸."
    },

    # --- سرزمین دانلود (SarzaminDownload) ---
    {
        "url": "https://sarzamindownload.com/contents/call-of-duty/",
        "domain": "sarzamindownload.com",
        "title": "دانلود بازی کال اف دیوتی برای کامپیوتر و اندروید - سرزمین دانلود",
        "description": "دانلود جدیدترین بازی‌های Call of Duty به همراه راهنمای نصب و ترینر.",
        "raw_body": "سرزمین دانلود مرجع دانلود بازی کال اف دیوتی (Call of Duty) کامپیوتر و گوشی. دانلود رایگان نسخه دوبله فارسی Call of Duty با نصب آسان."
    },

    # --- لپ‌تاپ و سخت‌افزار (Laptop & Hardware) ---
    {
        "url": "https://fa.wikipedia.org/wiki/لپ_تاپ",
        "domain": "fa.wikipedia.org",
        "title": "لپ‌تاپ و رایانه کیف‌دستی (لب تاپ) - دانشنامه آزاد",
        "description": "راهنمای کامل لپ‌تاپ، لب تاپ، سیستم‌های رایانه‌ای و قطعات سخت‌افزاری.",
        "raw_body": "لپ‌تاپ یا رایانه کیفی (Laptop) یا لب تاپ، یک رایانه شخصی همراه و کوچک است. لپ‌تاپ‌ها دارای صفحه نمایش، صفحه کلید، پردازنده، حافظه رم و باتری قابل شارژ هستند. برندهای محبوب لپ تاپ شامل ایسوس، لنوو، اپل مک‌بوک، اچ‌پی و دل می‌باشند."
    },
    {
        "url": "https://zoomit.ir/buying-guides/best-laptops-buying-guide/",
        "domain": "zoomit.ir",
        "title": "راهنمای خرید بهترین لپ تاپ و لب تاپ در بازار ایران (شهریور ۱۴۰۵)",
        "description": "لیست قیمت و راهنمای خرید انواع لپ تاپ دانشجویی، گیمینگ، مهندسی و اقتصادی.",
        "raw_body": "در این مقاله بهترین لپ تاپ های موجود در بازار ایران از برندهای ایسوس Asus، ایسر Acer، لنوو Lenovo و اپل معرفی شده‌اند. راهنمای خرید لب تاپ گیمینگ با کارت گرافیک RTX و لپتاپ‌های سبک دانشجویی برای کاربری روزمره."
    },
    {
        "url": "https://digikala.com/search/category-notebook-netbook/",
        "domain": "digikala.com",
        "title": "خرید لپ تاپ و لب تاپ با بهترین قیمت | دیجی‌کالا",
        "description": "بررسی قیمت لپ تاپ، لبتاپ‌های گیمینگ ایسوس، لنوو، مک‌بوک اپل با ضمانت اصالت.",
        "raw_body": "خرید آنلاین انواع لپ تاپ و لب تاپ گیمینگ، لپتاپ مهندسی، لپتاپ خانگی با تضمین بهترین قیمت و ارسال سریع. مقایسه مشخصات پردازنده Core i7 و Ryzen 7."
    },
    {
        "url": "https://lioncomputer.com/laptop-store.html",
        "domain": "lioncomputer.com",
        "title": "فروشگاه آنلاین لپ تاپ، لب تاپ گیمینگ و قطعات کامپیوتر - لیون کامپیوتر",
        "description": "تخصصی‌ترین مرکز فروش لپ تاپ و لب تاپ‌های گیمینگ حرفه‌ای در ایران.",
        "raw_body": "فروش حرفه‌ای انواع لپ تاپ و لب تاپ مخصوص بازی و رندرینگ، رم کامپیوتر، کارت گرافیک، حافظه اس اس دی SSD و سیستم‌های اسمبل شده گیمینگ."
    },
    {
        "url": "https://torob.com/browse/99/لپ-تاپ-laptop/",
        "domain": "torob.com",
        "title": "قیمت لپ تاپ و لب تاپ در فروشگاه‌های ایران | ترب",
        "description": "مقایسه قیمت میلیون‌ها مدل لپ تاپ و لبتاپ در هزاران فروشگاه معتبر.",
        "raw_body": "جستجو و مقایسه لحظه‌ای قیمت لپ تاپ ایسوس، لب تاپ لنوو، مک بوک، ایسر و اچ پی در تمامی فروشگاه‌های آنلاین ایران با تضمین کمترین قیمت."
    },
    {
        "url": "https://technolife.ir/product/category/laptop",
        "domain": "technolife.ir",
        "title": "قیمت انواع لپ تاپ و لبتاپ با گارانتی معتبر - تکنولایف",
        "description": "خرید اقساطی لپ تاپ و لب تاپ گیمینگ، اداری و دانش آموزی با ارسال فوری.",
        "raw_body": "فروش انواع لپ تاپ و لب تاپ با مهلت تست و گارانتی رسمی. قیمت لپتاپ core i5، مک بوک ایر و پرو، لپتاپ گیمینگ ROG و TUF ایسوس."
    },

    # --- اینترنت ملی و شبکه (National Intranet & Network) ---
    {
        "url": "https://zoomit.ir/tech/iran-intranet",
        "domain": "zoomit.ir",
        "title": "شبکه ملی اطلاعات و اینترنت ملی در ایران | وضعیت اینترنت",
        "description": "آخرین اخبار سرعت اینترنت، شبکه ملی اطلاعات و موتورهای جستجوی بومی.",
        "raw_body": "شبکه ملی اطلاعات یا اینترنت ملی در ایران، زیرساخت ارتباطی ایزوله داخلی است که دسترسی به وبسایت‌ها، موتورهای جستجوی بومی مانند Minesword Engine و سرویس‌های داخلی را در زمان قطعی اینترنت بین‌المللی تضمین می‌کند."
    },
    {
        "url": "https://fa.wikipedia.org/wiki/شبکه_ملی_اطلاعات",
        "domain": "fa.wikipedia.org",
        "title": "شبکه ملی اطلاعات (اینترنت ملی) - دانشنامه آزاد",
        "description": "تاریخچه، معماری و اهداف شبکه ملی اطلاعات و اینترنت داخلی در ایران.",
        "raw_body": "شبکه ملی اطلاعات یا اینترنت ملی، پروژه‌ای برای توسعه شبکه آی‌پی داخلی در کشور ایران است. هدف این شبکه افزایش سرعت ارتباطات داخلی، استقلال در زمان محدودیت‌های اینترنت و میزبانی موتورهای جستجو و پیام‌رسان‌های بومی است."
    },

    # --- اخبار و ورزش (News & Sports) ---
    {
        "url": "https://varzesh3.com/football-iran",
        "domain": "varzesh3.com",
        "title": "اخبار فوتبال ایران و ورزش۳ - نتایج زنده لیگ برتر",
        "description": "اخبار تیم ملی فوتبال ایران، بازی‌های لیگ برتر و مسابقات ورزشی.",
        "raw_body": "آخرین اخبار ورزشی و فوتبال ایران، جدول لیگ برتر، خلاصه بازی تیم ملی، اخبار جام جهانی و نقل و انتقالات بازیکنان فوتبال در ورزش ۳."
    },
    {
        "url": "https://football360.ir/news/",
        "domain": "football360.ir",
        "title": "فوتبال ۳۶۰ - نتایج زنده، خلاصه بازی‌ها و حواشی فوتبال",
        "description": "تحلیل‌های تخصصی فوتبال ایران و جهان، ویدیوهای بازی‌ها و جدول لیگ.",
        "raw_body": "فوتبال ۳۶۰ مرجع اخبار ویدیوها، مصاحبه‌های داغ فوتبالی، آنالیز فنی بازی‌های لیگ برتر ایران و مسابقات اروپا با اجرای عادل فردوسی‌پور."
    },

    # --- برنامه‌نویسی و وب (Programming & Technology) ---
    {
        "url": "https://maktabkhooneh.org/learn/python/",
        "domain": "maktabkhooneh.org",
        "title": "دوره آموزش کامل پایتون و برنامه‌نویسی وب - مکتب‌خونه",
        "description": "آموزش صفر تا صد برنامه‌نویسی پایتون، الگوریتم‌ها و پروژه‌های واقعی.",
        "raw_body": "آموزش برنامه‌نویسی پایتون از مقدماتی تا پیشرفته با مکتب‌خونه. یادگیری سورس‌کد ساخت موتور جستجو، هوش مصنوعی، پردازش متن و وب‌سرورهای پایتونی."
    },

    # --- خودرو (Automotive) ---
    {
        "url": "https://bama.ir/car",
        "domain": "bama.ir",
        "title": "خرید و فروش خودرو، ماشین صفر و کارکرده - باما",
        "description": "قیمت روز انواع ماشین، خودروهای ایرانی و وارداتی در بازار.",
        "raw_body": "خرید و فروش آنلاین خودرو و ماشین. ثبت آگهی رایگان خودرو، مشاهده قیمت روز ماشین‌های پژو، پراید، دنا، شاهین و خودروهای شاسی بلند وارداتی در باما."
    }
]


def seed_database_if_empty(db):
    """Seed initial pages if database contains zero pages or very few pages."""
    if db.get_total_pages() < len(SEED_PAGES):
        for page in SEED_PAGES:
            db.add_or_update_page(
                url=page["url"],
                domain=page["domain"],
                title=page["title"],
                description=page["description"],
                raw_body=page["raw_body"]
            )
