import requests
import socket
import ipaddress
from urllib.parse import urlparse
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
        """Validates that the URL uses http/https and points to a non-private IP."""
        parsed = urlparse(url)
        if parsed.scheme not in ('http', 'https'):
            return False

        host = parsed.hostname
        if not host:
            return False

        try:
            # Resolve the hostname to an IP address
            ip = socket.gethostbyname(host)
            ip_obj = ipaddress.ip_address(ip)

            # Check if the IP is private, loopback, or reserved
            if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_reserved or ip_obj.is_multicast or ip_obj.is_link_local:
                return False
            return True
        except Exception:
            return False

    def fetch_and_save(self, url, title=None):
        try:
            # Manually handle redirects (up to 3 hops) to validate each hop
            current_url = url
            for _ in range(3):
                if not self._is_safe_url(current_url):
                    print(f"SSRF Protection: Blocked unsafe URL {current_url}")
                    return None

                response = requests.get(current_url, timeout=10, allow_redirects=False)
                if 300 <= response.status_code < 400:
                    current_url = response.headers.get('Location')
                    if not current_url:
                        break
                else:
                    break
            else:
                # Too many redirects
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
