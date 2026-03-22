import requests
import ipaddress
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import markdownify
from . import storage
from .git_handler import GitHandler

def is_safe_url(url):
    """
    Validate that the URL is safe for scraping.
    Blocks non-http/https schemes and internal/private/reserved IP addresses to prevent SSRF.
    """
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ('http', 'https'):
            return False

        hostname = parsed.hostname
        if not hostname:
            return False

        # Attempt to parse as an IP address
        try:
            ip = ipaddress.ip_address(hostname)
            # Block loopback, private, and reserved addresses
            if ip.is_loopback or ip.is_private or ip.is_reserved or ip.is_link_local or ip.is_multicast:
                return False
        except ValueError:
            # If not an IP, it's a hostname. In a robust environment, we should resolve this
            # to an IP and check it. For now, we rely on the network layer or DNS to not
            # resolve internal names, but blocking common internal strings can be a basic layer.
            if hostname.lower() == 'localhost':
                return False

        return True
    except Exception:
        return False

class Scraper:
    def __init__(self, repo_path="."):
        self.repo_path = repo_path
        self.git_handler = GitHandler(repo_path)
        storage.ensure_satya_dirs()

    def fetch_and_save(self, url, title=None):
        if not is_safe_url(url):
            print(f"Blocked unsafe URL: {url}")
            return None

        try:
            # Set allow_redirects=False to prevent SSRF via redirects to internal resources
            response = requests.get(url, timeout=10, allow_redirects=False)
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
