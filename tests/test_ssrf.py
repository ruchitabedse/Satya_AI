import pytest
from unittest.mock import patch, MagicMock
from satya.core.scraper import Scraper

@pytest.fixture
def scraper(tmp_path):
    return Scraper(repo_path=str(tmp_path))

def test_is_safe_url_google(scraper):
    assert scraper._is_safe_url("https://google.com") is True

def test_is_safe_url_localhost(scraper):
    assert scraper._is_safe_url("http://localhost:5000") is False
    assert scraper._is_safe_url("http://127.0.0.1") is False

def test_is_safe_url_private_ip(scraper):
    assert scraper._is_safe_url("http://192.168.1.1") is False
    assert scraper._is_safe_url("http://10.0.0.1") is False
    assert scraper._is_safe_url("http://172.16.0.1") is False

def test_is_safe_url_metadata(scraper):
    assert scraper._is_safe_url("http://169.254.169.254") is False

@patch("satya.core.scraper.requests.get")
def test_fetch_and_save_blocks_ssrf(mock_get, scraper):
    url = "http://127.0.0.1/admin"
    filename = scraper.fetch_and_save(url)
    assert filename is None
    mock_get.assert_not_called()

@patch("satya.core.scraper.requests.get")
def test_fetch_and_save_follows_safe_redirect(mock_get, scraper):
    # Mock a safe redirect: example.com -> example.org
    mock_resp1 = MagicMock()
    mock_resp1.is_redirect = True
    mock_resp1.headers = {"Location": "https://example.org"}

    mock_resp2 = MagicMock()
    mock_resp2.is_redirect = False
    mock_resp2.status_code = 200
    mock_resp2.content = b"<html><title>Example</title><body>Hello</body></html>"
    mock_resp2.text = "<html><title>Example</title><body>Hello</body></html>"

    # We also need to patch BeautifulSoup or soup.title if we want a specific filename
    # Actually, scraper uses response.content and soup.title.string

    mock_get.side_effect = [mock_resp1, mock_resp2]

    with patch("satya.core.scraper.BeautifulSoup") as mock_bs:
        mock_soup = MagicMock()
        mock_soup.title.string = "Example Title"
        mock_bs.return_value = mock_soup

        filename = scraper.fetch_and_save("https://example.com")
        assert filename is not None
        assert "Example_Title.md" in filename

@patch("satya.core.scraper.requests.get")
def test_fetch_and_save_blocks_ssrf_redirect(mock_get, scraper):
    # Mock an SSRF redirect: example.com -> localhost
    mock_resp1 = MagicMock()
    mock_resp1.is_redirect = True
    mock_resp1.headers = {"Location": "http://localhost:5000/admin"}

    mock_get.side_effect = [mock_resp1]

    filename = scraper.fetch_and_save("https://example.com")
    assert filename is None

@patch("satya.core.scraper.requests.get")
def test_fetch_and_save_max_redirects(mock_get, scraper):
    # Mock infinite redirect loop
    mock_resp = MagicMock()
    mock_resp.is_redirect = True
    mock_resp.headers = {"Location": "https://infinite.com"}

    mock_get.return_value = mock_resp

    filename = scraper.fetch_and_save("https://example.com")
    assert filename is None
    assert mock_get.call_count == 4 # Initial + 3 redirects
