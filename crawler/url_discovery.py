import re
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from typing import Set

class URLDiscovery:
    def __init__(self, allowed_domains: Set[str]):
        self.allowed_domains = allowed_domains

    def is_valid(self, url: str) -> bool:
        parsed = urlparse(url)
        # Check if it's a valid http/https URL
        if parsed.scheme not in ["http", "https"]:
            return False
        
        # Check if it's within allowed domains (subdomains of tukenya.ac.ke)
        domain = parsed.netloc
        if any(domain == d or domain.endswith("." + d) for d in self.allowed_domains):
            return True
        
        return False

    def extract_links(self, html: str, base_url: str) -> Set[str]:
        soup = BeautifulSoup(html, "lxml")
        links = set()
        for a in soup.find_all("a", href=True):
            href = a["href"]
            full_url = urljoin(base_url, href)
            # Remove fragments
            full_url = full_url.split("#")[0]
            if self.is_valid(full_url):
                links.add(full_url)
        return links
