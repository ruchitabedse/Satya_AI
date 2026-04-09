import requests
import socket
import ipaddress
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import markdownify
from . import storage
from .git_handler import GitHandler

class Scraper:
    def __init__(self, repo_path="."):
        self.repo_path = repo_path
        self.git_handler = GitHandler(repo_path)
        storage.ensure_satya_dirs()

    def _is_safe_url(self, url):
        """Validates that the URL is safe from SSRF by checking IP addresses."""
        try:
            parsed = urlparse(url)
            if parsed.scheme not in ('http', 'https'):
                return False

            hostname = parsed.hostname
            if not hostname:
                return False

            # Resolve hostname to all associated IP addresses
            addr_info = socket.getaddrinfo(hostname, None)
            for info in addr_info:
                ip_str = info[4][0]
                ip = ipaddress.ip_address(ip_str)
                # Block loopback, private, and reserved IP ranges
                if ip.is_loopback or ip.is_private or ip.is_reserved:
                    return False
            return True
        except Exception:
            return False

    def fetch_and_save(self, url, title=None):
        try:
            current_url = url
            hops = 0
            max_hops = 3
            response = None

            while hops <= max_hops:
                if not self._is_safe_url(current_url):
                    print(f"Security violation: Blocked unsafe URL {current_url}")
                    return None

                # Disable automatic redirects to validate each hop
                response = requests.get(current_url, timeout=10, allow_redirects=False)

                if 300 <= response.status_code < 400:
                    location = response.headers.get('Location')
                    if not location:
                        break
                    current_url = urljoin(current_url, location)
                    hops += 1
                else:
                    break

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
