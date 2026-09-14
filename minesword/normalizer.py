"""Persian, Arabic, and English text normalization module for Minesword Engine."""

import re
import unicodedata
from typing import List, Set

# Char mapping table
PERSIAN_ARABIC_MAP = {
    'ك': 'ک',
    'ي': 'ی',
    'ى': 'ی',
    'ة': 'ه',
    'أ': 'ا',
    'إ': 'ا',
    'آ': 'ا',
    'ؤ': 'و',
    'ئ': 'ی',
    '٠': '0',
    '١': '1',
    '٢': '2',
    '٣': '3',
    '٤': '4',
    '٥': '5',
    '٦': '6',
    '٧': '7',
    '٨': '8',
    '٩': '9',
    '۰': '0',
    '۱': '1',
    '۲': '2',
    '۳': '3',
    '۴': '4',
    '۵': '5',
    '۶': '6',
    '۷': '7',
    '۸': '8',
    '۹': '9',
}

ENGLISH_TO_PERSIAN_DIGITS = {
    '0': '۰', '1': '۱', '2': '۲', '3': '۳', '4': '۴',
    '5': '۵', '6': '۶', '7': '۷', '8': '۸', '9': '۹'
}

# Controlled high-precision synonym dictionary
CONTROLLED_SYNONYMS = {
    "لب تاپ": ["لپ تاپ", "laptop"],
    "لپ تاپ": ["لب تاپ", "laptop"],
    "لپتاپ": ["لپ تاپ", "laptop"],
    "کالاف": ["کال اف دیوتی", "کالاف دیوتی", "call of duty"],
    "کالاف دیوتی": ["کال اف دیوتی", "کالاف", "call of duty"],
    "کال اف دیوتی": ["کالاف", "کالاف دیوتی", "call of duty"],
    "call of duty": ["کال اف دیوتی", "کالاف"],
    "جنگ های صلیبی": ["جنگهای صلیبی", "stronghold crusader"],
    "جنگهای صلیبی": ["جنگ های صلیبی", "stronghold crusader"],
    "stronghold crusader": ["جنگ های صلیبی"],
    "ویندوز ۱۱": ["ویندوز 11", "windows 11"],
    "ویندوز 11": ["ویندوز ۱۱", "windows 11"],
    "windows 11": ["ویندوز 11", "ویندوز ۱۱"],
    "پایتون": ["python"],
    "python": ["پایتون"],
    "گوشی": ["موبایل", "mobile"],
    "موبایل": ["گوشی", "mobile"],
    "خودرو": ["ماشین", "car"],
    "ماشین": ["خودرو", "car"]
}

DIACRITICS_RE = re.compile(r'[\u064b-\u065f\u0670]')
INVISIBLE_CHARS_RE = re.compile(r'[\u200c\u200b\u200d\ufeff\u00a0]')
PUNCTUATION_RE = re.compile(r'[^\w\s]', re.UNICODE)


def normalize_digits(text: str, to_english: bool = True) -> str:
    """Convert digits between Persian/Arabic and English."""
    if not text:
        return ""
    if to_english:
        chars = [PERSIAN_ARABIC_MAP.get(ch, ch) for ch in text]
    else:
        chars = [ENGLISH_TO_PERSIAN_DIGITS.get(ch, ch) for ch in text]
    return "".join(chars)


def normalize_text(text: str) -> str:
    """Normalize text for Persian/Arabic/English indexing and search."""
    if not text:
        return ""

    text = unicodedata.normalize('NFC', text)
    chars = [PERSIAN_ARABIC_MAP.get(ch, ch) for ch in text]
    text = "".join(chars)

    text = DIACRITICS_RE.sub('', text)
    text = INVISIBLE_CHARS_RE.sub(' ', text)
    text = text.lower()
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def tokenize(text: str) -> List[str]:
    """Tokenize normalized text into clean words."""
    norm = normalize_text(text)
    cleaned = PUNCTUATION_RE.sub(' ', norm)
    return [t.strip() for t in cleaned.split() if t.strip()]


def expand_query_synonyms(query: str) -> Set[str]:
    """Controlled synonym and digit variant expansion for search query."""
    norm_q = normalize_text(query)
    expansions = {norm_q}

    # Add digit variants
    expansions.add(normalize_digits(norm_q, to_english=True))
    expansions.add(normalize_digits(norm_q, to_english=False))

    for phrase, synonyms in CONTROLLED_SYNONYMS.items():
        norm_phrase = normalize_text(phrase)
        if norm_phrase in norm_q:
            for syn in synonyms:
                norm_syn = normalize_text(syn)
                expanded = norm_q.replace(norm_phrase, norm_syn)
                expansions.add(expanded)

    return expansions
