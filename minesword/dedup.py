"""Exact and near-duplicate content detection module for Minesword Engine."""

import hashlib
import re
from typing import Set, List
from minesword.normalizer import normalize_text, tokenize


def compute_content_hash(text: str) -> str:
    """Compute exact SHA-256 content hash of normalized text."""
    norm = normalize_text(text)
    return hashlib.sha256(norm.encode('utf-8')).hexdigest()


def get_shingles(text: str, k: int = 3) -> Set[str]:
    """Extract character k-shingles from normalized text."""
    norm = normalize_text(text)
    cleaned = re.sub(r'\s+', '', norm)
    if len(cleaned) < k:
        return {cleaned}
    return {cleaned[i:i+k] for i in range(len(cleaned) - k + 1)}


def jaccard_similarity(set1: Set[str], set2: Set[str]) -> float:
    """Calculate Jaccard similarity score between two set collections."""
    if not set1 or not set2:
        return 0.0
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return float(intersection) / float(union) if union > 0 else 0.0


def is_near_duplicate(text1: str, text2: str, threshold: float = 0.85) -> bool:
    """Check if two text documents are near-duplicates using Jaccard shingle similarity."""
    s1 = get_shingles(text1)
    s2 = get_shingles(text2)
    return jaccard_similarity(s1, s2) >= threshold
