import pytest
from unittest.mock import patch, MagicMock
from src.satya.core.scraper import Scraper

def test_ssrf_blocked():
    """Verify that the scraper now blocks requests to loopback IPs."""
    scraper = Scraper()

    with patch('src.satya.core.scraper.requests.get') as mock_get:
        # Test with a loopback IP
        unsafe_url = "http://127.0.0.1:8000/admin"
        filename = scraper.fetch_and_save(unsafe_url)

        # It should NOT be called and should return None
        assert not mock_get.called
        assert filename is None

def test_ssrf_metadata_blocked():
    """Verify that the scraper now blocks requests to cloud metadata services."""
    scraper = Scraper()

    with patch('src.satya.core.scraper.requests.get') as mock_get:
        metadata_url = "http://169.254.169.254/latest/meta-data/"
        filename = scraper.fetch_and_save(metadata_url)

        # It should NOT be called and should return None
        assert not mock_get.called
        assert filename is None

def test_safe_url_allowed():
    """Verify that safe URLs are still allowed."""
    scraper = Scraper()

    with patch('src.satya.core.scraper.requests.get') as mock_get:
        # Simulating a valid external website
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"<html><title>External Site</title><body>Content</body></html>"
        mock_response.text = "<html><title>External Site</title><body>Content</body></html>"
        mock_get.return_value = mock_response

        with patch('src.satya.core.scraper.socket.gethostbyname') as mock_dns:
            mock_dns.return_value = "8.8.8.8" # Public DNS IP

            safe_url = "https://example.com/blog"
            filename = scraper.fetch_and_save(safe_url)

            # It SHOULD be called with allow_redirects=False (due to manual redirect logic)
            mock_get.assert_called_with(safe_url, timeout=10, allow_redirects=False)
            assert filename is not None

def test_safe_redirect_allowed():
    """Verify that the scraper follows safe redirects."""
    scraper = Scraper()

    with patch('src.satya.core.scraper.requests.get') as mock_get:
        # 1. First call is a redirect
        redirect_response = MagicMock()
        redirect_response.status_code = 302
        redirect_response.is_redirect = True
        redirect_response.headers = {'Location': 'https://example.com/final'}

        # 2. Second call is the final page
        final_response = MagicMock()
        final_response.status_code = 200
        final_response.is_redirect = False
        final_response.content = b"<html><title>Final Page</title><body>Content</body></html>"
        final_response.text = "<html><title>Final Page</title><body>Content</body></html>"

        mock_get.side_effect = [redirect_response, final_response]

        with patch('src.satya.core.scraper.socket.gethostbyname') as mock_dns:
            mock_dns.return_value = "8.8.8.8"

            initial_url = "http://example.com/start"
            filename = scraper.fetch_and_save(initial_url)

            # Should be called twice
            assert mock_get.call_count == 2
            assert filename is not None

def test_unsafe_redirect_blocked():
    """Verify that the scraper blocks a redirect to an unsafe IP."""
    scraper = Scraper()

    with patch('src.satya.core.scraper.requests.get') as mock_get:
        # 1. First call is a redirect to internal IP
        redirect_response = MagicMock()
        redirect_response.status_code = 302
        redirect_response.is_redirect = True
        redirect_response.headers = {'Location': 'http://127.0.0.1/admin'}

        mock_get.return_value = redirect_response

        with patch('src.satya.core.scraper.socket.gethostbyname') as mock_dns:
            # First resolution is safe
            # Second resolution is unsafe
            mock_dns.side_effect = ["8.8.8.8", "127.0.0.1"]

            initial_url = "http://example.com/start"
            filename = scraper.fetch_and_save(initial_url)

            # Should be called once then blocked
            assert mock_get.call_count == 1
            assert filename is None
