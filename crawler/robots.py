from urllib.robotparser import RobotFileParser
from loguru import logger
import aiohttp
import asyncio

class RobotsHandler:
    def __init__(self):
        self.parsers = {}

    async def can_fetch(self, url: str, user_agent: str = "*") -> bool:
        from urllib.parse import urlparse
        parsed_url = urlparse(url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        robots_url = f"{base_url}/robots.txt"

        if base_url not in self.parsers:
            parser = RobotFileParser()
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(robots_url, timeout=5) as response:
                        if response.status == 200:
                            content = await response.text()
                            parser.parse(content.splitlines())
                        else:
                            # If no robots.txt, assume allowed
                            parser.parse(["User-agent: *", "Allow: /"])
            except Exception as e:
                logger.warning(f"Could not fetch robots.txt for {base_url}: {e}")
                parser.parse(["User-agent: *", "Allow: /"])
            
            self.parsers[base_url] = parser

        return self.parsers[base_url].can_fetch(user_agent, url)
