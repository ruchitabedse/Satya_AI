import pytest
from satya.core.scraper import Scraper
from unittest.mock import patch, MagicMock

@pytest.fixture
def scraper(tmp_path):
    with patch('satya.core.storage.TRUTH_DIR', str(tmp_path)):
        return Scraper(repo_path=str(tmp_path))

def test_is_safe_url_loopback(scraper):
    assert scraper._is_safe_url("http://127.0.0.1") is False
    assert scraper._is_safe_url("http://localhost") is False
    assert scraper._is_safe_url("http://[::1]") is False

def test_is_safe_url_private_ip(scraper):
    assert scraper._is_safe_url("http://192.168.1.1") is False
    assert scraper._is_safe_url("http://10.0.0.1") is False
    assert scraper._is_safe_url("http://172.16.0.1") is False

def test_is_safe_url_metadata_service(scraper):
    assert scraper._is_safe_url("http://169.254.169.254") is False

def test_is_safe_url_invalid_scheme(scraper):
    assert scraper._is_safe_url("file:///etc/passwd") is False
    assert scraper._is_safe_url("gopher://localhost:70") is False

def test_is_safe_url_valid_public_ip(scraper):
    # Mocking socket.getaddrinfo to return a public IP
    with patch('socket.getaddrinfo') as mock_getaddrinfo:
        mock_getaddrinfo.return_value = [
            (2, 1, 6, '', ('93.184.216.34', 0))
        ]
        assert scraper._is_safe_url("http://example.com") is True

@patch('satya.core.scraper.requests.get')
def test_fetch_and_save_blocks_ssrf(mock_get, scraper):
    filename = scraper.fetch_and_save("http://127.0.0.1")
    assert filename is None
    mock_get.assert_not_called()

@patch('satya.core.scraper.requests.get')
def test_fetch_and_save_blocks_redirect_ssrf(mock_get, scraper):
    # First request is to a "safe" URL, but it redirects to an unsafe one
    mock_response = MagicMock()
    mock_response.is_redirect = True
    mock_response.status_code = 302
    mock_response.headers = {'Location': 'http://127.0.0.1'}

    mock_get.return_value = mock_response

    with patch.object(scraper, '_is_safe_url', side_effect=[True, False]):
        filename = scraper.fetch_and_save("http://safe-url.com")
        assert filename is None
        assert mock_get.call_count == 1

@patch('satya.core.scraper.requests.get')
def test_fetch_and_save_follows_safe_redirect(mock_get, scraper):
    # First request redirects to another safe URL
    mock_redirect_response = MagicMock()
    mock_redirect_response.is_redirect = True
    mock_redirect_response.status_code = 302
    mock_redirect_response.headers = {'Location': 'http://another-safe-url.com'}

    mock_final_response = MagicMock()
    mock_final_response.is_redirect = False
    mock_final_response.status_code = 200
    mock_final_response.content = b"<html><title>TestTitle</title><body>Content</body></html>"
    mock_final_response.text = "<html><title>TestTitle</title><body>Content</body></html>"
    # To satisfy BeautifulSoup
    mock_final_response.headers = {}

    mock_get.side_effect = [mock_redirect_response, mock_final_response]

    with patch.object(scraper, '_is_safe_url', return_value=True):
        # Also mock storage.save_markdown to avoid actual file I/O errors in some envs
        with patch('satya.core.storage.save_markdown', return_value="TestTitle.md"):
            with patch('satya.core.scraper.BeautifulSoup') as mock_bs:
                mock_soup = MagicMock()
                mock_soup.title.string = "TestTitle"
                mock_bs.return_value = mock_soup
                filename = scraper.fetch_and_save("http://safe-url.com")
                assert filename == "TestTitle.md"
                assert mock_get.call_count == 2
