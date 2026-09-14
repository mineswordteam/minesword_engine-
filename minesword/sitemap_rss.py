"""Sitemap.xml and RSS/Atom feed parser for link discovery in Minesword Engine."""

import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from typing import List, Set


def fetch_and_parse_sitemap(sitemap_url: str, timeout: int = 5) -> List[str]:
    """Fetch and extract URLs from a sitemap.xml file."""
    urls = []
    try:
        req = urllib.request.Request(sitemap_url, headers={"User-Agent": "MineswordCrawler/2.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            content = resp.read()
            tree = ET.fromstring(content)
            for elem in tree.iter():
                if elem.tag.endswith('loc') and elem.text:
                    loc = elem.text.strip()
                    if loc.startswith('http'):
                        urls.append(loc)
    except Exception:
        pass
    return urls


def fetch_and_parse_rss(rss_url: str, timeout: int = 5) -> List[str]:
    """Fetch and extract URLs from an RSS or Atom feed."""
    urls = []
    try:
        req = urllib.request.Request(rss_url, headers={"User-Agent": "MineswordCrawler/2.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            content = resp.read()
            tree = ET.fromstring(content)
            for elem in tree.iter():
                if (elem.tag.endswith('link') or elem.tag.endswith('guid')) and elem.text:
                    loc = elem.text.strip()
                    if loc.startswith('http'):
                        urls.append(loc)
                elif elem.tag.endswith('link') and 'href' in elem.attrib:
                    href = elem.attrib['href'].strip()
                    if href.startswith('http'):
                        urls.append(href)
    except Exception:
        pass
    return urls
