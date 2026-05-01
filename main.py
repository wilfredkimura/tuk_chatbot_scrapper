import asyncio
import json
import os
import sys
from datetime import datetime
from loguru import logger
from crawler.crawler import RecursiveCrawler
from parsers.html_parser import HTMLParser
from normalizers.text_cleaner import TextCleaner
from storage.json_writer import JSONWriter
from typing import Dict, Any, List

# Configure loguru
logger.add("logs/scraper.log", rotation="10 MB", level="INFO")

from workers.pdf_worker import PDFWorker
from workers.image_worker import ImageWorker

ASCII_LOGO = r"""
  _____ _   _   _  __
 |_   _| | | | | |/ /
   | | | | | | | ' / 
   | | | |_| | | . \ 
   |_|  \___/  |_|\_\
  SCRAPER TOOL V1.0
"""

TOOL_DESCRIPTION = """
This tool is designed to crawl and extract data from Technical University of Kenya (TUK) subdomains.
It supports HTML parsing, PDF text extraction, and Image OCR processing.
Data is categorized and consolidated into a single JSON file for easy import/export.
"""

CATEGORIES_INFO = """
Data Categories:
- Admissions: Enrollment, intake, and application information.
- Academics: Staff portals, calendars, and academic resources.
- Research: Institutional repositories and research publications.
- Multimedia: Extracted text from PDF documents and images.
- General: General university information and news.
"""

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
                logger.info(f"Loaded {len(urls)} seen URLs")
                return set(urls)
            except Exception as e:
                logger.error(f"Failed to load seen URLs: {e}")
        return set()

    def save_seen_urls(self):
        try:
            with open(self.seen_urls_path, "w") as f:
                json.dump(list(self.seen_urls), f, indent=2)
            logger.info(f"Saved {len(self.seen_urls)} seen URLs")
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
            
            # Add to consolidated list
            self.writer.add_page(parsed_data, category=category)
            
            # Mark as seen
            self.seen_urls.add(url)
        except Exception as e:
            logger.error(f"Error processing page {url}: {e}")

    async def run(self, mode: str = "full", subdomains: List[str] = None):
        all_config_subdomains = self.load_subdomains()
        
        if mode == "targeted" and subdomains:
            logger.info(f"Targeted mode: crawling {len(subdomains)} domains")
        else:
            subdomains = all_config_subdomains
            logger.info(f"Full mode: crawling {len(subdomains)} subdomains")

        allowed_domains = set(all_config_subdomains)
        allowed_domains.add("tukenya.ac.ke")
        allowed_domains.add("www.tukenya.ac.ke")
        if mode == "targeted":
            for s in subdomains:
                allowed_domains.add(s)
        
        start_urls = []
        if mode == "full":
            start_urls.append("https://tukenya.ac.ke")
        
        start_urls.extend([f"https://{s}" for s in subdomains])

        crawler = RecursiveCrawler(
            start_urls=start_urls,
            allowed_domains=allowed_domains,
            max_depth=2,
            concurrency=10,
            process_callback=self.process_page,
            already_seen=self.seen_urls
        )

        try:
            print(f"\n[INFO] Starting scrape. Data will be saved in: {os.path.abspath(self.output_base_dir)}")
            await crawler.crawl()
            success = True
        except asyncio.CancelledError:
            print("\n[WARNING] Scrape was interrupted by user.")
            success = False
        except Exception as e:
            print(f"\n[ERROR] An unexpected error occurred during scraping: {e}")
            logger.exception("Scrape failed")
            success = False
        finally:
            # Save persistence
            self.save_seen_urls()
            
            # Save consolidated JSON
            output_file = self.writer.save_run(mode)
            
            if success and output_file:
                abs_path = os.path.abspath(output_file)
                print(f"\n" + "="*50)
                print(f"SCRAPE COMPLETED SUCCESSFULLY")
                print(f"Total Pages Scraped: {crawler.total_pages_scraped}")
                print(f"Output File: {abs_path}")
                print("="*50)
                logger.info(f"Crawl completed. Output: {abs_path}")
            elif not success:
                if output_file:
                    print(f"\n[INFO] Script terminated. Partial data saved to: {os.path.abspath(output_file)}")
                    print(f"Total Pages Scraped in this session: {crawler.total_pages_scraped}")
                else:
                    print("\n[INFO] Script terminated. No data was collected.")
        
        return success

def validate_json_domains(input_str: str) -> List[str]:
    try:
        data = json.loads(input_str)
        if not isinstance(data, list):
            raise ValueError("Input must be a JSON list.")
        if not all(isinstance(item, str) for item in data):
            raise ValueError("All items in the list must be strings.")
        return data
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON format. Please ensure you paste a valid JSON list.")

def main_menu():
    context_dir = os.path.join(os.getcwd(), "context")
    subdomains_path = os.path.join(context_dir, "tukenya.ac.ke subdomains.json")
    output_dir = os.path.join(os.getcwd(), "output")

    app = TUKScraperApp(subdomains_path, output_dir)

    try:
        while True:
            print(ASCII_LOGO)
            print(TOOL_DESCRIPTION)
            print(f"Data will be stored in: {os.path.abspath(output_dir)}")
            print(CATEGORIES_INFO)
            print("--- Menu ---")
            print("1. Full Scrape (All subdomains)")
            print("2. Targeted Scrape (JSON list of domains)")
            print("3. Reset and Scrape (Clear history first)")
            print("4. Exit")
            
            choice = input("\nSelect an option (1-4): ")

            if choice == "1":
                asyncio.run(app.run(mode="full"))
            elif choice == "2":
                print("\nPlease paste the list of domains in JSON format (e.g., [\"sub1.tukenya.ac.ke\", \"sub2.tukenya.ac.ke\"])")
                json_input = input("JSON Input: ")
                try:
                    target_domains = validate_json_domains(json_input)
                    asyncio.run(app.run(mode="targeted", subdomains=target_domains))
                except ValueError as e:
                    print(f"\n[ERROR] {e}")
            elif choice == "3":
                confirm = input("This will clear all history. Continue? (y/n): ")
                if confirm.lower() == 'y':
                    app.seen_urls = set()
                    if os.path.exists(app.seen_urls_path):
                        os.remove(app.seen_urls_path)
                    print("History cleared.")
                    asyncio.run(app.run(mode="full"))
            elif choice == "4":
                print("Exiting...")
                break
            else:
                print("Invalid choice, please try again.")
    except KeyboardInterrupt:
        print("\n\n[INFO] Script terminated by user (Ctrl+C). Exiting...")
    except Exception as e:
        print(f"\n\n[FATAL ERROR] {e}")
        logger.exception("Fatal error in main menu")
    finally:
        print("\nThank you for using the TU-Kenya Scraper Tool.")

if __name__ == "__main__":
    main_menu()
