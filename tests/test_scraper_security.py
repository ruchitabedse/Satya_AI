import pytest
from src.satya.core.scraper import is_safe_url, Scraper
from unittest.mock import patch

def test_is_safe_url_valid():
    assert is_safe_url("https://example.com") == True
    assert is_safe_url("http://example.com/path?query=1") == True

def test_is_safe_url_invalid_scheme():
    assert is_safe_url("file:///etc/passwd") == False
    assert is_safe_url("ftp://example.com") == False
    assert is_safe_url("javascript:alert(1)") == False
    assert is_safe_url("data:text/plain,hello") == False

def test_is_safe_url_loopback():
    assert is_safe_url("http://localhost") == False
    assert is_safe_url("http://127.0.0.1") == False
    assert is_safe_url("http://[::1]") == False
    assert is_safe_url("http://0.0.0.0") == False

def test_is_safe_url_no_hostname():
    assert is_safe_url("http://") == False

@patch("src.satya.core.scraper.requests.get")
def test_scraper_blocks_unsafe_url(mock_get):
    scraper = Scraper()
    result = scraper.fetch_and_save("file:///etc/passwd")
    assert result is None
    mock_get.assert_not_called()

@patch("src.satya.core.scraper.requests.get")
@patch("src.satya.core.scraper.storage.save_markdown")
def test_scraper_allows_safe_url(mock_save, mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.content = b"<html><head><title>Test</title></head><body>Hello</body></html>"
    mock_get.return_value.text = "<html><head><title>Test</title></head><body>Hello</body></html>"

    mock_save.return_value = "satya_data/truth/Test.md"

    scraper = Scraper()
    with patch.object(scraper.git_handler, 'commit_and_push'):
        result = scraper.fetch_and_save("https://example.com", title="Test")
        assert result == "Test.md"
        mock_get.assert_called_once_with("https://example.com", timeout=10)
