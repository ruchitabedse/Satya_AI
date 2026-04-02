import socket
import ipaddress
import urllib.parse
import logging
import requests
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

    def _is_safe_url(self, url: str) -> bool:
        """
        Validates the URL for SSRF protection by resolving hostname and
        blocking private/loopback/reserved IP ranges.
        """
        try:
            parsed = urllib.parse.urlparse(url)
            if parsed.scheme not in ("http", "https"):
                logger.warning(f"Blocked unsafe scheme: {parsed.scheme} in {url}")
                return False

            hostname = parsed.hostname
            if not hostname:
                return False

            # Resolve all IP addresses for the hostname
            addr_info = socket.getaddrinfo(hostname, parsed.port or (443 if parsed.scheme == "https" else 80))
            for family, _, _, _, sockaddr in addr_info:
                ip_str = sockaddr[0]
                ip = ipaddress.ip_address(ip_str)

                if ip.is_loopback:
                    logger.warning(f"Blocked loopback IP: {ip_str} in {url}")
                    return False
                if ip.is_private:
                    logger.warning(f"Blocked private IP: {ip_str} in {url}")
                    return False
                if ip.is_reserved:
                    logger.warning(f"Blocked reserved IP: {ip_str} in {url}")
                    return False
                if ip.is_link_local:
                    logger.warning(f"Blocked link-local IP: {ip_str} in {url}")
                    return False

            return True
        except Exception as e:
            logger.error(f"Error validating URL {url}: {e}")
            return False

    def fetch_and_save(self, url, title=None):
        try:
            current_url = url
            hops = 0
            max_hops = 3

            while hops <= max_hops:
                if not self._is_safe_url(current_url):
                    logger.error(f"SSRF Protection: Blocked request to unsafe URL: {current_url}")
                    return None

                response = requests.get(current_url, timeout=10, allow_redirects=False)

                if response.is_redirect:
                    hops += 1
                    location = response.headers.get("Location")
                    if not location:
                        break
                    current_url = urllib.parse.urljoin(current_url, location)
                    continue

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
