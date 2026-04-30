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
        process_callback: Callable[[str, str, Dict[str, Any]], asyncio.Future] = None
    ):
        self.start_urls = start_urls
        self.discovery = URLDiscovery(allowed_domains)
        self.robots = RobotsHandler()
        self.max_depth = max_depth
        self.semaphore = asyncio.Semaphore(concurrency)
        self.visited: Set[str] = set()
        self.process_callback = process_callback
        self.user_agent = "TUK-Knowledge-Engine-Bot/1.0"

    async def crawl(self):
        tasks = [self._crawl_url(url, 0) for url in self.start_urls]
        await asyncio.gather(*tasks)

    async def _crawl_url(self, url: str, depth: int):
        if depth > self.max_depth or url in self.visited:
            return

        self.visited.add(url)

        if not await self.robots.can_fetch(url, self.user_agent):
            logger.info(f"Skipping {url} (robots.txt)")
            return

        async with self.semaphore:
            try:
                async with aiohttp.ClientSession(headers={"User-Agent": self.user_agent}) as session:
                    async with session.get(url, timeout=10) as response:
                        if response.status != 200:
                            logger.warning(f"Failed to fetch {url}: status {response.status}")
                            return

                        content_type = response.headers.get("Content-Type", "")
                        if "text/html" not in content_type:
                            logger.info(f"Skipping {url} (non-HTML content: {content_type})")
                            # In future phases, route to other workers (PDF, etc.)
                            return

                        html = await response.text()
                        logger.info(f"Fetched {url} (depth {depth})")

                        # Process content
                        if self.process_callback:
                            await self.process_callback(url, html, {"depth": depth})

                        # Discover links
                        links = self.discovery.extract_links(html, url)
                        new_links = [l for l in links if l not in self.visited]
                        
                        if depth < self.max_depth:
                            await asyncio.gather(*[self._crawl_url(l, depth + 1) for l in new_links])

            except Exception as e:
                logger.error(f"Error crawling {url}: {e}")
