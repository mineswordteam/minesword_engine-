"""Search engine processing, intent classification, multi-signal ranking, and real snippet extraction."""

import re
from typing import List, Dict, Any, Tuple, Optional, Set
from minesword.db import Database
from minesword.normalizer import normalize_text, tokenize, expand_query_synonyms
from minesword.intent import detect_query_intent, QueryIntent
from minesword.dedup import is_near_duplicate
from minesword.ranking_config import DEFAULT_RANKING_WEIGHTS, TOP_DOMAIN_AUTHORITIES


class SearchEngine:
    """Core search engine handling query parsing, intent detection, multi-signal ranking, and snippet generation."""

    def __init__(self, db: Database, weights: Optional[Dict[str, float]] = None):
        self.db = db
        self.weights = weights or DEFAULT_RANKING_WEIGHTS

    def parse_query(self, query: str) -> Tuple[str, List[str], Optional[str]]:
        """Parse raw query string into FTS expression, exact phrase list, and site filter domain."""
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

        fts_terms = [f'"{token}"*' for token in tokens if token]
        for phrase in norm_phrases:
            fts_terms.append(f'"{phrase}"')

        fts_query = " AND ".join(fts_terms) if fts_terms else ""
        return fts_query, norm_phrases, site_filter

    def extract_contextual_snippet(self, body_text: str, query_text: str, window_size: int = 200) -> str:
        """Extract real contextual excerpt around query matching terms in page body."""
        if not body_text:
            return ""

        norm_body = body_text.lower()
        norm_tokens = tokenize(normalize_text(query_text))

        best_pos = -1
        for token in norm_tokens:
            pos = norm_body.find(token.lower())
            if pos != -1:
                best_pos = pos
                break

        if best_pos == -1:
            snippet = body_text[:window_size].strip()
            return (snippet + "...") if len(body_text) > window_size else snippet

        start = max(0, best_pos - 40)
        end = min(len(body_text), best_pos + window_size - 40)
        excerpt = body_text[start:end].strip()

        prefix = "..." if start > 0 else ""
        suffix = "..." if end < len(body_text) else ""
        return f"{prefix}{excerpt}{suffix}"

    def rank_results(
        self,
        results: List[Dict[str, Any]],
        query_text: str,
        exact_phrases: List[str],
        intent: QueryIntent
    ) -> List[Dict[str, Any]]:
        """Calculate multi-signal relevance score for each document."""
        norm_query = normalize_text(query_text)
        query_tokens = tokenize(norm_query)

        ranked = []
        seen_texts: List[str] = []

        for item in results:
            base_score = abs(item.get("score", 1.0))
            relevance = 100.0 / (1.0 + base_score)

            norm_title = item.get("normalized_title") or normalize_text(item.get("title", ""))
            norm_body = item.get("normalized_body") or normalize_text(item.get("raw_body", ""))
            norm_desc = normalize_text(item.get("description", ""))
            headings = normalize_text(item.get("headings", ""))
            domain = item.get("domain", "").lower()

            # Near duplicate penalty check
            is_dup = False
            for prev_text in seen_texts:
                if is_near_duplicate(norm_body, prev_text):
                    is_dup = True
                    break
            if is_dup:
                relevance *= self.weights.get("duplicate_penalty", 0.5)
            else:
                seen_texts.append(norm_body)

            # Signal 1: Title Exact & Prefix Match
            if norm_query and norm_query in norm_title:
                relevance *= self.weights.get("title_exact_match", 3.0)
                if norm_title.startswith(norm_query):
                    relevance *= self.weights.get("title_prefix_match", 1.5)

            # Signal 2: Token Coverage
            if query_tokens:
                title_matches = sum(1 for t in query_tokens if t in norm_title)
                title_ratio = title_matches / float(len(query_tokens))
                relevance *= (1.0 + title_ratio * self.weights.get("title_token_coverage", 2.0))

                desc_matches = sum(1 for t in query_tokens if t in norm_desc)
                desc_ratio = desc_matches / float(len(query_tokens))
                relevance *= (1.0 + desc_ratio * self.weights.get("description_token_coverage", 0.8))

                heading_matches = sum(1 for t in query_tokens if t in headings)
                if heading_matches > 0:
                    relevance *= self.weights.get("heading_match", 1.8)

            # Signal 3: Exact Phrase Match
            for phrase in exact_phrases:
                if phrase in norm_title:
                    relevance *= self.weights.get("phrase_match_title", 2.5)
                elif phrase in norm_body:
                    relevance *= self.weights.get("phrase_match_body", 1.4)

            # Signal 4: Query Intent Matching
            if intent == QueryIntent.DOWNLOAD and ("دانلود" in norm_title or "download" in norm_title or "farsroid" in domain or "yasdl" in domain or "soft98" in domain):
                relevance *= self.weights.get("query_intent_match", 2.0)
            elif intent == QueryIntent.REVIEW_GUIDE and ("راهنما" in norm_title or "بررسی" in norm_title or "بهترین" in norm_title or "zoomit" in domain or "zoomg" in domain):
                relevance *= self.weights.get("query_intent_match", 2.0)
            elif intent == QueryIntent.LAPTOP_HARDWARE and ("لپ تاپ" in norm_title or "لب تاپ" in norm_title or "laptop" in norm_title or "zoomit" in domain or "digikala" in domain or "torob" in domain):
                relevance *= self.weights.get("query_intent_match", 2.0)

            # Signal 5: Domain Authority & NIN Boost
            for auth_domain, weight in TOP_DOMAIN_AUTHORITIES.items():
                if auth_domain in domain:
                    relevance *= weight
                    break
            else:
                if domain.endswith(".ir") or ".ir/" in domain:
                    relevance *= self.weights.get("iran_domain_boost", 1.2)

            item_copy = dict(item)
            item_copy["relevance"] = round(relevance, 2)
            item_copy["query_intent"] = intent.value

            # Extract real contextual snippet
            raw_body = item_copy.get("raw_body") or item_copy.get("description") or ""
            item_copy["snippet"] = self.extract_contextual_snippet(raw_body, query_text)

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
        """Execute search pipeline: parse query, detect intent, FTS lookup, rank, and paginate."""
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
        intent = detect_query_intent(query_clean)

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

        if category and category.strip() and category.strip() != "all":
            cat_norm = normalize_text(category)
            filtered = []
            for r in raw_results:
                text_check = normalize_text(r.get("title", "") + " " + r.get("description", "") + " " + r.get("raw_body", ""))
                if cat_norm in text_check:
                    filtered.append(r)
            if filtered:
                raw_results = filtered

        ranked_results = self.rank_results(raw_results, query_clean, exact_phrases, intent)

        total_results = len(ranked_results)
        offset = (page - 1) * page_size
        paginated = ranked_results[offset : offset + page_size]

        return {
            "query": query_clean,
            "intent": intent.value,
            "total": total_results,
            "page": page,
            "page_size": page_size,
            "total_pages": (total_results + page_size - 1) // page_size if page_size > 0 else 1,
            "results": paginated
        }

    def suggest(self, prefix: str, limit: int = 8) -> List[str]:
        return self.db.get_suggestions(prefix, limit=limit)
