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
        parsed = urlparse(url)
        if parsed.scheme not in ('http', 'https') or not parsed.hostname:
            return False
        try:
            addr_info = socket.getaddrinfo(parsed.hostname, parsed.port or (80 if parsed.scheme == 'http' else 443))
            for _, _, _, _, sockaddr in addr_info:
                ip = ipaddress.ip_address(sockaddr[0])
                if ip.is_private or ip.is_loopback or ip.is_reserved or ip.is_multicast or ip.is_link_local:
                    logger.error(f"SSRF Blocked: URL {url} resolves to unsafe IP {sockaddr[0]}")
                    return False
            return True
        except Exception as e:
            logger.error(f"Error validating URL {url}: {e}")
            return False

    def fetch_and_save(self, url, title=None):
        try:
            current_url, hops, max_hops = url, 0, 3
            while hops <= max_hops:
                if not self._is_safe_url(current_url): return None
                response = requests.get(current_url, timeout=10, allow_redirects=False)
                if 300 <= response.status_code < 400 and 'Location' in response.headers:
                    current_url = urljoin(current_url, response.headers['Location'])
                    hops += 1
                else: break
            if hops > max_hops: return None
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            if not title:
                title = soup.title.string.strip() if soup.title else "untitled_page"
            safe_title = "".join([c for c in title if c.isalnum() or c in (' ', '-', '_')]).strip().replace(' ', '_')
            filename = f"{safe_title}.md"
            markdown_content = markdownify.markdownify(response.text, heading_style="ATX")
            full_content = f"# {title}\n\nSource: {url}\n\n---\n\n{markdown_content}"
            saved_path = storage.save_markdown(filename, full_content)
            if saved_path:
                self.git_handler.commit_and_push([saved_path], f"Added Truth Source: {title}")
                return filename
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
        return None

    def list_sources(self):
        return storage.list_truth_files()
