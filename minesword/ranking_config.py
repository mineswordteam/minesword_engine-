"""Configurable ranking weights and multi-signal scoring configuration for Minesword Engine."""

from typing import Dict, Any

DEFAULT_RANKING_WEIGHTS: Dict[str, float] = {
    # Match Signal Weights
    "title_exact_match": 3.0,
    "title_prefix_match": 1.5,
    "title_token_coverage": 2.0,
    "heading_match": 1.8,
    "description_token_coverage": 0.8,
    "phrase_match_title": 2.5,
    "phrase_match_body": 1.4,

    # Authority & NIN Boosts
    "domain_authority_top": 1.4,
    "iran_domain_boost": 1.2,

    # Intent Match Boost
    "query_intent_match": 2.0,

    # Penalties
    "duplicate_penalty": 0.5
}

TOP_DOMAIN_AUTHORITIES: Dict[str, float] = {
    "farsroid.com": 1.4,
    "yasdl.com": 1.4,
    "soft98.ir": 1.4,
    "zoomg.ir": 1.3,
    "zoomit.ir": 1.3,
    "digikala.com": 1.3,
    "torob.com": 1.3,
    "varzesh3.com": 1.3,
    "aparat.com": 1.25,
    "p30download.ir": 1.25,
    "sarzamindownload.com": 1.25,
    "fa.wikipedia.org": 1.2
}
