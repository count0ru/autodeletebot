import sqlite3
import datetime
from typing import List, Tuple
import logging

class MessageDatabase:
    """Database manager for storing and managing messages scheduled for deletion.
    
    This class handles all database operations including adding messages,
    retrieving messages to delete, and cleaning up old records.
    """
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Initialize the database with required tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        message_id INTEGER NOT NULL,
                        chat_id INTEGER NOT NULL,
                        forward_date TIMESTAMP NOT NULL,
                        delete_date TIMESTAMP NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                conn.commit()
                logging.info("Database initialized successfully")
        except Exception as e:
            logging.error("Error initializing database: %s", e)

    def add_message(self, message_id: int, chat_id: int, forward_date: datetime.datetime):
        """Add a new message to the database"""
        try:
            import config
            delete_date = forward_date + datetime.timedelta(minutes=config.DELETE_AFTER_MINUTES)
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO messages (message_id, chat_id, forward_date, delete_date)
                    VALUES (?, ?, ?, ?)
                ''', (message_id, chat_id, forward_date, delete_date))
                conn.commit()
                logging.info("Message %s added to database, will be deleted on %s", message_id, delete_date)
                return True
        except Exception as e:
            logging.error("Error adding message to database: %s", e)
            return False

    def get_messages_to_delete(self) -> List[Tuple[int, int, int]]:
        """Get all messages that should be deleted (message_id, chat_id, message_id)"""
        try:
            current_time = datetime.datetime.now()
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT message_id, chat_id, id FROM messages
                    WHERE delete_date <= ? AND message_id IS NOT NULL
                ''', (current_time,))
                return cursor.fetchall()
        except Exception as e:
            logging.error("Error getting messages to delete: %s", e)
            return []

    def delete_message_record(self, record_id: int):
        """Remove a message record from the database after deletion"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM messages WHERE id = ?', (record_id,))
                conn.commit()
                logging.info("Message record %s removed from database", record_id)
                return True
        except Exception as e:
            logging.error("Error deleting message record: %s", e)
            return False

    def cleanup_old_records(self, days: int = 7):
        """Clean up old records that are older than specified days"""
        try:
            cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days)
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM messages WHERE created_at < ?', (cutoff_date,))
                deleted_count = cursor.rowcount
                conn.commit()
                if deleted_count > 0:
                    logging.info("Cleaned up %s old records", deleted_count)
                return deleted_count
        except Exception as e:
            logging.error("Error cleaning up old records: %s", e)
            return 0
