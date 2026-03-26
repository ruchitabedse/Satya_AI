import unittest
from unittest.mock import patch, MagicMock
from src.satya.core.scraper import Scraper
import os
import shutil

class TestSSRF(unittest.TestCase):
    def setUp(self):
        self.repo_path = "test_ssrf_repo"
        os.makedirs(self.repo_path, exist_ok=True)
        # The Scraper constructor calls storage.ensure_satya_dirs() which creates satya_data/
        self.scraper = Scraper(self.repo_path)

    def tearDown(self):
        if os.path.exists(self.repo_path):
            shutil.rmtree(self.repo_path)
        if os.path.exists("satya_data"):
            shutil.rmtree("satya_data")

    @patch('socket.gethostbyname')
    @patch('requests.get')
    def test_fetch_and_save_ssrf_blocked(self, mock_get, mock_gethostbyname):
        # Scenario 1: Direct request to loopback
        mock_gethostbyname.return_value = '127.0.0.1'

        url = "http://127.0.0.1:8000/metadata"
        result = self.scraper.fetch_and_save(url)

        # Should now return None
        self.assertIsNone(result)
        # TRUTH_DIR is satya_data/truth. It should be empty if no files were saved.
        truth_dir = "satya_data/truth"
        if os.path.exists(truth_dir):
            self.assertEqual(len(os.listdir(truth_dir)), 0)

    @patch('socket.gethostbyname')
    @patch('requests.get')
    def test_fetch_and_save_ssrf_redirect_blocked(self, mock_get, mock_gethostbyname):
        # Scenario 2: Redirect to private IP
        # Hop 1: Public site
        # Hop 2: Private IP

        # We need to control the side effect of socket.gethostbyname
        def gethost_side_effect(host):
            if host == "public-site.com":
                return "8.8.8.8" # Public IP
            elif host == "192.168.1.1":
                return "192.168.1.1" # Private IP
            return "127.0.0.1"

        mock_gethostbyname.side_effect = gethost_side_effect

        # Mocking the first response as a redirect
        mock_redirect = MagicMock()
        mock_redirect.status_code = 302
        mock_redirect.headers = {"Location": "http://192.168.1.1"}

        # requests.get will be called twice
        mock_get.side_effect = [mock_redirect, MagicMock()] # Second mock won't be called if blocked

        url = "http://public-site.com/redirect"
        result = self.scraper.fetch_and_save(url)

        # Should be blocked at the second hop
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()
