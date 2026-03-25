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
        """Validates that a URL does not point to internal, private, or loopback resources."""
        try:
            parsed = urlparse(url)
            if parsed.scheme not in ('http', 'https'):
                return False

            hostname = parsed.hostname
            if not hostname:
                return False

            # Resolve hostname to IP to catch common SSRF attempts.
            # Note: DNS rebinding is still technically possible but this covers most cases.
            ip_address = socket.gethostbyname(hostname)
            ip = ipaddress.ip_address(ip_address)

            # Block private, loopback, link-local, and reserved addresses
            return not (ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved)
        except Exception:
            return False

    def fetch_and_save(self, url, title=None):
        try:
            # SSRF Protection: Validate initial URL and all hops in redirect chain (manual follow)
            current_url = url
            max_redirects = 3
            final_response = None

            for _ in range(max_redirects + 1):
                if not self._is_safe_url(current_url):
                    logger.warning(f"SSRF Protection: Unsafe or invalid URL blocked: {current_url}")
                    return None

                # Fetch without auto-redirects to validate each hop manually
                response = requests.get(current_url, timeout=10, allow_redirects=False)

                if response.is_redirect:
                    redirect_target = response.headers.get('Location')
                    if not redirect_target:
                        final_response = response
                        break
                    # Correctly resolve relative URLs against the current hop's URL
                    current_url = urljoin(current_url, redirect_target)
                else:
                    final_response = response
                    break

            if not final_response:
                return None

            final_response.raise_for_status()
            response = final_response

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
            logger.error(f"Error scraping {url}: {e}")
            return None

    def list_sources(self):
        return storage.list_truth_files()
