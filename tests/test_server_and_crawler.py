"""Integration test suite for server endpoints and crawler module."""

import unittest
import json
import os
from minesword.server import MineswordServer
from minesword.crawler import HTMLTextExtractor, normalize_url


class TestServerAndCrawler(unittest.TestCase):

    def setUp(self):
        self.db_path = "test_integration.db"
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        self.app = MineswordServer(self.db_path)

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_html_parser(self):
        html = "<html><head><title>Test</title></head><body><p>Hello world</p><a href='/next'>Next</a></body></html>"
        parser = HTMLTextExtractor()
        parser.feed(html)
        self.assertEqual(parser.get_title(), "Test")
        self.assertEqual(parser.get_body(), "Hello world Next")
        self.assertIn("/next", parser.links)

    def test_url_normalization(self):
        norm = normalize_url("/category/tech?id=1#section", "https://example.ir/blog/")
        self.assertEqual(norm, "https://example.ir/category/tech?id=1")

    def test_server_status_api(self):
        def start_response(status, headers):
            self.assertEqual(status, "200 OK")

        env = {"PATH_INFO": "/api/status", "REQUEST_METHOD": "GET"}
        resp = self.app(env, start_response)
        data = json.loads(resp[0].decode("utf-8"))
        self.assertEqual(data["status"], "ok")
        self.assertGreater(data["total_pages"], 0)


if __name__ == "__main__":
    unittest.main()
