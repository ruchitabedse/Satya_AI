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
        """Security helper: Validates scheme and destination IP address to prevent SSRF."""
        try:
            parsed = urlparse(url)
            if parsed.scheme not in ('http', 'https'):
                return False
            hostname = parsed.hostname
            if not hostname:
                return False
            ip_addr = socket.gethostbyname(hostname)
            ip = ipaddress.ip_address(ip_addr)
            return not (ip.is_private or ip.is_loopback or ip.is_reserved or ip.is_link_local)
        except Exception:
            return False

    def fetch_and_save(self, url, title=None):
        try:
            # Security Fix: Prevent SSRF by validating the URL and any redirects.
            current_url = url
            resp = None
            for _ in range(3): # Limit redirects to 3 hops for security/performance
                if not self._is_safe_url(current_url):
                    print(f"Blocked potentially unsafe URL: {current_url}")
                    return None

                resp = requests.get(current_url, timeout=10, allow_redirects=False)
                if resp.status_code in (301, 302, 303, 307, 308):
                    location = resp.headers.get('Location', '')
                    if not location:
                        break
                    current_url = urljoin(current_url, str(location))
                    continue
                resp.raise_for_status()
                break
            else:
                if not (resp and resp.status_code == 200):
                    print(f"Too many redirects or failed for {url}")
                    return None

            if not resp:
                return None

            soup = BeautifulSoup(resp.content, 'html.parser')
            page_title = title
            if not page_title:
                if soup.title and soup.title.string:
                    page_title = soup.title.string.strip()
                else:
                    page_title = "untitled_page"

            safe_title = "".join([c for c in str(page_title) if c.isalnum() or c in (' ', '-', '_')]).strip().replace(' ', '_')
            filename = f"{safe_title}.md"
            markdown_content = markdownify.markdownify(resp.text, heading_style="ATX")
            full_content = f"# {page_title}\n\nSource: {url}\n\n---\n\n{markdown_content}"

            saved_path = storage.save_markdown(filename, full_content)
            if saved_path:
                self.git_handler.commit_and_push([saved_path], f"Added Truth Source: {page_title}")
                return filename
            return None
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return None

    def list_sources(self):
        return storage.list_truth_files()
