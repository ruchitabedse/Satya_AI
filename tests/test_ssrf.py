import pytest
import socket
import ipaddress
from src.satya.core.scraper import Scraper

@pytest.fixture
def scraper():
    return Scraper()

def test_internal_ips_are_blocked(scraper):
    """Verify that requests to internal/private IPs are blocked."""
    internal_urls = [
        "http://127.0.0.1",
        "http://localhost",
        "http://10.0.0.1",
        "http://172.16.0.1",
        "http://192.168.1.1",
        "http://169.254.169.254", # AWS metadata
        "http://[::1]",
    ]

    for url in internal_urls:
        # Before fix, these might fail due to no server running, but they should be BLOCKED before requests.get
        # After fix, they should return None immediately.
        result = scraper.fetch_and_save(url)
        assert result is None, f"URL {url} should have been blocked"

def test_scheme_validation(scraper):
    """Verify that only http and https schemes are allowed."""
    invalid_schemes = [
        "file:///etc/passwd",
        "gopher://localhost:70",
        "ftp://example.com",
        "dict://localhost:11211/stat"
    ]

    for url in invalid_schemes:
        result = scraper.fetch_and_save(url)
        assert result is None, f"Scheme in {url} should have been blocked"
