"""Text normalization module for Persian, Arabic, and English text processing."""

import re
import unicodedata

# Mapping table for Arabic/Persian char normalization
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

# Arabic diacritics regex (\u064b to \u0652 plus Maddah \u0653, Hamza below \u0654, etc.)
DIACRITICS_RE = re.compile(r'[\u064b-\u065f\u0670]')

# Non-breaking spaces, ZWNJs, invisible chars
INVISIBLE_CHARS_RE = re.compile(r'[\u200c\u200b\u200d\ufeff\u00a0]')

# Punctuation and non-alphanumeric chars for tokenization
PUNCTUATION_RE = re.compile(r'[^\w\s]', re.UNICODE)


def normalize_text(text: str) -> str:
    """Normalize text for Persian/Arabic/English indexing and search.

    Unifies Kaf, Yeh, Teh Marbuta, Alef, digits, removes diacritics & ZWNJ,
    lowercases English text, and removes extra spaces.
    """
    if not text:
        return ""

    # Normalize unicode (NFD / NFC)
    text = unicodedata.normalize('NFC', text)

    # Character replacements
    chars = []
    for ch in text:
        chars.append(PERSIAN_ARABIC_MAP.get(ch, ch))
    text = "".join(chars)

    # Remove diacritics
    text = DIACRITICS_RE.sub('', text)

    # Convert ZWNJ and invisible characters to spaces
    text = INVISIBLE_CHARS_RE.sub(' ', text)

    # Lowercase ASCII / Latin
    text = text.lower()

    # Collapse multiple whitespaces
    text = re.sub(r'\s+', ' ', text).strip()

    return text


def tokenize(text: str) -> list[str]:
    """Tokenize normalized text into clean words."""
    norm = normalize_text(text)
    # Remove punctuation
    cleaned = PUNCTUATION_RE.sub(' ', norm)
    tokens = [t.strip() for t in cleaned.split() if t.strip()]
    return tokens
