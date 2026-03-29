import pytest
from unittest.mock import patch, MagicMock
from satya.core.scraper import Scraper
import os
import socket

def test_ssrf_protection_loopback():
    scraper = Scraper()
    # Testing loopback address
    url = "http://127.0.0.1/admin"

    # The request should be blocked before it even reaches requests.get
    result = scraper.fetch_and_save(url)
    assert result is None, f"Scraper should have blocked request to {url}"

def test_ssrf_protection_private_ip():
    scraper = Scraper()
    # Testing private IP range
    url = "http://192.168.1.1/config"

    result = scraper.fetch_and_save(url)
    assert result is None, f"Scraper should have blocked request to {url}"

def test_ssrf_protection_dns_rebinding():
    # This is harder to test without a real DNS setup,
    # but we can mock the socket.getaddrinfo
    scraper = Scraper()
    url = "http://malicious-domain.com"

    with patch("socket.getaddrinfo") as mock_dns:
        # Mocking getaddrinfo to return loopback info
        # Structure: [(family, type, proto, canonname, sockaddr), ...]
        mock_dns.return_value = [
            (socket.AF_INET, socket.SOCK_STREAM, 6, '', ('127.0.0.1', 0))
        ]
        result = scraper.fetch_and_save(url)
        assert result is None, f"Scraper should have blocked request to {url} which resolves to loopback"

def test_ssrf_protection_redirect_to_loopback():
    scraper = Scraper()
    url = "http://public-site.com/redirect"

    with patch("socket.getaddrinfo") as mock_dns:
        # Initial URL is safe, second is not
        mock_dns.side_effect = [
            [(socket.AF_INET, socket.SOCK_STREAM, 6, '', ('93.184.216.34', 0))],
            [(socket.AF_INET, socket.SOCK_STREAM, 6, '', ('127.0.0.1', 0))]
        ]

        with patch("satya.core.scraper.requests.get") as mock_get:
            # Mock the redirect
            mock_response = MagicMock()
            mock_response.is_redirect = True
            mock_response.is_permanent_redirect = False
            mock_response.headers = {'Location': 'http://127.0.0.1/admin'}
            mock_get.return_value = mock_response

            result = scraper.fetch_and_save(url)
            assert result is None, "Scraper should have blocked redirect to loopback"

def test_ssrf_protection_ipv6_loopback():
    scraper = Scraper()
    url = "http://[::1]/admin"

    result = scraper.fetch_and_save(url)
    assert result is None, "Scraper should have blocked IPv6 loopback"
