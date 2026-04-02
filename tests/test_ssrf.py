import pytest
from src.satya.core.scraper import Scraper

@pytest.fixture
def scraper():
    return Scraper()

def test_is_safe_url_blocked_schemes(scraper):
    assert scraper._is_safe_url("file:///etc/passwd") == False
    assert scraper._is_safe_url("ftp://example.com") == False
    assert scraper._is_safe_url("gopher://example.com") == False
    assert scraper._is_safe_url("http://example.com") == True
    assert scraper._is_safe_url("https://example.com") == True

def test_is_safe_url_blocked_ips(scraper):
    # Loopback
    assert scraper._is_safe_url("http://127.0.0.1") == False
    assert scraper._is_safe_url("http://localhost") == False
    assert scraper._is_safe_url("http://[::1]") == False

    # Private ranges
    assert scraper._is_safe_url("http://10.0.0.1") == False
    assert scraper._is_safe_url("http://172.16.0.1") == False
    assert scraper._is_safe_url("http://192.168.1.1") == False

    # Link local
    assert scraper._is_safe_url("http://169.254.169.254") == False

def test_fetch_and_save_blocked_url(scraper):
    # This should return None without making a real network request
    assert scraper.fetch_and_save("http://127.0.0.1/admin") == None
    assert scraper.fetch_and_save("file:///etc/shadow") == None
