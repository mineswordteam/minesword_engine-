"""Database management layer using SQLite and FTS5 for full-text searching."""

import sqlite3
import os
import hashlib
from typing import Optional, Dict, List, Any
from minesword.normalizer import normalize_text, tokenize

INIT_SQL = """
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;

CREATE TABLE IF NOT EXISTS pages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT UNIQUE NOT NULL,
    domain TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    raw_body TEXT NOT NULL,
    normalized_title TEXT NOT NULL,
    normalized_body TEXT NOT NULL,
    content_hash TEXT UNIQUE NOT NULL,
    indexed_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE VIRTUAL TABLE IF NOT EXISTS pages_fts USING fts5(
    title,
    body,
    tokenize='unicode61 remove_diacritics 2'
);

CREATE TABLE IF NOT EXISTS term_suggestions (
    term TEXT PRIMARY KEY,
    frequency INTEGER DEFAULT 1
);
"""


class Database:
    """SQLite Database interface for Minesword search engine."""

    def __init__(self, db_path: str = "minesword.db"):
        self.db_path = db_path
        self._init_db()

    def get_connection(self) -> sqlite3.Connection:
        # Fallback to /tmp if current directory is read-only (e.g. Vercel)
        target_path = self.db_path
        if not target_path.startswith("/tmp/") and (os.getenv("VERCEL") or not os.access(".", os.W_OK)):
            target_path = os.path.join("/tmp", os.path.basename(self.db_path))

        conn = sqlite3.connect(target_path, timeout=10.0)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self.get_connection() as conn:
            conn.executescript(INIT_SQL)
            conn.commit()

        # Seed starter data if database is empty
        try:
            from minesword.seed_data import seed_database_if_empty
            seed_database_if_empty(self)
        except Exception:
            pass

    def add_or_update_page(self, url: str, domain: str, title: str, description: str, raw_body: str) -> bool:
        """Add or update a web page in the database. Returns True if inserted/updated."""
        if not url or not raw_body:
            return False

        norm_title = normalize_text(title or url)
        norm_body = normalize_text(raw_body)

        content_hash = hashlib.sha256((norm_title + "\n" + norm_body).encode('utf-8')).hexdigest()

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, content_hash FROM pages WHERE url = ?", (url,))
            existing = cursor.fetchone()

            if existing:
                page_id = existing["id"]
                if existing["content_hash"] == content_hash:
                    return False  # Content unchanged

                cursor.execute("""
                    UPDATE pages
                    SET domain = ?, title = ?, description = ?, raw_body = ?,
                        normalized_title = ?, normalized_body = ?, content_hash = ?, indexed_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (domain, title, description, raw_body, norm_title, norm_body, content_hash, page_id))

                cursor.execute("DELETE FROM pages_fts WHERE rowid = ?", (page_id,))
                cursor.execute("INSERT INTO pages_fts(rowid, title, body) VALUES (?, ?, ?)", (page_id, norm_title, norm_body))
            else:
                cursor.execute("""
                    INSERT INTO pages (url, domain, title, description, raw_body, normalized_title, normalized_body, content_hash)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (url, domain, title, description, raw_body, norm_title, norm_body, content_hash))
                page_id = cursor.lastrowid
                cursor.execute("INSERT INTO pages_fts(rowid, title, body) VALUES (?, ?, ?)", (page_id, norm_title, norm_body))

            # Update term suggestions frequency
            words = tokenize(norm_title) + tokenize(norm_body)
            words = [w for w in set(words) if len(w) >= 2 and not w.isdigit()]
            for word in words:
                cursor.execute("""
                    INSERT INTO term_suggestions (term, frequency) VALUES (?, 1)
                    ON CONFLICT(term) DO UPDATE SET frequency = frequency + 1
                """, (word,))

            conn.commit()
            return True

    def get_total_pages(self) -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM pages")
            return cursor.fetchone()[0]

    def get_page_by_url(self, url: str) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM pages WHERE url = ?", (url,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def search_fts(self, fts_query: str, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Search pages table using SQLite FTS5 index and return matching records with BM25 score."""
        sql = """
            SELECT
                p.id,
                p.url,
                p.domain,
                p.title,
                p.description,
                p.raw_body,
                p.indexed_at,
                bm25(pages_fts, 2.0, 1.0) AS score,
                snippet(pages_fts, 1, '<b>', '</b>', '...', 32) AS snippet
            FROM pages_fts f
            JOIN pages p ON f.rowid = p.id
            WHERE pages_fts MATCH ?
            ORDER BY score ASC
            LIMIT ? OFFSET ?
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(sql, (fts_query, limit, offset))
                return [dict(r) for r in cursor.fetchall()]
            except sqlite3.OperationalError as e:
                return []

    def get_suggestions(self, prefix: str, limit: int = 8) -> List[str]:
        """Return auto-suggestions matching prefix ordered by frequency."""
        norm_prefix = normalize_text(prefix)
        if not norm_prefix:
            return []

        sql = """
            SELECT term FROM term_suggestions
            WHERE term LIKE ? || '%'
            ORDER BY frequency DESC, length(term) ASC
            LIMIT ?
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (norm_prefix, limit))
            return [row["term"] for row in cursor.fetchall()]

    def close(self):
        pass
