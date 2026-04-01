import requests
from bs4 import BeautifulSoup
import markdownify
from . import storage
from .git_handler import GitHandler
import socket
import ipaddress
import logging
from urllib.parse import urlparse, urljoin

logger = logging.getLogger(__name__)

class Scraper:
    def __init__(self, repo_path="."):
        self.repo_path = repo_path
        self.git_handler = GitHandler(repo_path)
        storage.ensure_satya_dirs()

    def _is_safe_url(self, url):
        """
        Check if the URL is safe to fetch, preventing SSRF attacks.
        Validates scheme and ensures IP is not private, loopback, or reserved.
        """
        try:
            parsed = urlparse(url)
            if parsed.scheme not in ('http', 'https'):
                logger.warning(f"Invalid scheme in URL: {url}")
                return False

            hostname = parsed.hostname
            if not hostname:
                return False

            # Resolve hostname to all associated IP addresses (IPv4 and IPv6)
            # This prevents bypasses and DNS rebinding attacks.
            try:
                addr_info = socket.getaddrinfo(hostname, None)
            except socket.gaierror:
                logger.warning(f"Could not resolve hostname: {hostname}")
                return False

            for family, _, _, _, sockaddr in addr_info:
                ip_str = sockaddr[0]
                ip = ipaddress.ip_address(ip_str)
                if ip.is_private or ip.is_loopback or ip.is_reserved or ip.is_multicast:
                    logger.warning(f"SSRF Attempt Blocked: {url} resolves to {ip_str}")
                    return False

            return True
        except Exception as e:
            logger.error(f"Error validating URL {url}: {e}")
            return False

    def fetch_and_save(self, url, title=None):
        current_url = url
        max_redirects = 3
        redirect_count = 0

        try:
            response = None
            while redirect_count <= max_redirects:
                if not self._is_safe_url(current_url):
                    return None

                response = requests.get(current_url, timeout=10, allow_redirects=False)

                if response.is_redirect or response.is_permanent_redirect or response.status_code in (301, 302, 303, 307, 308):
                    redirect_count += 1
                    if redirect_count > max_redirects:
                        logger.warning(f"Too many redirects for URL: {url}")
                        return None

                    location = response.headers.get('Location')
                    if not location:
                        break
                    current_url = urljoin(current_url, location)
                    continue

                response.raise_for_status()
                break
            else:
                return None

            if response is None:
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
