"""Search engine query processing and custom relevance ranking algorithm."""

import re
from typing import List, Dict, Any, Tuple, Optional
from minesword.db import Database
from minesword.normalizer import normalize_text, tokenize, expand_query_synonyms


TOP_AUTHORITY_DOMAINS = {
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


class SearchEngine:
    """Core search engine handling query parsing, FTS search, ranking, and autocomplete."""

    def __init__(self, db: Database):
        self.db = db

    def parse_query(self, query: str) -> Tuple[str, List[str], Optional[str]]:
        """Parse raw search query string into FTS query, exact phrase list, and site filter domain.

        Supports operators:
        - Exact phrases in double quotes: "national intranet"
        - Domain filter: site:varzesh3.com
        """
        exact_phrases = re.findall(r'"([^"]+)"', query)
        clean_q = re.sub(r'"[^"]+"', '', query)

        site_filter = None
        site_match = re.search(r'\bsite:([a-zA-Z0-9.-]+)', clean_q)
        if site_match:
            site_filter = site_match.group(1).lower()
            clean_q = re.sub(r'\bsite:[a-zA-Z0-9.-]+', '', clean_q)

        normalized_q = normalize_text(clean_q)
        tokens = tokenize(normalized_q)

        norm_phrases = [normalize_text(p) for p in exact_phrases if p.strip()]

        fts_terms = []
        for token in tokens:
            if token:
                fts_terms.append(f'"{token}"*')

        for phrase in norm_phrases:
            fts_terms.append(f'"{phrase}"')

        fts_query = " AND ".join(fts_terms) if fts_terms else ""
        return fts_query, norm_phrases, site_filter

    def rank_results(
        self,
        results: List[Dict[str, Any]],
        query_text: str,
        exact_phrases: List[str]
    ) -> List[Dict[str, Any]]:
        """Calculate custom relevance score for each result using Google-like multi-signal scoring.

        Score components:
        1. BM25 base score from SQLite FTS5
        2. Exact query match & prefix match in Title (up to 300% boost)
        3. Token coverage ratio in Title and Description
        4. Exact phrase presence in Title / Body
        5. Domain authority & .ir local domain bonus
        """
        norm_query = normalize_text(query_text)
        query_tokens = tokenize(norm_query)

        ranked = []
        for item in results:
            base_score = abs(item.get("score", 1.0))
            relevance = 100.0 / (1.0 + base_score)

            norm_title = item.get("normalized_title", normalize_text(item.get("title", "")))
            norm_body = item.get("normalized_body", normalize_text(item.get("raw_body", "")))
            norm_desc = item.get("normalized_description", normalize_text(item.get("description", "")))
            domain = item.get("domain", "").lower()

            # Boost 1: Full query in title
            if norm_query and norm_query in norm_title:
                relevance *= 3.0
                if norm_title.startswith(norm_query):
                    relevance *= 1.5

            # Boost 2: Query token occurrences in title and description
            if query_tokens:
                matches_in_title = sum(1 for t in query_tokens if t in norm_title)
                title_ratio = matches_in_title / float(len(query_tokens))
                relevance *= (1.0 + title_ratio * 2.0)

                matches_in_desc = sum(1 for t in query_tokens if t in norm_desc)
                desc_ratio = matches_in_desc / float(len(query_tokens))
                relevance *= (1.0 + desc_ratio * 0.8)

            # Boost 3: Exact phrase match boost
            for phrase in exact_phrases:
                if phrase in norm_title:
                    relevance *= 2.5
                elif phrase in norm_body:
                    relevance *= 1.4

            # Boost 4: Domain authority bonus
            for auth_domain, weight in TOP_AUTHORITY_DOMAINS.items():
                if auth_domain in domain:
                    relevance *= weight
                    break
            else:
                if domain.endswith(".ir") or ".ir/" in domain:
                    relevance *= 1.15

            item_copy = dict(item)
            item_copy["relevance"] = round(relevance, 2)

            if not item_copy.get("snippet"):
                raw = item_copy.get("description") or item_copy.get("raw_body", "")
                item_copy["snippet"] = (raw[:220] + "...") if len(raw) > 220 else raw

            ranked.append(item_copy)

        ranked.sort(key=lambda x: x["relevance"], reverse=True)
        return ranked

    def search(
        self,
        query: str,
        page: int = 1,
        page_size: int = 10,
        category: str = None
    ) -> Dict[str, Any]:
        """Execute full search pipeline: parse, expand synonyms, FTS query, filter, rank, and paginate."""
        query_clean = query.strip()
        if not query_clean:
            return {
                "query": query,
                "total": 0,
                "page": page,
                "page_size": page_size,
                "results": []
            }

        fts_query, exact_phrases, site_filter = self.parse_query(query_clean)

        expanded_queries = expand_query_synonyms(query_clean) if not exact_phrases else {query_clean}

        raw_results_dict: Dict[int, Dict[str, Any]] = {}

        for eq in expanded_queries:
            eq_fts, eq_phrases, _ = self.parse_query(eq)
            if not eq_fts:
                norm_q = normalize_text(eq)
                eq_fts = f'"{norm_q}"*' if norm_q else ""

            if eq_fts:
                res = self.db.search_fts(eq_fts, limit=200, offset=0)
                for r in res:
                    raw_results_dict[r["id"]] = r

        raw_results = list(raw_results_dict.values())

        if not raw_results and fts_query:
            tokens = tokenize(normalize_text(query_clean))
            if len(tokens) > 1:
                or_fts = " OR ".join([f'"{t}"*' for t in tokens if t])
                raw_results = self.db.search_fts(or_fts, limit=150, offset=0)

        if not raw_results:
            return {
                "query": query_clean,
                "total": 0,
                "page": page,
                "page_size": page_size,
                "total_pages": 0,
                "results": []
            }

        raw_results = list(raw_results)

        if site_filter:
            raw_results = [r for r in raw_results if site_filter in r.get("domain", "").lower()]

        # Filter category if specified
        if category and category.strip() and category.strip() != "all":
            cat_norm = normalize_text(category)
            filtered = []
            for r in raw_results:
                text_to_check = normalize_text(r.get("title", "") + " " + r.get("description", "") + " " + r.get("raw_body", ""))
                if cat_norm in text_to_check:
                    filtered.append(r)
            if filtered:
                raw_results = filtered

        ranked_results = self.rank_results(raw_results, query_clean, exact_phrases)

        total_results = len(ranked_results)
        offset = (page - 1) * page_size
        paginated = ranked_results[offset : offset + page_size]

        return {
            "query": query_clean,
            "total": total_results,
            "page": page,
            "page_size": page_size,
            "total_pages": (total_results + page_size - 1) // page_size if page_size > 0 else 1,
            "results": paginated
        }

    def suggest(self, prefix: str, limit: int = 8) -> List[str]:
        """Get auto-completion suggestions for query prefix."""
        return self.db.get_suggestions(prefix, limit=limit)
