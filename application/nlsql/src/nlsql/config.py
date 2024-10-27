import os
from typing import Dict, Any

class Config:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.db_path = os.getenv("DB_PATH", "data/database.db")
        self.log_level = os.getenv("LOG_LEVEL", "INFO")

def load_config() -> Config:
    """Load configuration from environment variables"""
    return Config()
