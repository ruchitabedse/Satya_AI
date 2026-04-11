import unittest
from unittest.mock import patch, MagicMock
from satya.core.scraper import Scraper
import os

class TestSSRFProtection(unittest.TestCase):
    def setUp(self):
        self.scraper = Scraper()

    @patch('satya.core.scraper.requests.get')
    def test_fetch_and_save_with_local_ip(self, mock_get):
        # We expect this to be blocked by the security fix
        url = "http://127.0.0.1/admin"
        result = self.scraper.fetch_and_save(url)

        # In a vulnerable state, it might attempt to call requests.get
        # After the fix, it should return None and NOT call requests.get
        self.assertIsNone(result)
        mock_get.assert_not_called()

    @patch('satya.core.scraper.requests.get')
    def test_fetch_and_save_with_private_ip(self, mock_get):
        url = "http://192.168.1.1/config"
        result = self.scraper.fetch_and_save(url)
        self.assertIsNone(result)
        mock_get.assert_not_called()

    @patch('satya.core.scraper.requests.get')
    def test_fetch_and_save_with_unsafe_scheme(self, mock_get):
        url = "file:///etc/passwd"
        result = self.scraper.fetch_and_save(url)
        self.assertIsNone(result)
        mock_get.assert_not_called()

    @patch('satya.core.scraper.socket.gethostbyname')
    @patch('satya.core.scraper.requests.get')
    def test_fetch_and_save_with_valid_url(self, mock_get, mock_gethost):
        # Mock DNS resolution to a public IP
        mock_gethost.return_value = "8.8.8.8"

        # Mock a successful response for a valid public URL
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"<html><title>Public Page</title><body>Hello</body></html>"
        mock_response.text = "<html><title>Public Page</title><body>Hello</body></html>"
        mock_get.return_value = mock_response

        url = "https://www.google.com"
        result = self.scraper.fetch_and_save(url)

        self.assertIsNotNone(result)
        self.assertTrue(result.endswith(".md"))
        mock_get.assert_called_once()

        # Clean up
        if result and os.path.exists(os.path.join("satya_data/truth", result)):
            os.remove(os.path.join("satya_data/truth", result))

if __name__ == "__main__":
    unittest.main()
