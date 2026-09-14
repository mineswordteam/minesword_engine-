import unittest
from minesword.sitemap_rss import fetch_and_parse_sitemap, fetch_and_parse_rss


class TestSitemapRSS(unittest.TestCase):

    def test_invalid_sitemap_url_graceful_handling(self):
        urls = fetch_and_parse_sitemap("https://invalid-non-existent-domain-test.ir/sitemap.xml")
        self.assertEqual(urls, [])

    def test_invalid_rss_url_graceful_handling(self):
        urls = fetch_and_parse_rss("https://invalid-non-existent-domain-test.ir/rss")
        self.assertEqual(urls, [])


if __name__ == '__main__':
    unittest.main()
