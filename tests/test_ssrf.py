import unittest
from unittest.mock import patch, MagicMock
import os
import sys

# Add src to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from satya.core.scraper import Scraper

class TestSSRFProtection(unittest.TestCase):
    def setUp(self):
        self.scraper = Scraper()

    @patch("satya.core.scraper.requests.get")
    def test_fetch_unsafe_url_localhost(self, mock_get):
        url = "http://localhost/admin"
        result = self.scraper.fetch_and_save(url)
        self.assertIsNone(result)
        mock_get.assert_not_called()

    @patch("satya.core.scraper.requests.get")
    def test_fetch_unsafe_url_private_ip(self, mock_get):
        url = "http://192.168.1.1/config"
        result = self.scraper.fetch_and_save(url)
        self.assertIsNone(result)
        mock_get.assert_not_called()

    @patch("satya.core.scraper.requests.get")
    def test_fetch_unsafe_url_metadata(self, mock_get):
        url = "http://169.254.169.254/latest/meta-data/"
        result = self.scraper.fetch_and_save(url)
        self.assertIsNone(result)
        mock_get.assert_not_called()

if __name__ == "__main__":
    unittest.main()
