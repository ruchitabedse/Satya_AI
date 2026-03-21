import unittest
import os
import shutil
from unittest.mock import patch, MagicMock
from src.satya.core.scraper import Scraper, is_safe_url

class TestSSRF(unittest.TestCase):
    def setUp(self):
        self.test_dir = "test_ssrf_dir"
        os.makedirs(self.test_dir, exist_ok=True)
        # Mock satya dirs
        from src.satya.core import storage
        self.orig_tasks_dir = storage.TASKS_DIR
        self.orig_truth_dir = storage.TRUTH_DIR
        self.orig_agents_dir = storage.AGENTS_DIR

        storage.TASKS_DIR = os.path.join(self.test_dir, "tasks")
        storage.TRUTH_DIR = os.path.join(self.test_dir, "truth")
        storage.AGENTS_DIR = os.path.join(self.test_dir, "agents")

    def tearDown(self):
        from src.satya.core import storage
        storage.TASKS_DIR = self.orig_tasks_dir
        storage.TRUTH_DIR = self.orig_truth_dir
        storage.AGENTS_DIR = self.orig_agents_dir

        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_is_safe_url(self):
        self.assertTrue(is_safe_url("http://example.com"))
        self.assertTrue(is_safe_url("https://google.com"))
        self.assertFalse(is_safe_url("http://127.0.0.1"))
        self.assertFalse(is_safe_url("http://localhost"))
        self.assertFalse(is_safe_url("http://192.168.1.1"))
        self.assertFalse(is_safe_url("ftp://example.com"))
        self.assertFalse(is_safe_url("file:///etc/passwd"))

    def test_scraper_ssrf_protection_triggered(self):
        # This test ensures the scraper BLOCKS internal URL requests
        scraper = Scraper(repo_path=self.test_dir)

        # We don't need to patch requests.get if it's already blocked by is_safe_url
        internal_url = "http://192.168.1.1/admin"
        result = scraper.fetch_and_save(internal_url)

        # Should be blocked
        self.assertIsNone(result)

if __name__ == "__main__":
    unittest.main()
