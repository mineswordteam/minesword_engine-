"""WSGI Web Server and REST API module for Minesword search engine."""

import json
import os
import urllib.parse
from wsgiref.simple_server import make_server
from typing import Dict, Any, Callable
from minesword.db import Database
from minesword.search_engine import SearchEngine
from minesword.crawler import WebCrawler


class MineswordServer:
    """WSGI web application serving REST APIs and single-page frontend."""

    def __init__(self, db_path: str = "minesword.db"):
        self.db = Database(db_path)
        self.search_engine = SearchEngine(self.db)
        self.crawler = WebCrawler(self.db)
        self.static_dir = os.path.join(os.path.dirname(__file__), "static")

    def __call__(self, environ: Dict[str, Any], start_response: Callable) -> list:
        path = environ.get("PATH_INFO", "/")
        method = environ.get("REQUEST_METHOD", "GET").upper()

        if path == "/" or path == "/index.html":
            return self.serve_file("index.html", "text/html; charset=utf-8", start_response)

        if path == "/api/search" and method == "GET":
            return self.handle_search(environ, start_response)

        if path == "/api/suggest" and method == "GET":
            return self.handle_suggest(environ, start_response)

        if path == "/api/status" and method == "GET":
            return self.handle_status(environ, start_response)

        if path == "/api/index" and method == "POST":
            return self.handle_index(environ, start_response)

        # 404 Not Found
        start_response("404 Not Found", [("Content-Type", "text/plain; charset=utf-8")])
        return [b"404 Not Found"]

    def serve_file(self, filename: str, content_type: str, start_response: Callable) -> list:
        filepath = os.path.join(self.static_dir, filename)
        if not os.path.exists(filepath):
            start_response("404 Not Found", [("Content-Type", "text/plain; charset=utf-8")])
            return [b"File not found"]

        with open(filepath, "rb") as f:
            content = f.read()

        start_response("200 OK", [
            ("Content-Type", content_type),
            ("Content-Length", str(len(content)))
        ])
        return [content]

    def json_response(self, data: Any, start_response: Callable, status: str = "200 OK") -> list:
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        start_response(status, [
            ("Content-Type", "application/json; charset=utf-8"),
            ("Content-Length", str(len(body)))
        ])
        return [body]

    def handle_search(self, environ: Dict[str, Any], start_response: Callable) -> list:
        query_params = urllib.parse.parse_qs(environ.get("QUERY_STRING", ""))
        q = query_params.get("q", [""])[0]
        try:
            page = int(query_params.get("page", ["1"])[0])
        except ValueError:
            page = 1

        try:
            page_size = int(query_params.get("page_size", ["10"])[0])
        except ValueError:
            page_size = 10

        res = self.search_engine.search(query=q, page=page, page_size=page_size)
        return self.json_response(res, start_response)

    def handle_suggest(self, environ: Dict[str, Any], start_response: Callable) -> list:
        query_params = urllib.parse.parse_qs(environ.get("QUERY_STRING", ""))
        q = query_params.get("q", [""])[0]
        try:
            limit = int(query_params.get("limit", ["8"])[0])
        except ValueError:
            limit = 8

        suggestions = self.search_engine.suggest(prefix=q, limit=limit)
        return self.json_response({"query": q, "suggestions": suggestions}, start_response)

    def handle_status(self, environ: Dict[str, Any], start_response: Callable) -> list:
        total = self.db.get_total_pages()
        return self.json_response({"status": "ok", "total_pages": total}, start_response)

    def handle_index(self, environ: Dict[str, Any], start_response: Callable) -> list:
        try:
            content_length = int(environ.get("CONTENT_LENGTH", 0))
            body = environ["wsgi.input"].read(content_length)
            payload = json.loads(body.decode("utf-8"))
        except Exception:
            return self.json_response({"error": "Invalid JSON request"}, start_response, status="400 Bad Request")

        url = payload.get("url", "").strip()
        depth = int(payload.get("depth", 2))
        max_pages = int(payload.get("max_pages", 30))

        if not url:
            return self.json_response({"error": "URL parameter required"}, start_response, status="400 Bad Request")

        count = self.crawler.crawl_seed(seed_url=url, max_pages=max_pages, max_depth=depth)
        return self.json_response({"message": f"خزش انجام شد. {count} صفحه جدید اندکس گردید.", "indexed": count}, start_response)


def run_server(host: str = "0.0.0.0", port: int = 8080, db_path: str = "minesword.db"):
    app = MineswordServer(db_path=db_path)
    print(f"Minesword Server running on http://{host}:{port}")
    httpd = make_server(host, port, app)
    httpd.serve_forever()


if __name__ == "__main__":
    run_server()
