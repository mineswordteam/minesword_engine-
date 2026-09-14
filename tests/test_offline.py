import unittest, os, tempfile
from minesword.db import Database
from minesword.search_engine import SearchEngine


class TestOfflineSearch(unittest.TestCase):

    def setUp(self):
        self.db_path = tempfile.mktemp('.db')
        self.db = Database(self.db_path)
        self.db.add_or_update_page(
            url="https://offline-test.ir/post-1",
            domain="offline-test.ir",
            title="صفحه تست آفلاین شبکه ملی",
            description="جستجوی بومی بدون نیاز به اینترنت خارجی",
            raw_body="موتور جستجوی ماین سورد قادر به کار در شرایط قطعی اینترنت بین المللی است."
        )
        self.se = SearchEngine(self.db)

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_local_offline_search(self):
        res = self.se.search("شبکه ملی", page=1)
        self.assertGreaterEqual(res["total"], 1)
        self.assertEqual(res["results"][0]["domain"], "offline-test.ir")


if __name__ == '__main__':
    unittest.main()
