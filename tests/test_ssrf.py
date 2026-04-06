import pytest
from unittest.mock import MagicMock, patch
from satya.core.scraper import Scraper

@pytest.fixture
def scraper():
    return Scraper()

def test_is_safe_url_valid(scraper):
    with patch("socket.getaddrinfo") as mock_resolve:
        mock_resolve.return_value = [(2, 1, 6, "", ("93.184.216.34", 443))]
        assert scraper._is_safe_url("https://www.google.com") is True
        assert scraper._is_safe_url("http://example.com") is True

def test_is_safe_url_invalid_scheme(scraper):
    assert scraper._is_safe_url("ftp://example.com") is False
    assert scraper._is_safe_url("file:///etc/passwd") is False
    assert scraper._is_safe_url("gopher://example.com") is False

def test_is_safe_url_loopback(scraper):
    assert scraper._is_safe_url("http://127.0.0.1") is False
    assert scraper._is_safe_url("http://localhost") is False
    assert scraper._is_safe_url("http://[::1]") is False

def test_is_safe_url_private_ip(scraper):
    assert scraper._is_safe_url("http://192.168.1.1") is False
    assert scraper._is_safe_url("http://10.0.0.1") is False
    assert scraper._is_safe_url("http://172.16.0.1") is False

def test_is_safe_url_reserved_ip(scraper):
    assert scraper._is_safe_url("http://240.0.0.1") is False

@patch("satya.core.scraper.requests.get")
def test_fetch_and_save_blocks_ssrf(mock_get, scraper):
    # Ensure it returns None for an unsafe URL
    assert scraper.fetch_and_save("http://127.0.0.1/admin") is None
    # Ensure requests.get was never called for an unsafe URL
    mock_get.assert_not_called()

@patch("satya.core.scraper.requests.get")
def test_fetch_and_save_blocks_redirect_ssrf(mock_get, scraper):
    # First request returns a redirect to an unsafe URL
    mock_redirect = MagicMock()
    mock_redirect.status_code = 302
    mock_redirect.is_redirect = True
    mock_redirect.headers = {"Location": "http://169.254.169.254/latest/meta-data/"}

    mock_get.return_value = mock_redirect

    # Use side_effect on getaddrinfo to return safe IP first, then raise for subsequent calls if needed
    with patch("socket.getaddrinfo") as mock_resolve:
        mock_resolve.side_effect = [
            [(2, 1, 6, "", ("93.184.216.34", 443))], # for safe-url.com
            socket.gaierror() # fallback/fail for anything else
        ]

        # We expect it to return None because the redirect is to an unsafe IP (even if it doesn't resolve, _is_safe_url handles it)
        # Actually _is_safe_url for 169.254.169.254 will return False because it is a reserved/link-local address
        assert scraper.fetch_and_save("https://safe-url.com") is None

    # requests.get should be called exactly once for the safe URL
    assert mock_get.call_count == 1
    mock_get.assert_called_with("https://safe-url.com", timeout=10, allow_redirects=False)

import socket

@patch("satya.core.scraper.requests.get")
def test_fetch_and_save_success(mock_get, scraper):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.is_redirect = False
    mock_response.content = b"<html><title>Test Page</title><body>Hello World</body></html>"
    mock_response.text = "<html><title>Test Page</title><body>Hello World</body></html>"

    mock_get.return_value = mock_response

    # Mock storage and git to avoid side effects
    with patch("satya.core.storage.save_markdown") as mock_save, \
         patch("satya.core.git_handler.GitHandler.commit_and_push"), \
         patch("socket.getaddrinfo") as mock_resolve:

        mock_resolve.return_value = [(2, 1, 6, "", ("93.184.216.34", 443))]
        mock_save.return_value = "satya_data/truth/Test_Page.md"

        filename = scraper.fetch_and_save("https://example.com", title="Test Page")
        assert filename == "Test_Page.md"
        assert mock_get.call_count == 1
