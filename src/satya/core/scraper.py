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
        """Validates if the URL is safe from SSRF."""
        try:
            parsed = urlparse(url)
            if parsed.scheme not in ('http', 'https'):
                logger.error(f"SSRF Protection: Blocked invalid scheme {parsed.scheme} for {url}")
                return False

            hostname = parsed.hostname
            if not hostname:
                return False

            # Resolve hostname to all associated IPs to prevent bypasses/rebinding
            try:
                addr_info = socket.getaddrinfo(hostname, parsed.port or (80 if parsed.scheme == 'http' else 443))
            except socket.gaierror:
                logger.error(f"SSRF Protection: Could not resolve hostname {hostname}")
                return False

            for family, _, _, _, sockaddr in addr_info:
                ip_str = sockaddr[0]
                ip = ipaddress.ip_address(ip_str)

                if ip.is_loopback:
                    logger.error(f"SSRF Protection: Blocked loopback address {ip_str} for {url}")
                    return False
                if ip.is_private:
                    logger.error(f"SSRF Protection: Blocked private address {ip_str} for {url}")
                    return False
                if ip.is_reserved:
                    logger.error(f"SSRF Protection: Blocked reserved address {ip_str} for {url}")
                    return False

            return True
        except Exception as e:
            logger.error(f"SSRF Protection: Error validating URL {url}: {e}")
            return False

    def fetch_and_save(self, url, title=None):
        try:
            current_url = url
            max_redirects = 3
            redirect_count = 0

            # SSRF Fix: Manual redirect following with IP validation at each hop
            while redirect_count <= max_redirects:
                if not self._is_safe_url(current_url):
                    return None

                response = requests.get(current_url, timeout=10, allow_redirects=False)

                if response.is_redirect:
                    redirect_url = response.headers.get('Location')
                    if not redirect_url:
                        break
                    current_url = urljoin(current_url, redirect_url)
                    redirect_count += 1
                else:
                    response.raise_for_status()
                    break
            else:
                logger.error(f"Too many redirects for {url}")
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
