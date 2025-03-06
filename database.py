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
            feedback INTEGER DEFAULT NULL,
            curated_response TEXT DEFAULT NULL
        )
    """)
    
    conn.commit()
    conn.close()

def save_curated_response(message_id, curated_response):
    """Save a curated response for a negative feedback"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE chat_history 
        SET curated_response = ? 
        WHERE id = ?
    """, (curated_response, message_id))
    conn.commit()
    conn.close()

def find_similar_question(current_question):
    """Find similar previous questions with positive feedback or curated responses"""
    if not current_question:
        return None
        
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT user_message, ai_response, curated_response, feedback
            FROM chat_history
            WHERE (feedback = 1 OR curated_response IS NOT NULL)
            ORDER BY timestamp DESC
        """)
        results = cursor.fetchall()
        
        # Simple text similarity (you might want to use better methods like cosine similarity)
        current_words = set(current_question.lower().split())
        for msg, response, curated, feedback in results:
            if msg and current_words:  # Add null checks
                msg_words = set(msg.lower().split())
                # Check if there's at least 50% word overlap
                if len(current_words.intersection(msg_words)) / len(current_words) >= 0.5:
                    return curated if curated else response
        return None
    except Exception as e:
        print(f"Error in find_similar_question: {e}")
        return None
    finally:
        conn.close()