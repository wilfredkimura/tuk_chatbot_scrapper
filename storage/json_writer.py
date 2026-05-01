import json
import os
import re
from datetime import datetime
from loguru import logger
from typing import Dict, Any

class JSONWriter:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def write(self, data: Dict[str, Any], category: str = None):
        # Create a filename based on URL or title
        url = data.get("url", "unknown")
        # Sanitize filename: remove protocol and replace invalid characters
        filename = url.replace("https://", "").replace("http://", "")
        # Replace non-alphanumeric (except . - _) with _
        filename = re.sub(r'[^a-zA-Z0-9.\-_]', '_', filename)
        
        if len(filename) > 150:
            filename = filename[:150]
        
        target_dir = self.output_dir
        if category:
            target_dir = os.path.join(self.output_dir, category)
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)

        filepath = os.path.join(target_dir, f"{filename}.json")
        
        # Add timestamp
        data["scraped_at"] = datetime.now().isoformat()
        
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.debug(f"Saved data to {filepath}")
        except Exception as e:
            logger.error(f"Failed to save JSON to {filepath}: {e}")
