"""Unit test suite for SearchEngine query parsing and ranking."""

import unittest
import os
from minesword.db import Database
from minesword.search_engine import SearchEngine


class TestSearchEngine(unittest.TestCase):

    def setUp(self):
        self.db_path = "test_engine.db"
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        self.db = Database(self.db_path)
        self.engine = SearchEngine(self.db)

        # Seed sample data
        self.db.add_or_update_page(
            url="https://varzesh3.com/news/football",
            domain="varzesh3.com",
            title="فوتبال ایران در جام جهانی",
            description="اخبار فوتبال",
            raw_body="تیم ملی فوتبال ایران موفق شد نتایج درخشانی در مسابقات آسیایی کسب کند."
        )
        self.db.add_or_update_page(
            url="https://zoomit.ir/tech/intranet",
            domain="zoomit.ir",
            title="شبکه ملی اطلاعات و اینترنت کشور",
            description="بررسی اینترنت ملی",
            raw_body="راه اندازی سرویس های بومی در زمان قطعی اینترنت جهانی و عملکرد شبکه ملی اطلاعات."
        )

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_search_relevance(self):
        res = self.engine.search("شبکه ملی")
        self.assertGreater(res["total"], 0)
        self.assertEqual(res["results"][0]["domain"], "zoomit.ir")

    def test_site_filter(self):
        res = self.engine.search("ایران site:varzesh3.com")
        self.assertEqual(res["total"], 1)
        self.assertEqual(res["results"][0]["domain"], "varzesh3.com")

    def test_exact_phrase(self):
        res = self.engine.search('"تیم ملی"')
        self.assertEqual(res["total"], 1)

    def test_empty_query(self):
        res = self.engine.search("   ")
        self.assertEqual(res["total"], 0)


if __name__ == "__main__":
    unittest.main()
