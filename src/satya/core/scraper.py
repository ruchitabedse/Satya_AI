import requests
from bs4 import BeautifulSoup
import markdownify
import socket
import ipaddress
from urllib.parse import urlparse, urljoin
from . import storage
from .git_handler import GitHandler

class Scraper:
    def __init__(self, repo_path="."):
        self.repo_path = repo_path
        self.git_handler = GitHandler(repo_path)
        storage.ensure_satya_dirs()

    def _is_safe_url(self, url):
        """Validates that the URL is safe for scraping (SSRF protection)."""
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            return False

        hostname = parsed.hostname
        if not hostname:
            return False

        try:
            # Resolve the hostname to an IP address
            ip = socket.gethostbyname(hostname)
            ip_obj = ipaddress.ip_address(ip)

            # Block loopback, private, and reserved IP ranges
            if ip_obj.is_loopback or ip_obj.is_private or ip_obj.is_reserved or ip_obj.is_multicast or ip_obj.is_link_local:
                return False
            return True
        except (socket.gaierror, ValueError):
            return False

    def fetch_and_save(self, url, title=None):
        try:
            # SSRF Protection: Initial URL check
            if not self._is_safe_url(url):
                print(f"SSRF Protection: Blocked potentially unsafe URL: {url}")
                return None

            # SSRF Protection: Manually handle redirects to ensure they are safe
            current_url = url
            max_redirects = 3
            response = None

            for _ in range(max_redirects + 1):
                # Note: To fully mitigate DNS rebinding, we would ideally resolve the IP
                # once and then use it for the request while passing the 'Host' header.
                # However, for this implementation, we re-validate each hop.
                response = requests.get(current_url, timeout=10, allow_redirects=False)
                if 300 <= response.status_code < 400 and 'Location' in response.headers:
                    redirect_url = response.headers['Location']
                    # Handle relative URLs
                    if not urlparse(redirect_url).netloc:
                        redirect_url = urljoin(current_url, redirect_url)

                    if not self._is_safe_url(redirect_url):
                        print(f"SSRF Protection: Blocked unsafe redirect to: {redirect_url}")
                        return None
                    current_url = redirect_url
                else:
                    break

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
