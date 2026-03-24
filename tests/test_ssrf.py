import pytest
from unittest.mock import patch, MagicMock
import requests
from src.satya.core.scraper import Scraper

@pytest.fixture
def scraper():
    with patch('src.satya.core.storage.ensure_satya_dirs'):
        return Scraper(repo_path=".")

def test_is_safe_url_blocks_private_ips(scraper):
    assert scraper._is_safe_url("http://127.0.0.1") is False
    assert scraper._is_safe_url("http://localhost") is False
    assert scraper._is_safe_url("http://192.168.1.1") is False
    assert scraper._is_safe_url("http://10.0.0.1") is False
    assert scraper._is_safe_url("http://169.254.169.254") is False

def test_is_safe_url_blocks_non_http_schemes(scraper):
    assert scraper._is_safe_url("file:///etc/passwd") is False
    assert scraper._is_safe_url("gopher://localhost") is False
    assert scraper._is_safe_url("ftp://example.com") is False

def test_is_safe_url_allows_public_ips(scraper):
    # Mocking socket.getaddrinfo to return a public IP
    with patch('socket.getaddrinfo') as mock_getaddrinfo:
        mock_getaddrinfo.return_value = [(None, None, None, None, ('93.184.216.34', 80))] # example.com
        assert scraper._is_safe_url("http://example.com") is True

def test_fetch_and_save_blocks_ssrf_redirect(scraper):
    # First request returns a redirect to a private IP
    mock_redirect = MagicMock()
    mock_redirect.status_code = 302
    mock_redirect.headers = {'Location': 'http://127.0.0.1/admin'}

    with patch.object(requests, 'get', return_value=mock_redirect) as mock_get:
        # We need to mock the initial public URL check
        with patch.object(scraper, '_is_safe_url', side_effect=[True, False]):
            result = scraper.fetch_and_save("http://public-service.com/redirect")
            assert result is None
            # Should have called requests.get once for the public URL
            assert mock_get.call_count == 1

def test_fetch_and_save_follows_safe_redirect(scraper):
    # First request returns a redirect to another public URL
    mock_redirect = MagicMock()
    mock_redirect.status_code = 302
    mock_redirect.headers = {'Location': 'http://another-public.com'}

    # We mock BeautifulSoup in conftest, so let's mock it locally to behave as we expect
    with patch('src.satya.core.scraper.BeautifulSoup') as mock_bs:
        mock_soup = MagicMock()
        mock_soup.title.string.strip.return_value = "Success"
        mock_bs.return_value = mock_soup

        mock_success = MagicMock()
        mock_success.status_code = 200
        mock_success.content = b"<html><title>Success</title><body>Hello</body></html>"
        mock_success.text = "<html><title>Success</title><body>Hello</body></html>"

        with patch.object(requests, 'get', side_effect=[mock_redirect, mock_success]) as mock_get:
            with patch.object(scraper, '_is_safe_url', return_value=True), \
                 patch('src.satya.core.storage.save_markdown', return_value="path/to/file.md"), \
                 patch('src.satya.core.git_handler.GitHandler.commit_and_push'):

                result = scraper.fetch_and_save("http://public.com")
                # The title extracted from mock_success is "Success"
                assert result == "Success.md"
                assert mock_get.call_count == 2
