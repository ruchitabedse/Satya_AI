import pytest
from src.satya.core.scraper import is_safe_url

def test_is_safe_url_valid():
    assert is_safe_url("https://www.google.com") is True
    assert is_safe_url("http://example.com") is True

def test_is_safe_url_invalid_scheme():
    assert is_safe_url("ftp://example.com") is False
    assert is_safe_url("file:///etc/passwd") is False
    assert is_safe_url("gopher://example.com") is False

def test_is_safe_url_loopback():
    assert is_safe_url("http://127.0.0.1") is False
    assert is_safe_url("http://localhost") is False
    assert is_safe_url("http://0.0.0.0") is False
    assert is_safe_url("http://[::1]") is False

def test_is_safe_url_private_ip():
    assert is_safe_url("http://192.168.1.1") is False
    assert is_safe_url("http://10.0.0.1") is False
    assert is_safe_url("http://172.16.0.1") is False

def test_is_safe_url_no_hostname():
    assert is_safe_url("http://") is False
    assert is_safe_url("not_a_url") is False
