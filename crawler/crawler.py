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
        connector = aiohttp.TCPConnector(ssl=False) # Disable SSL check for university sites if needed
        async with aiohttp.ClientSession(headers=self.headers, connector=connector) as session:
            tasks = [self._crawl_url(url, 0, session) for url in self.start_urls]
            await asyncio.gather(*tasks)

    async def _crawl_url(self, url: str, depth: int, session: aiohttp.ClientSession):
        if depth > self.max_depth or url in self.visited:
            return

        if url in self.already_seen:
            logger.info(f"Skipping {url} (already scraped)")
            return

        from urllib.parse import urlparse
        domain = urlparse(url).netloc
        if domain in self.failed_domains:
            logger.info(f"Skipping {url} (domain {domain} previously failed)")
            return

        self.visited.add(url)

        async with self.semaphore:
            if not await self.robots.can_fetch(url, self.headers["User-Agent"], headers=self.headers):
                logger.info(f"Skipping {url} (robots.txt)")
                return

            try:
                # Use a slightly shorter timeout for individual requests to move faster
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as response:
                    if response.status != 200:
                        logger.warning(f"Failed to fetch {url}: status {response.status}")
                        return

                    content_type = response.headers.get("Content-Type", "").lower()
                    
                    if "text/html" in content_type:
                        html = await response.text()
                        logger.info(f"Fetched HTML {url} (depth {depth})")
                        if self.process_callback:
                            await self.process_callback(url, html, content_type, {"depth": depth})
                        
                        # Discover links only in HTML
                        links = self.discovery.extract_links(html, url)
                        new_links = [l for l in links if l not in self.visited and l not in self.already_seen]
                        if depth < self.max_depth:
                            await asyncio.gather(*[self._crawl_url(l, depth + 1, session) for l in new_links])
                    
                    elif "application/pdf" in content_type:
                        content = await response.read()
                        logger.info(f"Fetched PDF {url}")
                        if self.process_callback:
                            await self.process_callback(url, content, content_type, {"depth": depth})
                    
                    elif any(img_type in content_type for img_type in ["image/jpeg", "image/png", "image/gif"]):
                        content = await response.read()
                        logger.info(f"Fetched Image {url}")
                        if self.process_callback:
                            await self.process_callback(url, content, content_type, {"depth": depth})
                    
                    else:
                        logger.info(f"Skipping {url} (unsupported content type: {content_type})")

            except (asyncio.TimeoutError, aiohttp.ClientConnectorError) as e:
                logger.error(f"Network error crawling {url}: {type(e).__name__}")
                # If a root domain fails, mark it as failed
                if depth == 0:
                    logger.error(f"Marking domain {domain} as failed")
                    self.failed_domains.add(domain)
            except Exception as e:
                logger.error(f"Error crawling {url}: {type(e).__name__}: {e}")
