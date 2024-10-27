import sqlite3
from typing import Dict, Any, List
import logging
from ..utils.logger import get_logger

logger = get_logger(__name__)

class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        """Initialize the database with sample tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create users table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY,
                        name TEXT NOT NULL,
                        age INTEGER,
                        email TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create orders table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS orders (
                        id INTEGER PRIMARY KEY,
                        user_id INTEGER,
                        total_amount DECIMAL(10, 2),
                        status TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    )
                """)
                
                # Create products table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS products (
                        id INTEGER PRIMARY KEY,
                        name TEXT NOT NULL,
                        price DECIMAL(10, 2),
                        category TEXT,
                        stock INTEGER,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Add sample data if tables are empty
                self._insert_sample_data(cursor)
                
                conn.commit()
                logger.info("Database initialized successfully")
                
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
            raise

    def _insert_sample_data(self, cursor):
        """Insert sample data into tables"""
        # Check if users table is empty
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            cursor.executemany(
                "INSERT INTO users (name, age, email) VALUES (?, ?, ?)",
                [
                    ("John Doe", 28, "john@example.com"),
                    ("Jane Smith", 32, "jane@example.com"),
                    ("Bob Johnson", 45, "bob@example.com"),
                    ("Alice Brown", 29, "alice@example.com"),
                    ("Charlie Wilson", 35, "charlie@example.com")
                ]
            )
            
        # Check if products table is empty
        cursor.execute("SELECT COUNT(*) FROM products")
        if cursor.fetchone()[0] == 0:
            cursor.executemany(
                "INSERT INTO products (name, price, category, stock) VALUES (?, ?, ?, ?)",
                [
                    ("Laptop", 999.99, "Electronics", 50),
                    ("Smartphone", 599.99, "Electronics", 100),
                    ("Desk Chair", 199.99, "Furniture", 30),
                    ("Coffee Maker", 79.99, "Appliances", 75),
                    ("Headphones", 149.99, "Electronics", 200)
                ]
            )
            
        # Check if orders table is empty
        cursor.execute("SELECT COUNT(*) FROM orders")
        if cursor.fetchone()[0] == 0:
            cursor.executemany(
                "INSERT INTO orders (user_id, total_amount, status) VALUES (?, ?, ?)",
                [
                    (1, 999.99, "completed"),
                    (2, 799.98, "completed"),
                    (3, 199.99, "pending"),
                    (1, 149.99, "completed"),
                    (4, 679.98, "processing")
                ]
            )

    def execute_query(self, query: str) -> List[Dict[str, Any]]:
        """Execute SQL query and return results as list of dictionaries"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(query)
                results = [dict(row) for row in cursor.fetchall()]
                return results
        except Exception as e:
            logger.error(f"Error executing query: {str(e)}")
            raise

    def get_schema(self) -> Dict[str, List[str]]:
        """Get database schema information"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                schema = {}
                
                # Get all tables
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name NOT LIKE 'sqlite_%'
                """)
                tables = cursor.fetchall()
                
                # Get columns for each table
                for (table_name,) in tables:
                    cursor.execute(f"PRAGMA table_info({table_name})")
                    columns = cursor.fetchall()
                    schema[table_name] = [col[1] for col in columns]
                
                return schema
        except Exception as e:
            logger.error(f"Error getting schema: {str(e)}")
            raise
