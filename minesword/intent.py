"""Query intent detector module for Minesword Engine."""

from enum import Enum
from typing import Dict, Any, List
from minesword.normalizer import normalize_text


class QueryIntent(Enum):
    GENERAL = "general"
    DOWNLOAD = "download"
    REVIEW_GUIDE = "review_guide"
    SOFTWARE_GAME = "software_game"
    LAPTOP_HARDWARE = "laptop_hardware"
    NEWS = "news"
    SPORTS = "sports"
    AUTOMOTIVE = "automotive"
    TROUBLESHOOTING = "troubleshooting"


INTENT_KEYWORDS = {
    QueryIntent.DOWNLOAD: ["دانلود", "دریافت", "download", "apk", "نسخه فشرده", "کرک"],
    QueryIntent.REVIEW_GUIDE: ["بهترین", "راهنما", "بررسی", "آموزش", "اموزش", "مقایسه", "راهنمای خرید"],
    QueryIntent.SOFTWARE_GAME: ["بازی", "گیم", "کالاف", "پابجی", "صلیبی", "جی تی ای", "کلش", "فیفا", "ویندوز", "اپلیکیشن", "برنامه"],
    QueryIntent.LAPTOP_HARDWARE: ["لپ تاپ", "لب تاپ", "laptop", "کارت گرافیک", "پردازنده", "رم", "مادربرد", "ایسوس", "لنوو", "قیمت لپ تاپ"],
    QueryIntent.NEWS: ["اخبار", "خبر", "فوری", "خبرگزاری", "اطلاعیه", "روزنامه"],
    QueryIntent.SPORTS: ["فوتبال", "ورزش", "لیگ برتر", "استقلال", "پرسپولیس", "تیم ملی", "جام جهانی"],
    QueryIntent.AUTOMOTIVE: ["خودرو", "ماشین", "قیمت خودرو", "باما", "ایران خودرو", "سایپا"],
    QueryIntent.TROUBLESHOOTING: ["حل مشکل", "ارور", "خطا", "رفع مشکل", "قطع شدن", "کار نکردن"]
}


def detect_query_intent(query: str) -> QueryIntent:
    """Detect dominant query intent from search keywords."""
    norm_q = normalize_text(query)
    if not norm_q:
        return QueryIntent.GENERAL

    scores: Dict[QueryIntent, int] = {intent: 0 for intent in QueryIntent}

    for intent, keywords in INTENT_KEYWORDS.items():
        for kw in keywords:
            norm_kw = normalize_text(kw)
            if norm_kw in norm_q:
                scores[intent] += 2 if norm_kw == norm_q else 1

    best_intent = max(scores, key=scores.get)
    if scores[best_intent] > 0:
        return best_intent
    return QueryIntent.GENERAL
