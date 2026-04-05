import requests
import socket
import ipaddress
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import markdownify
from . import storage
from .git_handler import GitHandler

def _is_safe_url(url):
    """
    Validates that a URL is safe to fetch, preventing SSRF attacks.
    Checks for non-http/https schemes and blocks private, loopback, and reserved IP ranges.
    """
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ('http', 'https'):
            return False

        hostname = parsed.hostname
        if not hostname:
            return False

        # Resolve hostname to all associated IP addresses (IPv4 and IPv6)
        # to prevent DNS rebinding attacks and ensure all destinations are safe.
        addr_infos = socket.getaddrinfo(hostname, None)
        for info in addr_infos:
            ip_str = info[4][0]
            ip = ipaddress.ip_address(ip_str)
            if (ip.is_loopback or
                ip.is_private or
                ip.is_multicast or
                ip.is_reserved or
                ip.is_link_local):
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
        try:
            current_url = url
            response = None
            max_redirects = 3

            # Manually follow redirects to validate each hop against SSRF risks.
            for i in range(max_redirects + 1):
                if not _is_safe_url(current_url):
                    print(f"SSRF Protection: Blocked unsafe URL {current_url}")
                    return None

                response = requests.get(current_url, timeout=10, allow_redirects=False)

                # Check for redirect status codes
                if 300 <= response.status_code < 400 and 'Location' in response.headers:
                    current_url = urljoin(current_url, response.headers['Location'])
                else:
                    break

            if not response:
                return None

            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            if not title:
                if soup.title and soup.title.string:
                    title = str(soup.title.string).strip()
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
