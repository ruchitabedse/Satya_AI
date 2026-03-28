import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# The conftest.py in tests/ already mocks requests
import requests
import socket

from satya.core.scraper import Scraper

class TestSSRF(unittest.TestCase):
    def setUp(self):
        self.scraper = Scraper()

    def test_scraper_blocks_localhost(self):
        url = "http://127.0.0.1:5000/admin"
        result = self.scraper.fetch_and_save(url)
        self.assertIsNone(result, "Scraper should have blocked the local URL")

    def test_scraper_blocks_private_ip(self):
        url = "http://192.168.1.1/config"
        result = self.scraper.fetch_and_save(url)
        self.assertIsNone(result, "Scraper should have blocked the private IP URL")

    @patch('satya.core.scraper.requests.get')
    @patch('satya.core.scraper.socket.gethostbyname')
    @patch('satya.core.scraper.BeautifulSoup')
    def test_scraper_allows_public_url(self, mock_bs, mock_dns, mock_get):
        # Setup mock to return a simple response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"<html><title>Public</title><body>Public Data</body></html>"
        mock_response.text = "<html><title>Public</title><body>Public Data</body></html>"
        mock_get.return_value = mock_response
        mock_dns.return_value = "93.184.216.34"

        mock_soup = MagicMock()
        mock_soup.title.string.strip.return_value = "Public"
        mock_bs.return_value = mock_soup

        url = "http://example.com"
        result = self.scraper.fetch_and_save(url)
        self.assertIsNotNone(result)
        self.assertEqual(result, "Public.md")

    @patch('satya.core.scraper.requests.get')
    @patch('satya.core.scraper.socket.gethostbyname')
    def test_scraper_blocks_unsafe_redirect(self, mock_dns, mock_get):
        # Initial request
        mock_resp1 = MagicMock()
        mock_resp1.status_code = 302
        mock_resp1.headers = {'Location': 'http://127.0.0.1/secret'}

        mock_get.return_value = mock_resp1
        mock_dns.side_effect = ["1.1.1.1", "127.0.0.1"]

        url = "http://public-service.com/redirect"
        result = self.scraper.fetch_and_save(url)
        self.assertIsNone(result, "Scraper should have blocked the unsafe redirect")

if __name__ == "__main__":
    unittest.main()
