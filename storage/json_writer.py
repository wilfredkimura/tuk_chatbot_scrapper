import json
import os
from datetime import datetime
from loguru import logger
from typing import Dict, Any

class JSONWriter:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def write(self, data: Dict[str, Any]):
        # Create a filename based on URL or title
        url = data.get("url", "unknown")
        # Sanitize filename
        filename = url.replace("https://", "").replace("http://", "").replace("/", "_").replace(".", "_")
        if len(filename) > 100:
            filename = filename[:100]
        
        filepath = os.path.join(self.output_dir, f"{filename}.json")
        
        # Add timestamp
        data["scraped_at"] = datetime.now().isoformat()
        
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.debug(f"Saved data to {filepath}")
        except Exception as e:
            logger.error(f"Failed to save JSON to {filepath}: {e}")
