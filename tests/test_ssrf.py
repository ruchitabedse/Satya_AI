import pytest
from unittest.mock import patch, MagicMock
import socket
import sys
import os

# Add src to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from satya.core.scraper import is_safe_url

def test_is_safe_url_exists():
    assert is_safe_url is not None

@pytest.mark.parametrize("url", [
    "https://www.google.com",
    "http://example.com/path?query=1",
    "https://github.com/anktechsol/Satya_AI",
])
def test_is_safe_url_allowed(url):
    assert is_safe_url(url) is True

@pytest.mark.parametrize("url", [
    "file:///etc/passwd",
    "ftp://example.com",
    "gopher://example.com",
    "mailto:admin@example.com",
    "javascript:alert(1)",
])
def test_is_safe_url_disallowed_schemes(url):
    assert is_safe_url(url) is False

@patch("socket.gethostbyname")
def test_is_safe_url_disallowed_ips(mock_gethostbyname):
    # Loopback
    mock_gethostbyname.return_value = "127.0.0.1"
    assert is_safe_url("http://localhost") is False

    # Private
    mock_gethostbyname.return_value = "192.168.1.1"
    assert is_safe_url("http://internal.corp") is False

    # Reserved/Link-local (AWS/GCP metadata)
    mock_gethostbyname.return_value = "169.254.169.254"
    assert is_safe_url("http://169.254.169.254/latest/meta-data/") is False

def test_scraper_rejects_unsafe_url():
    from satya.core.scraper import Scraper
    scraper = Scraper()

    # Mocking is_safe_url to return False
    with patch("satya.core.scraper.is_safe_url", return_value=False):
        result = scraper.fetch_and_save("http://unsafe-but-looks-safe.com")
        assert result is None

@patch("satya.core.scraper.requests.get")
@patch("satya.core.scraper.BeautifulSoup")
@patch("satya.core.scraper.markdownify.markdownify")
def test_scraper_integration_with_safe_url(mock_md, mock_bs, mock_get):
    from satya.core.scraper import Scraper

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "<html><title>Test Page</title><body>Hello World</body></html>"
    mock_response.content = mock_response.text.encode('utf-8')
    mock_get.return_value = mock_response

    mock_soup = MagicMock()
    mock_soup.title.string.strip.return_value = "Test Page"
    mock_bs.return_value = mock_soup

    mock_md.return_value = "Hello World"

    scraper = Scraper()

    # Mock is_safe_url to return True
    # Mock storage and git to avoid filesystem/git side effects
    with patch("satya.core.scraper.is_safe_url", return_value=True), \
         patch("satya.core.storage.save_markdown", return_value="satya_data/truth/Test_Page.md"), \
         patch.object(scraper.git_handler, "commit_and_push"):

        result = scraper.fetch_and_save("https://safe-website.com")
        assert result == "Test_Page.md"
        mock_get.assert_called_once()
