import requests
from bs4 import BeautifulSoup
import markdownify
import ipaddress
from urllib.parse import urlparse
from . import storage
from .git_handler import GitHandler

def is_safe_url(url):
    """
    Validates a URL for SSRF protection:
    - Checks for allowed schemes (http, https).
    - Checks if the IP address is not private, loopback, or reserved.
    """
    parsed_url = urlparse(url)
    if parsed_url.scheme not in ('http', 'https'):
        return False

    hostname = parsed_url.hostname
    if not hostname:
        return False

    try:
        # Check if hostname is an IP address
        ip = ipaddress.ip_address(hostname)
        if ip.is_private or ip.is_loopback or ip.is_unspecified or ip.is_reserved:
            return False
    except ValueError:
        # If not an IP, it's a domain name. In a more production-ready system,
        # we would also resolve the domain and check the resulting IP.
        # For this exercise, we block 'localhost'.
        if hostname.lower() == 'localhost':
            return False

    return True

class Scraper:
    def __init__(self, repo_path="."):
        self.repo_path = repo_path
        self.git_handler = GitHandler(repo_path)
        storage.ensure_satya_dirs()

    def fetch_and_save(self, url, title=None):
        if not is_safe_url(url):
            print(f"Blocked unsafe URL for SSRF protection: {url}")
            return None
        try:
            # allow_redirects=False is a security measure to prevent redirect bypasses
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
