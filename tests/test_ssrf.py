import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Ensure src is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from satya.core.scraper import Scraper

class TestSSRF(unittest.TestCase):
    def setUp(self):
        self.scraper = Scraper()

    @patch("requests.get")
    def test_ssrf_internal_ip(self, mock_get):
        url = "http://192.168.1.1/admin"
        result = self.scraper.fetch_and_save(url)
        self.assertIsNone(result)
        mock_get.assert_not_called()

    @patch("requests.get")
    def test_ssrf_loopback(self, mock_get):
        url = "http://127.0.0.1:5000/internal"
        result = self.scraper.fetch_and_save(url)
        self.assertIsNone(result)
        mock_get.assert_not_called()

    @patch("requests.get")
    def test_ssrf_loopback_hostname(self, mock_get):
        url = "http://localhost:5000/internal"
        result = self.scraper.fetch_and_save(url)
        self.assertIsNone(result)
        mock_get.assert_not_called()

    @patch("requests.get")
    @patch("socket.gethostbyname")
    def test_ssrf_redirect_chain_vulnerable(self, mock_gethost, mock_get):
        # Initial URL is fine
        url = "http://example.com/redirect"
        # Initial IP is fine, second is localhost
        mock_gethost.side_effect = ["93.184.216.34", "127.0.0.1"]

        # First hop is fine, but it redirects to localhost
        resp1 = MagicMock()
        resp1.is_redirect = True
        resp1.headers = {'Location': 'http://localhost/admin'}

        mock_get.side_effect = [resp1]

        result = self.scraper.fetch_and_save(url)
        self.assertIsNone(result)
        # Should call once for initial, then block the second due to localhost IP
        self.assertEqual(mock_get.call_count, 1)

    @patch("requests.get")
    def test_safe_url(self, mock_get):
        url = "http://www.google.com"

        resp = MagicMock()
        resp.is_redirect = False
        resp.content = b"<html><title>Google</title><body>Hello</body></html>"
        resp.text = "<html><title>Google</title><body>Hello</body></html>"
        resp.status_code = 200
        mock_get.return_value = resp

        result = self.scraper.fetch_and_save(url)
        self.assertIsNotNone(result)
        # Verify requests.get was called with the original URL
        mock_get.assert_called_with(url, timeout=10, allow_redirects=False)

    @patch("requests.get")
    @patch("socket.gethostbyname")
    def test_relative_redirect(self, mock_gethost, mock_get):
        url = "http://example.com/page1"
        mock_gethost.return_value = "93.184.216.34" # example.com

        resp1 = MagicMock()
        resp1.is_redirect = True
        resp1.headers = {'Location': '/page2'}

        resp2 = MagicMock()
        resp2.is_redirect = False
        resp2.content = b"<html><title>Page 2</title></html>"
        resp2.text = "<html><title>Page 2</title></html>"
        resp2.status_code = 200

        mock_get.side_effect = [resp1, resp2]

        result = self.scraper.fetch_and_save(url)
        self.assertIsNotNone(result)
        self.assertEqual(mock_get.call_count, 2)
        # Verify the second call used the correctly resolved relative URL
        self.assertEqual(mock_get.call_args_list[1][0][0], "http://example.com/page2")

if __name__ == "__main__":
    unittest.main()
