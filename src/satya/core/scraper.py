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
        try:
            parsed = urlparse(url)
            if parsed.scheme not in ('http', 'https'):
                logger.warning(f"SSRF Protection: Blocked invalid scheme '{parsed.scheme}' for URL: {url}")
                return False

            hostname = parsed.hostname
            if not hostname:
                return False

            # Resolve hostname to all associated IP addresses (IPv4 and IPv6)
            addr_info = socket.getaddrinfo(hostname, None)
            for info in addr_info:
                ip_str = info[4][0]
                ip = ipaddress.ip_address(ip_str)
                if ip.is_loopback or ip.is_private or ip.is_link_local or ip.is_multicast or ip.is_reserved:
                    logger.warning(f"SSRF Protection: Blocked private/reserved IP '{ip_str}' for URL: {url}")
                    return False
            return True
        except Exception as e:
            logger.error(f"Error validating URL {url}: {e}")
            return False

    def fetch_and_save(self, url, title=None):
        try:
            current_url = url
            response = None
            max_redirects = 3

            for _ in range(max_redirects + 1):
                if not self._is_safe_url(current_url):
                    return None

                response = requests.get(current_url, timeout=10, allow_redirects=False)

                if response.is_redirect:
                    redirect_url = response.headers.get('Location')
                    if not redirect_url:
                        break
                    current_url = urljoin(current_url, redirect_url)
                else:
                    break
            else:
                # Reached max_redirects without finding a final page
                logger.warning(f"SSRF Protection: Max redirects exceeded for URL: {url}")
                return None

            if not response:
                return None

            response.raise_for_status()

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
