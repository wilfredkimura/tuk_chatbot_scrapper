from bs4 import BeautifulSoup
from typing import Dict, Any, List
import re

class HTMLParser:
    def __init__(self):
        pass

    def parse(self, html: str, url: str) -> Dict[str, Any]:
        soup = BeautifulSoup(html, "lxml")
        
        # Remove script and style elements
        for script_or_style in soup(["script", "style", "nav", "footer", "header"]):
            script_or_style.decompose()

        title = soup.title.string if soup.title else ""
        
        # Extract headings
        headings = []
        for i in range(1, 7):
            for h in soup.find_all(f"h{i}"):
                headings.append({"level": i, "text": h.get_text(strip=True)})

        # Extract text content
        # We try to get the "main" content if possible, otherwise body
        main_content = soup.find("main") or soup.find("article") or soup.find("div", id="content") or soup.body
        
        if main_content:
            text = main_content.get_text(separator="\n", strip=True)
        else:
            text = soup.get_text(separator="\n", strip=True)

        # Extract metadata
        metadata = {}
        for meta in soup.find_all("meta"):
            name = meta.get("name") or meta.get("property")
            content = meta.get("content")
            if name and content:
                metadata[name] = content

        # Extract tables
        tables = []
        for table in soup.find_all("table"):
            rows = []
            for tr in table.find_all("tr"):
                cells = [td.get_text(strip=True) for td in tr.find_all(["td", "th"])]
                if cells:
                    rows.append(cells)
            if rows:
                tables.append(rows)

        return {
            "title": title,
            "url": url,
            "headings": headings,
            "content": text,
            "metadata": metadata,
            "tables": tables
        }
