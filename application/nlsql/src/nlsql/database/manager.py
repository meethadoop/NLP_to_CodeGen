from typing import Optional
from .database import Database

class DatabaseManager:
    _instance: Optional[Database] = None
    
    @classmethod
    def initialize(cls, db_path: str):
        """Initialize database connection"""
        if cls._instance is None:
            cls._instance = Database(db_path)
    
    @classmethod
    def get_instance(cls) -> Database:
        """Get database instance"""
        if cls._instance is None:
            raise RuntimeError("Database not initialized")
        return cls._instance
