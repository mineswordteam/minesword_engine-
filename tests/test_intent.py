import unittest
from minesword.intent import detect_query_intent, QueryIntent


class TestIntent(unittest.TestCase):

    def test_download_intent(self):
        self.assertEqual(detect_query_intent("دانلود کالاف دیوتی"), QueryIntent.DOWNLOAD)

    def test_review_intent(self):
        self.assertEqual(detect_query_intent("بهترین لپ تاپ برای برنامه نویسی"), QueryIntent.REVIEW_GUIDE)

    def test_sports_intent(self):
        self.assertEqual(detect_query_intent("اخبار پرسپولیس و استقلال"), QueryIntent.SPORTS)


if __name__ == '__main__':
    unittest.main()
