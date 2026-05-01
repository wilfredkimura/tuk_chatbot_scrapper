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

from workers.pdf_worker import PDFWorker
from workers.image_worker import ImageWorker

class TUKScraperApp:
    def __init__(self, subdomains_file: str, output_base_dir: str):
        self.subdomains_file = subdomains_file
        self.output_base_dir = output_base_dir
        self.parser = HTMLParser()
        self.pdf_worker = PDFWorker()
        self.image_worker = ImageWorker()
        self.cleaner = TextCleaner()
        self.writer = JSONWriter(output_base_dir)
        self.seen_urls_path = os.path.join(output_base_dir, "seen_urls.json")
        self.seen_urls = self.load_seen_urls()

    def load_seen_urls(self) -> set:
        if os.path.exists(self.seen_urls_path):
            try:
                with open(self.seen_urls_path, "r") as f:
                    urls = json.load(f)
                logger.info(f"Loaded {len(urls)} seen URLs from {self.seen_urls_path}")
                return set(urls)
            except Exception as e:
                logger.error(f"Failed to load seen URLs: {e}")
        return set()

    def save_seen_urls(self):
        try:
            with open(self.seen_urls_path, "w") as f:
                json.dump(list(self.seen_urls), f, indent=2)
            logger.info(f"Saved {len(self.seen_urls)} seen URLs to {self.seen_urls_path}")
        except Exception as e:
            logger.error(f"Failed to save seen URLs: {e}")

    def load_subdomains(self):
        with open(self.subdomains_file, "r") as f:
            data = json.load(f)
        return [item["subdomain"] for item in data]

    def get_category(self, url: str, content_type: str) -> str:
        url_lower = url.lower()
        if "admission" in url_lower or "intake" in url_lower:
            return "admissions"
        if "research" in url_lower or "repository" in url_lower:
            return "research"
        if "staff" in url_lower or "portal" in url_lower:
            return "academics"
        if "image" in content_type or "pdf" in content_type:
            return "multimedia"
        return "general"

    async def process_page(self, url: str, content: Any, content_type: str, metadata: Dict[str, Any]):
        try:
            parsed_data = {}
            if "text/html" in content_type:
                parsed_data = self.parser.parse(content, url)
                parsed_data["content"] = self.cleaner.clean(parsed_data["content"])
                parsed_data["source_type"] = "html"
            
            elif "application/pdf" in content_type:
                parsed_data = self.pdf_worker.process(content, url)
                if parsed_data:
                    parsed_data["content"] = self.cleaner.clean(parsed_data["content"])
            
            elif "image" in content_type:
                parsed_data = self.image_worker.process(content, url)
                if parsed_data:
                    parsed_data["content"] = self.cleaner.clean(parsed_data["content"])

            if not parsed_data:
                return

            parsed_data["crawler_metadata"] = metadata
            
            from urllib.parse import urlparse
            subdomain = urlparse(url).netloc
            parsed_data["subdomain"] = subdomain
            
            category = self.get_category(url, content_type)
            parsed_data["category"] = category
            
            # Save to JSON
            self.writer.write(parsed_data, category=category)
            
            # Mark as seen
            self.seen_urls.add(url)
        except Exception as e:
            logger.error(f"Error processing page {url}: {e}")

    async def run(self, limit_subdomains: int = None):
        subdomains = self.load_subdomains()
        if limit_subdomains:
            subdomains = subdomains[:limit_subdomains]
            logger.info(f"Limiting to first {limit_subdomains} subdomains for testing")

        allowed_domains = set(subdomains)
        allowed_domains.add("tukenya.ac.ke")
        allowed_domains.add("www.tukenya.ac.ke")
        
        start_urls = ["https://tukenya.ac.ke"]
        start_urls.extend([f"https://{s}" for s in subdomains])

        crawler = RecursiveCrawler(
            start_urls=start_urls,
            allowed_domains=allowed_domains,
            max_depth=2, # Start with depth 2 for Phase 1
            concurrency=10,
            process_callback=self.process_page,
            already_seen=self.seen_urls
        )

        logger.info(f"Starting crawl for {len(subdomains)} subdomains")
        await crawler.crawl()
        
        # Final save of seen URLs
        self.save_seen_urls()
        logger.info("Crawl completed")

if __name__ == "__main__":
    # Define paths
    context_dir = os.path.join(os.getcwd(), "context")
    subdomains_path = os.path.join(context_dir, "tukenya.ac.ke subdomains.json")
    output_dir = os.path.join(os.getcwd(), "output")

    app = TUKScraperApp(subdomains_path, output_dir)
    
    # Run the app
    # Removing limit to scrape all subdomains
    asyncio.run(app.run())
