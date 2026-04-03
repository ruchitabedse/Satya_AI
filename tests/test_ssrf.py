import pytest
from satya.core.scraper import Scraper

def test_is_safe_url_blocked_schemes():
    scraper = Scraper()
    assert scraper._is_safe_url("file:///etc/passwd") == False
    assert scraper._is_safe_url("ftp://127.0.0.1") == False
    assert scraper._is_safe_url("gopher://127.0.0.1") == False

def test_is_safe_url_blocked_ips():
    scraper = Scraper()
    # Loopback
    assert scraper._is_safe_url("http://127.0.0.1") == False
    assert scraper._is_safe_url("http://localhost") == False
    assert scraper._is_safe_url("http://[::1]") == False

    # Private IPv4
    assert scraper._is_safe_url("http://10.0.0.1") == False
    assert scraper._is_safe_url("http://172.16.0.1") == False
    assert scraper._is_safe_url("http://192.168.1.1") == False

    # Private IPv6
    assert scraper._is_safe_url("http://[fd00::1]") == False

def test_is_safe_url_allowed():
    scraper = Scraper()
    # Google (public IP) - will involve DNS resolution
    assert scraper._is_safe_url("https://www.google.com") == True

def test_fetch_and_save_blocks_ssrf():
    scraper = Scraper()
    # Should return None instead of attempting request
    assert scraper.fetch_and_save("http://127.0.0.1:8081") == None
