import sqlite3
import os
from datetime import datetime

DATABASE_FILE = "chat_history.db"

def adapt_datetime(ts):
    """Convert datetime to SQLite timestamp string"""
    return ts.isoformat()

def convert_datetime(ts):
    """Convert SQLite timestamp string back to datetime"""
    return datetime.fromisoformat(ts)

def get_connection():
    """Create a database connection"""
    conn = sqlite3.connect(DATABASE_FILE, detect_types=sqlite3.PARSE_DECLTYPES)
    # Register datetime adapter and converter
    sqlite3.register_adapter(datetime, adapt_datetime)
    sqlite3.register_converter("timestamp", convert_datetime)
    return conn

def init_db():
    """Initialize the database with required tables"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create chat history table with explicit timestamp type
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TIMESTAMP NOT NULL,
            user_message TEXT NOT NULL,
            ai_response TEXT NOT NULL,
            feedback INTEGER DEFAULT NULL
        )
    """)
    
    conn.commit()
    conn.close()