"""SQLite database management with FTS5 full-text indexing for Minesword Engine."""

import sqlite3
import os
from typing import List, Dict, Any, Optional, Tuple, Union
from minesword.normalizer import normalize_text, tokenize
from minesword.dedup import compute_content_hash


INIT_SQL = """
CREATE TABLE IF NOT EXISTS pages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT UNIQUE NOT NULL,
    canonical_url TEXT,
    domain TEXT NOT NULL,
    title TEXT NOT NULL,
    headings TEXT,
    description TEXT,
    raw_body TEXT,
    language TEXT DEFAULT 'fa',
    publication_date TEXT,
    crawl_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata TEXT,
    content_hash TEXT,
    domain_authority REAL DEFAULT 1.0,
    normalized_title TEXT,
    normalized_body TEXT
);

CREATE VIRTUAL TABLE IF NOT EXISTS pages_fts USING fts5(
    title,
    headings,
    description,
    raw_body,
    content='pages',
    content_rowid='id',
    tokenize='unicode61'
);

CREATE TABLE IF NOT EXISTS suggestions (
    term TEXT PRIMARY KEY,
    frequency INTEGER DEFAULT 1
);

CREATE INDEX IF NOT EXISTS idx_domain ON pages(domain);
CREATE INDEX IF NOT EXISTS idx_content_hash ON pages(content_hash);
"""


class Database:
    """SQLite FTS5 database manager for indexing and querying web pages."""

    def __init__(self, db_path: str = "minesword.db"):
        self.db_path = db_path
        self._ensure_dir()
        self.init_db()

    def _ensure_dir(self):
        dirname = os.path.dirname(self.db_path)
        if dirname and not os.path.exists(dirname):
            os.makedirs(dirname, exist_ok=True)

    def get_connection(self) -> sqlite3.Connection:
        try:
            conn = sqlite3.connect(self.db_path)
        except sqlite3.OperationalError:
            fallback = "/tmp/minesword.db"
            conn = sqlite3.connect(fallback)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        with self.get_connection() as conn:
            conn.executescript(INIT_SQL)

            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(pages)")
            cols = {row["name"] for row in cursor.fetchall()}

            for col, col_type in [
                ("canonical_url", "TEXT"),
                ("headings", "TEXT"),
                ("language", "TEXT DEFAULT 'fa'"),
                ("publication_date", "TEXT"),
                ("metadata", "TEXT"),
                ("content_hash", "TEXT"),
                ("domain_authority", "REAL DEFAULT 1.0"),
                ("normalized_title", "TEXT"),
                ("normalized_body", "TEXT")
            ]:
                if col not in cols:
                    try:
                        cursor.execute(f"ALTER TABLE pages ADD COLUMN {col} {col_type}")
                    except Exception:
                        pass

            conn.commit()

    def add_or_update_page(
        self,
        url: str,
        domain: str,
        title: str,
        description: str = "",
        raw_body: str = "",
        canonical_url: str = None,
        headings: str = "",
        language: str = "fa",
        publication_date: str = None,
        metadata: str = None,
        domain_authority: float = 1.0
    ) -> bool:
        norm_title = normalize_text(title)
        norm_body = normalize_text(raw_body)
        c_hash = compute_content_hash(raw_body or title)
        c_url = canonical_url or url

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM pages WHERE url = ?", (url,))
            existing = cursor.fetchone()

            if existing:
                page_id = existing["id"]
                cursor.execute("""
                    UPDATE pages SET
                        canonical_url = ?, domain = ?, title = ?, headings = ?,
                        description = ?, raw_body = ?, language = ?, publication_date = ?,
                        metadata = ?, content_hash = ?, domain_authority = ?,
                        normalized_title = ?, normalized_body = ?
                    WHERE id = ?
                """, (c_url, domain, title, headings, description, raw_body, language,
                      publication_date, metadata, c_hash, domain_authority, norm_title, norm_body, page_id))
                is_new = False
            else:
                cursor.execute("""
                    INSERT INTO pages (
                        url, canonical_url, domain, title, headings, description,
                        raw_body, language, publication_date, metadata, content_hash,
                        domain_authority, normalized_title, normalized_body
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (url, c_url, domain, title, headings, description, raw_body, language,
                      publication_date, metadata, c_hash, domain_authority, norm_title, norm_body))
                page_id = cursor.lastrowid
                cursor.execute("""
                    INSERT INTO pages_fts (rowid, title, headings, description, raw_body)
                    VALUES (?, ?, ?, ?, ?)
                """, (page_id, title, headings, description, raw_body))
                is_new = True

            tokens = tokenize(title) + tokenize(description)
            for token in tokens:
                if len(token) >= 2:
                    cursor.execute("""
                        INSERT INTO suggestions (term, frequency) VALUES (?, 1)
                        ON CONFLICT(term) DO UPDATE SET frequency = frequency + 1
                    """, (token,))

            conn.commit()
            return is_new

    def search_fts(self, fts_query: str, limit: int = 150, offset: int = 0) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                sql = """
                    SELECT p.*, bm25(pages_fts) as score
                    FROM pages_fts f
                    JOIN pages p ON f.rowid = p.id
                    WHERE pages_fts MATCH ?
                    ORDER BY score ASC
                    LIMIT ? OFFSET ?
                """
                cursor.execute(sql, (fts_query, limit, offset))
                return [dict(row) for row in cursor.fetchall()]
            except sqlite3.OperationalError:
                return []

    def get_total_pages(self) -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as cnt FROM pages")
            row = cursor.fetchone()
            return row["cnt"] if row else 0

    def get_suggestions(self, prefix: str, limit: int = 8) -> List[str]:
        norm_prefix = normalize_text(prefix)
        if not norm_prefix:
            return []
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT term FROM suggestions
                WHERE term LIKE ? || '%'
                ORDER BY frequency DESC, length(term) ASC
                LIMIT ?
            """, (norm_prefix, limit))
            return [row["term"] for row in cursor.fetchall()]
