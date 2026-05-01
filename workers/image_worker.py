from PIL import Image
import pytesseract
import io
from loguru import logger
from typing import Dict, Any

class ImageWorker:
    def __init__(self):
        pass

    def process(self, content: bytes, url: str) -> Dict[str, Any]:
        try:
            image = Image.open(io.BytesIO(content))
            
            # Basic OCR
            text = ""
            try:
                text = pytesseract.image_to_string(image)
            except Exception as ocr_err:
                logger.warning(f"OCR failed for {url}: {ocr_err}. Is Tesseract installed?")
                text = "[OCR Failed or Tesseract not found]"

            return {
                "title": url.split("/")[-1],
                "url": url,
                "content": text.strip(),
                "metadata": {
                    "format": image.format,
                    "size": image.size,
                    "mode": image.mode
                },
                "source_type": "image"
            }
        except Exception as e:
            logger.error(f"Error processing image {url}: {e}")
            return {}
