import pytest
from unittest.mock import patch, MagicMock
from satya.core.scraper import Scraper
import socket

@pytest.fixture
def scraper():
    return Scraper()

def test_is_safe_url_loopback(scraper):
    assert scraper._is_safe_url("http://127.0.0.1") is False
    assert scraper._is_safe_url("http://localhost") is False
    assert scraper._is_safe_url("http://[::1]") is False

def test_is_safe_url_private_ip(scraper):
    assert scraper._is_safe_url("http://192.168.1.1") is False
    assert scraper._is_safe_url("http://10.0.0.1") is False
    assert scraper._is_safe_url("http://172.16.0.1") is False

def test_is_safe_url_public_ip(scraper):
    # Mocking socket.getaddrinfo to avoid real DNS lookups and ensure test stability
    with patch("socket.getaddrinfo") as mock_getaddrinfo:
        mock_getaddrinfo.return_value = [
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", 80))
        ]
        assert scraper._is_safe_url("http://example.com") is True

def test_is_safe_url_invalid_scheme(scraper):
    assert scraper._is_safe_url("file:///etc/passwd") is False
    assert scraper._is_safe_url("ftp://example.com") is False
    assert scraper._is_safe_url("gopher://example.com") is False

def test_fetch_and_save_blocks_ssrf(scraper):
    with patch("satya.core.scraper.requests.get") as mock_get:
        # Should not even call requests.get if it's a loopback
        with patch("satya.core.scraper.logger") as mock_logger:
            result = scraper.fetch_and_save("http://127.0.0.1/admin")
            assert result is None
            mock_get.assert_not_called()
            mock_logger.warning.assert_called()

def test_fetch_and_save_blocks_redirect_ssrf(scraper):
    with patch("satya.core.scraper.requests.get") as mock_get:
        # We need a custom side effect for getaddrinfo to handle different hosts
        original_getaddrinfo = socket.getaddrinfo
        def side_effect(host, port, family=0, type=0, proto=0, flags=0):
            if host == "example.com":
                return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", port))]
            # For other hosts (like 127.0.0.1), use the real one or a safe mock
            return original_getaddrinfo(host, port, family, type, proto, flags)

        with patch("socket.getaddrinfo", side_effect=side_effect):
            # Mocking the first response to be a redirect to a local address
            mock_redirect = MagicMock()
            mock_redirect.is_redirect = True
            mock_redirect.headers = {"Location": "http://127.0.0.1/secret"}

            # Second call (which should not happen) would be the actual fetch
            mock_get.side_effect = [mock_redirect]

            result = scraper.fetch_and_save("http://example.com/redirect")
            assert result is None
            # It should have called it once for the redirect
            assert mock_get.call_count == 1
            # But it should have blocked the second call
