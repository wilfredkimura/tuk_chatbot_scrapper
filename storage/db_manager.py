import sqlite3
import json
import os
from datetime import datetime
from loguru import logger
from typing import Dict, Any

class DatabaseManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS scraped_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT UNIQUE,
                    subdomain TEXT,
                    category TEXT,
                    content TEXT,
                    metadata TEXT,
                    scraped_at TEXT
                )
            ''')
            conn.commit()
            conn.close()
            logger.info(f"Database initialized at {self.db_path}")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")

    def insert_page(self, data: Dict[str, Any]):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            url = data.get("url")
            subdomain = data.get("subdomain")
            category = data.get("category")
            content = data.get("content", "")
            metadata = json.dumps(data.get("crawler_metadata", {}))
            scraped_at = data.get("scraped_at", datetime.now().isoformat())

            cursor.execute('''
                INSERT OR REPLACE INTO scraped_data 
                (url, subdomain, category, content, metadata, scraped_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (url, subdomain, category, content, metadata, scraped_at))
            
            conn.commit()
            conn.close()
            logger.debug(f"Inserted/Updated {url} in database")
        except Exception as e:
            logger.error(f"Failed to insert data for {data.get('url')}: {e}")

    def clear_all(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM scraped_data')
            conn.commit()
            conn.close()
            logger.info("Database cleared")
        except Exception as e:
            logger.error(f"Failed to clear database: {e}")
