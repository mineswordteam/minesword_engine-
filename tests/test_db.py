"""Unit test suite for SQLite FTS5 database module."""

import unittest
import os
from minesword.db import Database


class TestDatabase(unittest.TestCase):

    def setUp(self):
        self.db_path = "test_db.db"
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        self.db = Database(self.db_path)

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_add_and_search_page(self):
        added = self.db.add_or_update_page(
            url="https://test.ir/page1",
            domain="test.ir",
            title="آموزش پایتون و طراحی موتور جستجو",
            description="دوره آموزش کامل پایتون",
            raw_body="این یک دوره آموزشی جامع پایتون برای ساخت موتور جستجوی پیشرفته است."
        )
        self.assertTrue(added)
        self.assertEqual(self.db.get_total_pages(), 1)

        results = self.db.search_fts("پایتون")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "آموزش پایتون و طراحی موتور جستجو")

    def test_deduplication(self):
        url = "https://test.ir/duplicate"
        added1 = self.db.add_or_update_page(url, "test.ir", "عنوان", "توضیح", "متن تکراری برای تست")
        self.assertTrue(added1)

        # Second insert with identical content should return False
        added2 = self.db.add_or_update_page(url, "test.ir", "عنوان", "توضیح", "متن تکراری برای تست")
        self.assertFalse(added2)
        self.assertEqual(self.db.get_total_pages(), 1)

    def test_suggestions(self):
        self.db.add_or_update_page("https://a.com", "a.com", "فناوری و هوش مصنوعی", "", "کاربردهای هوش مصنوعی در ایران")
        suggestions = self.db.get_suggestions("هوش")
        self.assertIn("هوش", suggestions)


if __name__ == "__main__":
    unittest.main()
