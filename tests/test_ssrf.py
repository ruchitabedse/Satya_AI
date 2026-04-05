import unittest
from unittest.mock import patch, MagicMock
import socket
import ipaddress
from satya.core.scraper import _is_safe_url, Scraper

class TestSSRFProtection(unittest.TestCase):

    @patch('socket.getaddrinfo')
    def test_is_safe_url_public_ip(self, mock_getaddrinfo):
        # Mock public IP resolution
        mock_getaddrinfo.return_value = [(socket.AF_INET, socket.SOCK_STREAM, 6, '', ('93.184.216.34', 0))]
        self.assertTrue(_is_safe_url("http://example.com"))

    @patch('socket.getaddrinfo')
    def test_is_safe_url_private_ip(self, mock_getaddrinfo):
        # Mock private IP resolution
        mock_getaddrinfo.return_value = [(socket.AF_INET, socket.SOCK_STREAM, 6, '', ('192.168.1.1', 0))]
        self.assertFalse(_is_safe_url("http://internal.service"))

    @patch('socket.getaddrinfo')
    def test_is_safe_url_loopback_ip(self, mock_getaddrinfo):
        # Mock loopback IP resolution
        mock_getaddrinfo.return_value = [(socket.AF_INET, socket.SOCK_STREAM, 6, '', ('127.0.0.1', 0))]
        self.assertFalse(_is_safe_url("http://localhost"))

    @patch('socket.getaddrinfo')
    def test_is_safe_url_ipv6_loopback(self, mock_getaddrinfo):
        # Mock IPv6 loopback resolution
        mock_getaddrinfo.return_value = [(socket.AF_INET6, socket.SOCK_STREAM, 6, '', ('::1', 0, 0, 0))]
        self.assertFalse(_is_safe_url("http://[::1]"))

    def test_is_safe_url_invalid_scheme(self):
        self.assertFalse(_is_safe_url("ftp://example.com"))
        self.assertFalse(_is_safe_url("file:///etc/passwd"))

    @patch('satya.core.scraper._is_safe_url')
    @patch('satya.core.scraper.requests.get')
    def test_fetch_and_save_blocks_unsafe_url(self, mock_get, mock_is_safe):
        mock_is_safe.return_value = False
        scraper = Scraper()
        result = scraper.fetch_and_save("http://unsafe.com")
        self.assertIsNone(result)
        mock_get.assert_not_called()

    @patch('satya.core.scraper._is_safe_url')
    @patch('satya.core.scraper.requests.get')
    def test_fetch_and_save_follows_safe_redirect(self, mock_get, mock_is_safe):
        # Mock initial URL safe, redirect URL safe
        mock_is_safe.side_effect = [True, True]

        # Mock redirect response
        mock_resp1 = MagicMock()
        mock_resp1.status_code = 302
        mock_resp1.headers = {'Location': 'https://safe.com/final'}

        # Mock final response
        mock_resp2 = MagicMock()
        mock_resp2.status_code = 200
        mock_resp2.content = b"<html><title>Final</title><body>Content</body></html>"
        mock_resp2.text = "<html><title>Final</title><body>Content</body></html>"
        # Explicitly mock BeautifulSoup title and string for more predictable behavior
        mock_resp2.soup = MagicMock()
        mock_resp2.soup.title.string = "Final"

        mock_get.side_effect = [mock_resp1, mock_resp2]

        with patch('satya.core.storage.save_markdown') as mock_save, \
             patch('satya.core.scraper.BeautifulSoup') as mock_bs:
            mock_bs.return_value = mock_resp2.soup
            mock_save.return_value = "path/to/Final.md"
            scraper = Scraper()
            result = scraper.fetch_and_save("http://safe.com/start")
            self.assertEqual(result, "Final.md")
            self.assertEqual(mock_get.call_count, 2)

    @patch('satya.core.scraper._is_safe_url')
    @patch('satya.core.scraper.requests.get')
    def test_fetch_and_save_blocks_unsafe_redirect(self, mock_get, mock_is_safe):
        # Mock initial URL safe, redirect URL unsafe
        mock_is_safe.side_effect = [True, False]

        # Mock redirect response
        mock_resp1 = MagicMock()
        mock_resp1.status_code = 302
        mock_resp1.headers = {'Location': 'http://169.254.169.254/metadata'}

        mock_get.return_value = mock_resp1

        scraper = Scraper()
        result = scraper.fetch_and_save("http://safe.com/start")
        self.assertIsNone(result)
        self.assertEqual(mock_get.call_count, 1)
