import asyncio
import json
import os
from loguru import logger
from crawler.crawler import RecursiveCrawler
from parsers.html_parser import HTMLParser
from normalizers.text_cleaner import TextCleaner
from storage.json_writer import JSONWriter
from typing import Dict, Any

# Configure loguru
logger.add("logs/scraper.log", rotation="10 MB", level="INFO")

class TUKScraperApp:
    def __init__(self, subdomains_file: str, output_base_dir: str):
        self.subdomains_file = subdomains_file
        self.output_base_dir = output_base_dir
        self.parser = HTMLParser()
        self.cleaner = TextCleaner()
        self.writer = JSONWriter(output_base_dir)

    def load_subdomains(self):
        with open(self.subdomains_file, "r") as f:
            data = json.load(f)
        return [item["subdomain"] for item in data]

    async def process_page(self, url: str, html: str, metadata: Dict[str, Any]):
        try:
            # Parse HTML
            parsed_data = self.parser.parse(html, url)
            
            # Clean text
            parsed_data["content"] = self.cleaner.clean(parsed_data["content"])
            
            # Add metadata from crawler
            parsed_data["crawler_metadata"] = metadata
            
            # Extract subdomain for categorization
            from urllib.parse import urlparse
            subdomain = urlparse(url).netloc
            parsed_data["subdomain"] = subdomain
            
            # Save to JSON
            self.writer.write(parsed_data)
        except Exception as e:
            logger.error(f"Error processing page {url}: {e}")

    async def run(self, limit_subdomains: int = None):
        subdomains = self.load_subdomains()
        if limit_subdomains:
            subdomains = subdomains[:limit_subdomains]
            logger.info(f"Limiting to first {limit_subdomains} subdomains for testing")

        allowed_domains = set(subdomains)
        start_urls = [f"https://{s}" for s in subdomains]

        crawler = RecursiveCrawler(
            start_urls=start_urls,
            allowed_domains=allowed_domains,
            max_depth=2, # Start with depth 2 for Phase 1
            concurrency=10,
            process_callback=self.process_page
        )

        logger.info(f"Starting crawl for {len(subdomains)} subdomains")
        await crawler.crawl()
        logger.info("Crawl completed")

if __name__ == "__main__":
    # Define paths
    context_dir = os.path.join(os.getcwd(), "context")
    subdomains_path = os.path.join(context_dir, "tukenya.ac.ke subdomains.json")
    output_dir = os.path.join(os.getcwd(), "output")

    app = TUKScraperApp(subdomains_path, output_dir)
    
    # Run the app
    # For initial testing, we can limit the subdomains
    asyncio.run(app.run(limit_subdomains=3))
