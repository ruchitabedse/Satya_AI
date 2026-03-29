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

    def _is_safe_url(self, url: str) -> bool:
        """
        Validates a URL to prevent SSRF attacks.
        Checks for allowed schemes and ensures the host resolves to a public IP.
        """
        parsed = urlparse(url)
        if parsed.scheme not in ('http', 'https'):
            return False

        hostname = parsed.hostname
        if not hostname:
            return False

        try:
            # Resolve hostname to all associated IP addresses (IPv4 and IPv6)
            addr_info = socket.getaddrinfo(hostname, None)
            for family, _, _, _, sockaddr in addr_info:
                ip_str = sockaddr[0]
                ip = ipaddress.ip_address(ip_str)

                # Block private, loopback, and reserved addresses
                if (ip.is_loopback or
                    ip.is_private or
                    ip.is_link_local or
                    ip.is_multicast or
                    ip.is_reserved or
                    ip.is_unspecified):
                    return False

            return True
        except (socket.gaierror, ValueError):
            return False

    def fetch_and_save(self, url, title=None):
        try:
            # Security: Validate URL against SSRF
            if not self._is_safe_url(url):
                print(f"SSRF Protection: Blocked potentially malicious URL: {url}")
                return None

            # Manually handle redirects to ensure each hop is validated
            max_redirects = 3
            current_url = url
            response = None

            for _ in range(max_redirects + 1):
                if not self._is_safe_url(current_url):
                    print(f"SSRF Protection: Blocked redirect to potentially malicious URL: {current_url}")
                    return None

                response = requests.get(current_url, timeout=10, allow_redirects=False)

                if response.is_redirect or response.is_permanent_redirect:
                    next_url = response.headers.get('Location')
                    if not next_url:
                        break
                    # Handle relative redirects
                    if not urlparse(next_url).netloc:
                        current_url = urljoin(current_url, next_url)
                    else:
                        current_url = next_url
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
