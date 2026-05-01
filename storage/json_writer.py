import json
import os
from datetime import datetime
from loguru import logger
from typing import Dict, Any, List

class JSONWriter:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        self.collected_data: List[Dict[str, Any]] = []

    def add_page(self, data: Dict[str, Any], category: str = None):
        """Adds a page's data to the internal list for consolidation."""
        data["scraped_at"] = datetime.now().isoformat()
        if category:
            data["selected_category"] = category
        self.collected_data.append(data)
        logger.debug(f"Collected data for {data.get('url')}")

    def save_run(self, run_mode: str) -> str:
        """Saves all collected data into a single timestamped JSON file and returns the path."""
        if not self.collected_data:
            logger.warning("No data collected to save.")
            return None

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"scraped_data_{run_mode}_{timestamp}.json"
        filepath = os.path.join(self.output_dir, filename)

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(self.collected_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Consolidated run data saved to {filepath} ({len(self.collected_data)} records)")
            # Clear for next run if reuse
            self.collected_data = []
            return filepath
        except Exception as e:
            logger.error(f"Failed to save consolidated JSON to {filepath}: {e}")
            return None
