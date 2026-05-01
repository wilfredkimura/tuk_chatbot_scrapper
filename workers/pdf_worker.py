import pdfplumber
import io
from loguru import logger
from typing import Dict, Any

class PDFWorker:
    def __init__(self):
        pass

    def process(self, content: bytes, url: str) -> Dict[str, Any]:
        try:
            text = ""
            tables = []
            metadata = {}
            
            with pdfplumber.open(io.BytesIO(content)) as pdf:
                metadata = pdf.metadata
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                    
                    page_tables = page.extract_tables()
                    if page_tables:
                        tables.extend(page_tables)

            return {
                "title": metadata.get("Title", url.split("/")[-1]),
                "url": url,
                "content": text.strip(),
                "metadata": metadata,
                "tables": tables,
                "source_type": "pdf"
            }
        except Exception as e:
            logger.error(f"Error processing PDF {url}: {e}")
            return {}
