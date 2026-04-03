import requests
import socket
import ipaddress
import logging
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import markdownify
from . import storage
from .git_handler import GitHandler

logger = logging.getLogger(__name__)

class Scraper:
    def __init__(self, repo_path="."):
        self.repo_path = repo_path
        self.git_handler = GitHandler(repo_path)
        storage.ensure_satya_dirs()

    def _is_safe_url(self, url):
        """Validates URL to prevent SSRF by checking schemes and IP addresses."""
        parsed = urlparse(url)
        if parsed.scheme not in ('http', 'https'):
            return False

        hostname = parsed.hostname
        if not hostname:
            return False

        try:
            # Resolve hostname to all associated IP addresses (IPv4 and IPv6)
            addr_info = socket.getaddrinfo(hostname, None)
            for info in addr_info:
                ip_str = info[4][0]
                ip = ipaddress.ip_address(ip_str)
                if ip.is_loopback or ip.is_private or ip.is_reserved:
                    logger.warning(f"SSRF Protection: Blocked access to {hostname} ({ip_str})")
                    return False
        except socket.gaierror:
            # If resolution fails, we can't verify the IP, so block it for safety
            return False

        return True

    def fetch_and_save(self, url, title=None):
        try:
            current_url = url
            # Manually follow redirects (up to 3 hops) to validate each hop against SSRF
            for hop in range(4):
                if not self._is_safe_url(current_url):
                    logger.error(f"SSRF Protection: Blocked attempt to fetch {current_url}")
                    return None

                # Disable automatic redirects to allow per-hop validation
                response = requests.get(current_url, timeout=10, allow_redirects=False)

                if response.is_redirect or response.is_permanent_redirect:
                    next_url = response.headers.get('Location')
                    if not next_url:
                        break
                    # Handle relative redirects
                    current_url = urljoin(current_url, next_url)
                else:
                    response.raise_for_status()
                    break
            else:
                logger.error(f"Too many redirects for URL: {url}")
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
            logger.error(f"Error scraping {url}: {e}")
            return None

    def list_sources(self):
        return storage.list_truth_files()
