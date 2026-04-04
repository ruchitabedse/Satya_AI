import pytest
from satya.core.scraper import Scraper

@pytest.fixture
def scraper():
    return Scraper()

def test_is_safe_url_valid(scraper):
    assert scraper._is_safe_url("https://www.google.com") == True

def test_is_safe_url_invalid_scheme(scraper):
    assert scraper._is_safe_url("ftp://ftp.example.com") == False
    assert scraper._is_safe_url("file:///etc/passwd") == False

def test_is_safe_url_loopback(scraper):
    assert scraper._is_safe_url("http://127.0.0.1") == False
    assert scraper._is_safe_url("http://localhost") == False

def test_is_safe_url_private(scraper):
    assert scraper._is_safe_url("http://192.168.1.1") == False
    assert scraper._is_safe_url("http://10.0.0.1") == False

def test_is_safe_url_reserved(scraper):
    assert scraper._is_safe_url("http://0.0.0.0") == False

def test_fetch_and_save_blocks_unsafe(scraper):
    result = scraper.fetch_and_save("http://localhost:8000")
    assert result is None
