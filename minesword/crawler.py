"""Robust web crawler with NIN priority, robots.txt, sitemap/RSS discovery for Minesword Engine."""

import re
import time
import urllib.parse
import urllib.request
import urllib.robotparser
from html.parser import HTMLParser
from typing import List, Set, Dict, Any, Optional
from minesword.db import Database
from minesword.sitemap_rss import fetch_and_parse_sitemap, fetch_and_parse_rss


def normalize_url(url: str, base_url: str = "") -> str:
    """Normalize and resolve relative or absolute URLs."""
    if not url:
        return ""
    if base_url:
        url = urllib.parse.urljoin(base_url, url)
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in ['http', 'https']:
        return ""
    return urllib.parse.urlunparse((parsed.scheme, parsed.netloc, parsed.path, '', parsed.query, ''))


class HTMLTextExtractor(HTMLParser):
    """HTML parser extracting title, canonical URL, headings, description, and links."""

    def __init__(self):
        super().__init__()
        self.title_parts: List[str] = []
        self.heading_parts: List[str] = []
        self.body_parts: List[str] = []
        self.description: str = ""
        self.canonical_url: str = ""
        self.links: Set[str] = set()

        self.in_title = False
        self.in_heading = False
        self.ignored_tags_count = 0

    def handle_starttag(self, tag: str, attrs: List[tuple]):
        tag_lower = tag.lower()
        if tag_lower in ['script', 'style', 'noscript', 'header', 'footer', 'nav']:
            self.ignored_tags_count += 1
            return

        if tag_lower == 'title':
            self.in_title = True
        elif tag_lower in ['h1', 'h2', 'h3']:
            self.in_heading = True
        elif tag_lower == 'link':
            attr_dict = dict(attrs)
            if attr_dict.get('rel') == 'canonical':
                self.canonical_url = attr_dict.get('href', '')
        elif tag_lower == 'meta':
            attr_dict = dict(attrs)
            if attr_dict.get('name', '').lower() == 'description':
                self.description = attr_dict.get('content', '')
        elif tag_lower == 'a':
            attr_dict = dict(attrs)
            href = attr_dict.get('href')
            if href:
                self.links.add(href)

    def handle_endtag(self, tag: str):
        tag_lower = tag.lower()
        if tag_lower in ['script', 'style', 'noscript', 'header', 'footer', 'nav']:
            if self.ignored_tags_count > 0:
                self.ignored_tags_count -= 1
            return

        if tag_lower == 'title':
            self.in_title = False
        elif tag_lower in ['h1', 'h2', 'h3']:
            self.in_heading = False

    def handle_data(self, data: str):
        if self.ignored_tags_count > 0:
            return
        text = data.strip()
        if not text:
            return

        if self.in_title:
            self.title_parts.append(text)
        elif self.in_heading:
            self.heading_parts.append(text)
        else:
            self.body_parts.append(text)

    def get_title(self) -> str:
        return " ".join(self.title_parts).strip()

    def get_headings(self) -> str:
        return " ".join(self.heading_parts).strip()

    def get_body_text(self) -> str:
        return " ".join(self.body_parts).strip()

    def get_body(self) -> str:
        return self.get_body_text()


class WebCrawler:
    """NIN-first web crawler supporting robots.txt, canonical URLs, rate limits, and feed discovery."""

    def __init__(
        self,
        db: Database,
        iran_priority: bool = True,
        allowed_domains: Optional[List[str]] = None,
        blocked_domains: Optional[List[str]] = None
    ):
        self.db = db
        self.iran_priority = iran_priority
        self.allowed_domains = [d.lower() for d in (allowed_domains or [])]
        self.blocked_domains = [d.lower() for d in (blocked_domains or [])]
        self.robots_cache: Dict[str, urllib.robotparser.RobotFileParser] = {}
        self.last_domain_crawl: Dict[str, float] = {}

    def is_domain_allowed(self, domain: str) -> bool:
        domain = domain.lower()
        if any(b in domain for b in self.blocked_domains):
            return False
        if self.allowed_domains and not any(a in domain for a in self.allowed_domains):
            return False
        return True

    def get_robots_parser(self, domain: str) -> urllib.robotparser.RobotFileParser:
        if domain in self.robots_cache:
            return self.robots_cache[domain]

        parser = urllib.robotparser.RobotFileParser()
        parser.set_url(f"https://{domain}/robots.txt")
        try:
            parser.read()
        except Exception:
            pass
        self.robots_cache[domain] = parser
        return parser

    def can_fetch(self, url: str) -> bool:
        parsed = urllib.parse.urlparse(url)
        domain = parsed.netloc.lower()
        if not self.is_domain_allowed(domain):
            return False

        parser = self.get_robots_parser(domain)
        try:
            return parser.can_fetch("MineswordCrawler", url)
        except Exception:
            return True

    def crawl_url(self, url: str, timeout: int = 5) -> Optional[Dict[str, Any]]:
        if not self.can_fetch(url):
            return None

        parsed = urllib.parse.urlparse(url)
        domain = parsed.netloc.lower()

        last_time = self.last_domain_crawl.get(domain, 0)
        if time.time() - last_time < 0.3:
            time.sleep(0.3)
        self.last_domain_crawl[domain] = time.time()

        try:
            req = urllib.request.Request(url, headers={"User-Agent": "MineswordCrawler/2.0"})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                if resp.status != 200:
                    return None

                content_type = resp.headers.get("Content-Type", "")
                if "text/html" not in content_type.lower():
                    return None

                html_content = resp.read().decode('utf-8', errors='ignore')

            extractor = HTMLTextExtractor()
            extractor.feed(html_content)

            title = extractor.get_title() or domain
            headings = extractor.get_headings()
            body_text = extractor.get_body_text()
            description = extractor.description
            canonical_url = extractor.canonical_url or url

            domain_auth = 1.3 if (self.iran_priority and (domain.endswith('.ir') or '.ir/' in domain)) else 1.0

            page_id = self.db.add_or_update_page(
                url=url,
                domain=domain,
                title=title,
                description=description,
                raw_body=body_text,
                canonical_url=canonical_url,
                headings=headings,
                domain_authority=domain_auth
            )

            resolved_links = set()
            for link in extractor.links:
                abs_url = normalize_url(link, url)
                if abs_url:
                    resolved_links.add(abs_url)

            return {
                "id": page_id,
                "url": url,
                "domain": domain,
                "title": title,
                "description": description,
                "body_text": body_text,
                "links": resolved_links
            }
        except Exception:
            return None

    def crawl_seed(self, seed_url: str, max_pages: int = 20, max_depth: int = 2):
        visited: Set[str] = set()
        queue: List[tuple] = [(seed_url, 1)]

        try:
            domain = urllib.parse.urlparse(seed_url).netloc
            sitemap_urls = fetch_and_parse_sitemap(f"https://{domain}/sitemap.xml")
            for u in sitemap_urls[:15]:
                queue.append((u, 2))

            rss_urls = fetch_and_parse_rss(f"https://{domain}/rss")
            for u in rss_urls[:10]:
                queue.append((u, 2))
        except Exception:
            pass

        count = 0
        while queue and count < max_pages:
            url, depth = queue.pop(0)
            if url in visited or depth > max_depth:
                continue

            visited.add(url)
            res = self.crawl_url(url)
            if res:
                count += 1
                if depth < max_depth:
                    for link in res.get("links", []):
                        if link not in visited:
                            queue.append((link, depth + 1))
