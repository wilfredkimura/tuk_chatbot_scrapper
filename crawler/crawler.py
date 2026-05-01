import asyncio
import aiohttp
from loguru import logger
from typing import Set, List, Dict, Any, Callable
from .robots import RobotsHandler
from .url_discovery import URLDiscovery

class RecursiveCrawler:
    def __init__(
        self, 
        start_urls: List[str], 
        allowed_domains: Set[str],
        max_depth: int = 3,
        concurrency: int = 5,
        process_callback: Callable[[str, Any, str, Dict[str, Any]], asyncio.Future] = None,
        already_seen: Set[str] = None
    ):
        self.start_urls = start_urls
        self.discovery = URLDiscovery(allowed_domains)
        self.robots = RobotsHandler()
        self.max_depth = max_depth
        self.semaphore = asyncio.Semaphore(concurrency)
        self.visited: Set[str] = set()
        self.already_seen = already_seen or set()
        self.failed_domains: Set[str] = set()
        self.process_callback = process_callback
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.google.com/",
            "Connection": "keep-alive"
        }

    async def crawl(self):
        self.total_pages_scraped = 0
        self.total_roots = len(self.start_urls)
        self.completed_roots = 0
        
        connector = aiohttp.TCPConnector(ssl=False) # Disable SSL check for university sites if needed
        async with aiohttp.ClientSession(headers=self.headers, connector=connector) as session:
            tasks = [self._crawl_url(url, 0, session) for url in self.start_urls]
            
            for task in asyncio.as_completed(tasks):
                await task
                self.completed_roots += 1
                self._print_overall_progress()

    def _print_overall_progress(self):
        percent = (self.completed_roots / self.total_roots) * 100
        bar_length = 30
        filled_length = int(bar_length * self.completed_roots // self.total_roots)
        bar = '█' * filled_length + '-' * (bar_length - filled_length)
        
        # Use carriage return to stay on the same line if possible, 
        # but with loguru output it might just print new lines.
        # We'll print a clear status message.
        print(f"\rProgress: |{bar}| {percent:.1f}% ({self.completed_roots}/{self.total_roots} subdomains completed) | Pages Scraped: {self.total_pages_scraped}", end="\n")

    async def _crawl_url(self, url: str, depth: int, session: aiohttp.ClientSession):
        if depth > self.max_depth or url in self.visited:
            return

        if url in self.already_seen:
            # logger.info(f"Skipping {url} (already scraped)")
            return

        from urllib.parse import urlparse
        domain = urlparse(url).netloc
        if domain in self.failed_domains:
            return

        self.visited.add(url)

        async with self.semaphore:
            if not await self.robots.can_fetch(url, self.headers["User-Agent"], headers=self.headers):
                return

            try:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as response:
                    if response.status != 200:
                        return

                    content_type = response.headers.get("Content-Type", "").lower()
                    
                    if "text/html" in content_type:
                        html = await response.text()
                        if self.process_callback:
                            await self.process_callback(url, html, content_type, {"depth": depth})
                        
                        self.total_pages_scraped += 1
                        
                        # Discover links only in HTML
                        links = self.discovery.extract_links(html, url)
                        new_links = [l for l in links if l not in self.visited and l not in self.already_seen]
                        if depth < self.max_depth:
                            await asyncio.gather(*[self._crawl_url(l, depth + 1, session) for l in new_links])
                    
                    elif "application/pdf" in content_type:
                        content = await response.read()
                        if self.process_callback:
                            await self.process_callback(url, content, content_type, {"depth": depth})
                        self.total_pages_scraped += 1
                    
                    elif any(img_type in content_type for img_type in ["image/jpeg", "image/png", "image/gif"]):
                        content = await response.read()
                        if self.process_callback:
                            await self.process_callback(url, content, content_type, {"depth": depth})
                        self.total_pages_scraped += 1
                    
            except (asyncio.TimeoutError, aiohttp.ClientConnectorError):
                if depth == 0:
                    self.failed_domains.add(domain)
            except Exception as e:
                logger.error(f"Error crawling {url}: {type(e).__name__}: {e}")
