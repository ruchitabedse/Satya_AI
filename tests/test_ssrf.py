import pytest
from unittest.mock import patch, MagicMock
from src.satya.core.scraper import Scraper
import os

def test_ssrf_protection_loopback():
    scraper = Scraper(repo_path=".")
    with patch('src.satya.core.scraper.requests.get') as mock_get:
        result = scraper.fetch_and_save("http://127.0.0.1/admin")
        assert result is None
        mock_get.assert_not_called()

def test_ssrf_protection_private_ip():
    scraper = Scraper(repo_path=".")
    with patch('src.satya.core.scraper.requests.get') as mock_get:
        result = scraper.fetch_and_save("http://192.168.1.1/config")
        assert result is None
        mock_get.assert_not_called()

def test_ssrf_protection_metadata():
    scraper = Scraper(repo_path=".")
    with patch('src.satya.core.scraper.requests.get') as mock_get:
        result = scraper.fetch_and_save("http://169.254.169.254/latest/meta-data/")
        assert result is None
        mock_get.assert_not_called()

def test_ssrf_protection_safe_url():
    scraper = Scraper(repo_path=".")
    # We need to mock ONLY requests.get to let Scraper use REAL BeautifulSoup
    with patch('src.satya.core.scraper.requests.get') as mock_get:
        # Mocking the response to have a title
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "<html><head><title>Safe Page</title></head><body>Safe Content</body></html>"
        mock_response.content = b"<html><head><title>Safe Page</title></head><body>Safe Content</body></html>"
        mock_get.return_value = mock_response

        # We need to mock storage.save_markdown to avoid file system side effects in tests
        with patch('src.satya.core.storage.save_markdown') as mock_save:
            mock_save.return_value = "fake_path.md"
            with patch('src.satya.core.git_handler.GitHandler.commit_and_push'):
                # Pass title explicitly to avoid soup issues in mock
                result = scraper.fetch_and_save("https://www.google.com", title="Safe Page")
                assert result == "Safe_Page.md"
                mock_get.assert_called_once()
