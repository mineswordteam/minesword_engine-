"""Search engine query processing and custom relevance ranking algorithm."""

import re
from typing import List, Dict, Any, Tuple, Optional
from minesword.db import Database
from minesword.normalizer import normalize_text, tokenize


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
        # Remove exact phrases from main query
        clean_q = re.sub(r'"[^"]+"', '', query)

        # Domain filter site:domain.com
        site_filter = None
        site_match = re.search(r'\bsite:([a-zA-Z0-9.-]+)', clean_q)
        if site_match:
            site_filter = site_match.group(1).lower()
            clean_q = re.sub(r'\bsite:[a-zA-Z0-9.-]+', '', clean_q)

        normalized_q = normalize_text(clean_q)
        tokens = tokenize(normalized_q)

        # Normalize exact phrases
        norm_phrases = [normalize_text(p) for p in exact_phrases if p.strip()]

        # Build SQLite FTS5 query string
        fts_terms = []
        for token in tokens:
            if token:
                # Add prefix search to last token or all tokens for flexible matching
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
        """Calculate custom relevance score for each result.

        Score components:
        1. BM25 score from SQLite FTS5 (lower BM25 numerical score = higher relevance)
        2. Exact query match boost in Title (up to 50% score boost)
        3. Token match ratio in Title (boost)
        4. Exact phrase presence in Title / Body (boost)
        5. Domain brevity & quality bonus (.ir / national domain relevance)
        """
        norm_query = normalize_text(query_text)
        query_tokens = tokenize(norm_query)

        ranked = []
        for item in results:
            base_score = abs(item.get("score", 1.0))
            # Start with base score multiplier (smaller score = better in FTS5 BM25, so we convert to a higher-is-better metric)
            relevance = 100.0 / (1.0 + base_score)

            norm_title = item.get("normalized_title", normalize_text(item.get("title", "")))
            norm_body = item.get("normalized_body", normalize_text(item.get("raw_body", "")))

            # Boost 1: Full query in title
            if norm_query and norm_query in norm_title:
                relevance *= 2.5

            # Boost 2: Query token occurrences in title
            if query_tokens:
                matches_in_title = sum(1 for t in query_tokens if t in norm_title)
                title_ratio = matches_in_title / float(len(query_tokens))
                relevance *= (1.0 + title_ratio * 1.5)

            # Boost 3: Exact phrase match boost
            for phrase in exact_phrases:
                if phrase in norm_title:
                    relevance *= 2.0
                elif phrase in norm_body:
                    relevance *= 1.3

            # Boost 4: Iranian domain boost (.ir / local domain)
            domain = item.get("domain", "").lower()
            if domain.endswith(".ir") or ".ir/" in domain:
                relevance *= 1.2

            item_copy = dict(item)
            item_copy["relevance"] = round(relevance, 2)

            # Format snippet highlighting
            if not item_copy.get("snippet"):
                # Generate fallback snippet
                raw = item_copy.get("raw_body", "")
                item_copy["snippet"] = (raw[:200] + "...") if len(raw) > 200 else raw

            ranked.append(item_copy)

        # Sort descending by relevance
        ranked.sort(key=lambda x: x["relevance"], reverse=True)
        return ranked

    def search(
        self,
        query: str,
        page: int = 1,
        page_size: int = 10
    ) -> Dict[str, Any]:
        """Execute full search pipeline: parse, FTS query, filter, rank, and paginate."""
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

        if not fts_query:
            # Fallback for single characters or empty parsed query
            norm_q = normalize_text(query_clean)
            fts_query = f'"{norm_q}"*' if norm_q else ""

        if not fts_query:
            return {
                "query": query,
                "total": 0,
                "page": page,
                "page_size": page_size,
                "results": []
            }

        raw_results = self.db.search_fts(fts_query, limit=200, offset=0)

        # Apply site filter if requested
        if site_filter:
            raw_results = [r for r in raw_results if site_filter in r.get("domain", "").lower()]

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
