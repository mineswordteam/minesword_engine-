"""Command Line Interface (CLI) module for Minesword search engine."""

import argparse
import sys
import json
from minesword.db import Database
from minesword.search_engine import SearchEngine
from minesword.crawler import WebCrawler
from minesword.server import run_server


def main():
    parser = argparse.ArgumentParser(
        prog="minesword",
        description="Minesword Search Engine - Powerful Persian/English Intranet Search Engine"
    )
    parser.add_argument("--db", default="minesword.db", help="Path to SQLite database file (default: minesword.db)")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Serve command
    serve_parser = subparsers.add_parser("serve", help="Start the web server UI and REST API")
    serve_parser.add_argument("--host", default="0.0.0.0", help="Host address (default: 0.0.0.0)")
    serve_parser.add_argument("--port", type=int, default=8080, help="Port number (default: 8080)")

    # Crawl command
    crawl_parser = subparsers.add_parser("crawl", help="Crawl a URL and index web pages into the database")
    crawl_parser.add_argument("url", help="Target URL to crawl (e.g., https://example.ir)")
    crawl_parser.add_argument("--max-pages", type=int, default=50, help="Maximum pages to index")
    crawl_parser.add_argument("--depth", type=int, default=2, help="Crawl depth level")

    # Search command
    search_parser = subparsers.add_parser("search", help="Perform search query directly from CLI")
    search_parser.add_argument("query", help="Search query string")
    search_parser.add_argument("--page", type=int, default=1, help="Page number")
    search_parser.add_argument("--json", action="store_true", help="Output results in JSON format")

    # Status command
    subparsers.add_parser("status", help="Show total indexed pages in database")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    db = Database(args.db)

    if args.command == "serve":
        run_server(host=args.host, port=args.port, db_path=args.db)

    elif args.command == "crawl":
        print(f"[*] Starting crawler for seed: {args.url} (max_pages={args.max_pages}, depth={args.depth})")
        crawler = WebCrawler(db)
        count = crawler.crawl_seed(seed_url=args.url, max_pages=args.max_pages, max_depth=args.depth)
        print(f"[+] Crawling complete. Successfully indexed {count} pages into '{args.db}'.")

    elif args.command == "search":
        engine = SearchEngine(db)
        res = engine.search(query=args.query, page=args.page)

        if args.json:
            print(json.dumps(res, ensure_ascii=False, indent=2))
        else:
            print(f"\n--- Results for '{res['query']}' ({res['total']} found, Page {res['page']}/{res['total_pages']}) ---\n")
            if not res["results"]:
                print("No results found.")
            for i, item in enumerate(res["results"], start=1):
                print(f"{i}. {item['title']}")
                print(f"   URL: {item['url']}")
                print(f"   Snippet: {item['snippet']}")
                print(f"   Score: {item['relevance']}\n")

    elif args.command == "status":
        total = db.get_total_pages()
        print(f"Minesword Database Status ('{args.db}'):")
        print(f"Total indexed pages: {total}")


if __name__ == "__main__":
    main()
