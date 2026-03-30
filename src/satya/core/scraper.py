import requests
from bs4 import BeautifulSoup
import markdownify
import socket
import ipaddress
import logging
from urllib.parse import urlparse, urljoin
from . import storage
from .git_handler import GitHandler

logger = logging.getLogger(__name__)

class Scraper:
    def __init__(self, repo_path="."):
        self.repo_path = repo_path
        self.git_handler = GitHandler(repo_path)
        storage.ensure_satya_dirs()

    def _is_safe_url(self, url):
        """
        Security Fix: SSRF Protection.
        Resolves hostname to all IP addresses (v4/v6) and checks if they are private/loopback.
        """
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            return False

        hostname = parsed.hostname
        if not hostname:
            return False

        try:
            # Resolve to all available IP addresses
            addr_info = socket.getaddrinfo(hostname, parsed.port or (80 if parsed.scheme == "http" else 443))
            for family, _, _, _, sockaddr in addr_info:
                ip_str = sockaddr[0]
                ip = ipaddress.ip_address(ip_str)
                if ip.is_loopback or ip.is_private or ip.is_reserved or ip.is_link_local or ip.is_multicast:
                    return False
            return True
        except socket.gaierror:
            return False

    def fetch_and_save(self, url, title=None):
        try:
            current_url = url
            # Security Fix: Manually follow redirects (up to 3 hops) to validate each hop against SSRF.
            # We follow up to 3 hops as a safe default for documentation scraping.
            for _ in range(3):
                if not self._is_safe_url(current_url):
                    logger.warning(f"SSRF Protection: Blocked potentially unsafe URL: {current_url}")
                    return None

                response = requests.get(current_url, timeout=10, allow_redirects=False)

                if response.is_redirect:
                    next_url = response.headers.get('Location')
                    if not next_url:
                        break

                    # Handle both absolute and relative URLs robustly
                    current_url = urljoin(current_url, next_url)
                else:
                    response.raise_for_status()
                    break
            else:
                # If we've hit 3 redirects and still on a redirect, stop.
                if response.is_redirect:
                    logger.warning("SSRF Protection: Too many redirects.")
                    return None

            soup = BeautifulSoup(response.content, 'html.parser')
            if not title:
                if soup.title:
                    title = soup.title.string.strip()
                else:
                    title = "untitled_page"

            safe_title = "".join([c for c in title if c.isalnum() or c in (' ', '-', '_')]).strip().replace(' ', '_')
            filename = f"{safe_title}.md"

            markdown_content = markdownify.markdownify(response.text, heading_style="ATX")

            full_content = f"# {title}\n\nSource: {url}\n\n---\n\n{markdown_content}"

            saved_path = storage.save_markdown(filename, full_content)

            if saved_path:
                self.git_handler.commit_and_push([saved_path], f"Added Truth Source: {title}")
                return filename
            return None

        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return None

    def list_sources(self):
        return storage.list_truth_files()
