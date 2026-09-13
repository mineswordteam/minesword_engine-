"""Web crawler and HTML parser module for Minesword search engine."""

import urllib.request
import urllib.parse
import urllib.error
import re
import socket
import logging
from html.parser import HTMLParser
from typing import Set, List, Dict, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor
from minesword.db import Database

logger = logging.getLogger(__name__)

# Standard User-Agent mimicking standard browser for maximum compatibility
DEFAULT_USER_AGENT = "MineswordBot/1.0 (+http://minesword.local/bot)"


class HTMLTextExtractor(HTMLParser):
    """Custom HTML Parser to extract title, meta description, raw body text, and internal/external hyperlinks."""

    def __init__(self):
        super().__init__()
        self.in_title = False
        self.in_script_or_style = False
        self.title_parts: List[str] = []
        self.meta_description: str = ""
        self.body_parts: List[str] = []
        self.links: List[str] = []
        self.canonical_url: Optional[str] = None

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]):
        tag = tag.lower()
        attr_dict = {k.lower(): (v or "") for k, v in attrs}

        if tag == "title":
            self.in_title = True
        elif tag in ["script", "style", "noscript", "svg", "header", "footer", "nav"]:
            self.in_script_or_style = True
        elif tag == "meta":
            name = attr_dict.get("name", "").lower()
            property_attr = attr_dict.get("property", "").lower()
            if name == "description" or property_attr == "og:description":
                if not self.meta_description:
                    self.meta_description = attr_dict.get("content", "").strip()
        elif tag == "link":
            rel = attr_dict.get("rel", "").lower()
            if rel == "canonical":
                self.canonical_url = attr_dict.get("href", "").strip()
        elif tag == "a":
            href = attr_dict.get("href")
            if href:
                # Filter out javascript, mailto, tel links
                if not href.startswith(("javascript:", "mailto:", "tel:", "#")):
                    self.links.append(href.strip())

    def handle_endtag(self, tag: str):
        tag = tag.lower()
        if tag == "title":
            self.in_title = False
        elif tag in ["script", "style", "noscript", "svg", "header", "footer", "nav"]:
            self.in_script_or_style = False

    def handle_data(self, data: str):
        if self.in_title:
            self.title_parts.append(data)
        elif not self.in_script_or_style:
            text = data.strip()
            if text:
                self.body_parts.append(text)

    def get_title(self) -> str:
        return " ".join(self.title_parts).strip()

    def get_body(self) -> str:
        return " ".join(self.body_parts).strip()


def normalize_url(url: str, base_url: str = "") -> str:
    """Normalize and resolve relative URLs, stripping query fragments."""
    if base_url:
        url = urllib.parse.urljoin(base_url, url)

    parsed = urllib.parse.urlparse(url)
    # Reconstruct clean URL (scheme, netloc, path, params, query)
    scheme = parsed.scheme.lower()
    if scheme not in ("http", "https"):
        return ""

    netloc = parsed.netloc.lower()
    path = parsed.path
    if not path:
        path = "/"

    # Strip trailing fragment `#`
    clean_url = urllib.parse.urlunparse((scheme, netloc, path, parsed.params, parsed.query, ""))
    return clean_url


def extract_domain(url: str) -> str:
    parsed = urllib.parse.urlparse(url)
    return parsed.netloc.lower()


class WebCrawler:
    """Multithreaded web crawler designed for high resilience on local networks and intranet."""

    def __init__(self, db: Database, max_threads: int = 5, timeout: int = 10, user_agent: str = DEFAULT_USER_AGENT):
        self.db = db
        self.max_threads = max_threads
        self.timeout = timeout
        self.user_agent = user_agent
        self.visited_urls: Set[str] = set()

    def fetch_url(self, url: str) -> Optional[Tuple[str, str, str]]:
        """Fetch URL content, return (html_content, content_type, final_url)."""
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": self.user_agent,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "fa,fa-IR,en-US,en;q=0.9",
            }
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                content_type = resp.headers.get_content_type()
                if "text/html" not in content_type and "application/xhtml+xml" not in content_type:
                    return None

                charset = resp.headers.get_content_charset() or "utf-8"
                raw_bytes = resp.read()
                try:
                    html_content = raw_bytes.decode(charset, errors="replace")
                except (LookupError, UnicodeDecodeError):
                    html_content = raw_bytes.decode("utf-8", errors="replace")

                return html_content, content_type, resp.geturl()
        except Exception as e:
            logger.debug(f"Failed to fetch {url}: {e}")
            return None

    def parse_html(self, html_content: str, base_url: str) -> Tuple[str, str, str, List[str]]:
        """Parse HTML to extract title, description, body text, and resolved link URLs."""
        parser = HTMLTextExtractor()
        try:
            parser.feed(html_content)
        except Exception as e:
            logger.debug(f"HTML parsing warning for {base_url}: {e}")

        title = parser.get_title() or base_url
        description = parser.meta_description
        body = parser.get_body()

        resolved_links = []
        for link in parser.links:
            norm = normalize_url(link, base_url)
            if norm:
                resolved_links.append(norm)

        return title, description, body, resolved_links

    def crawl_seed(self, seed_url: str, max_pages: int = 50, max_depth: int = 2) -> int:
        """Crawl starting from seed_url up to max_pages and max_depth."""
        normalized_seed = normalize_url(seed_url)
        if not normalized_seed:
            return 0

        queue: List[Tuple[str, int]] = [(normalized_seed, 0)]
        indexed_count = 0

        with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            while queue and indexed_count < max_pages:
                current_batch = []
                while queue and len(current_batch) < self.max_threads:
                    url, depth = queue.pop(0)
                    if url in self.visited_urls:
                        continue
                    self.visited_urls.add(url)
                    current_batch.append((url, depth))

                if not current_batch:
                    break

                futures = {executor.submit(self.fetch_url, url): (url, depth) for url, depth in current_batch}

                for future in futures:
                    url, depth = futures[future]
                    result = future.result()
                    if not result:
                        continue

                    html_content, _, final_url = result
                    title, description, body, links = self.parse_html(html_content, final_url)

                    if len(body) < 10:  # Skip empty or negligible pages
                        continue

                    domain = extract_domain(final_url)
                    updated = self.db.add_or_update_page(
                        url=final_url,
                        domain=domain,
                        title=title,
                        description=description,
                        raw_body=body
                    )
                    if updated:
                        indexed_count += 1

                    # Queue discovered links if depth limit is not reached
                    if depth < max_depth:
                        for link_url in links:
                            if link_url not in self.visited_urls:
                                queue.append((link_url, depth + 1))

        return indexed_count
