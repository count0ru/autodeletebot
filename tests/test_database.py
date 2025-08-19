"""Unit tests for the MessageDatabase class."""

import unittest
import tempfile
import os
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import MessageDatabase


class TestMessageDatabase(unittest.TestCase):
    """Test cases for MessageDatabase class."""

    def setUp(self):
        """Set up test database."""
        # Create temporary database file
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db = MessageDatabase(self.temp_db.name)

    def tearDown(self):
        """Clean up test database."""
        # Remove temporary database file
        os.unlink(self.temp_db.name)

    def test_init_database(self):
        """Test database initialization."""
        # Check if database file was created
        self.assertTrue(os.path.exists(self.temp_db.name))

        # Check if messages table exists by trying to add a message
        message_id = 123
        chat_id = 456
        forward_date = datetime.now()

        result = self.db.add_message(message_id, chat_id, forward_date)
        self.assertTrue(result)

    def test_add_message(self):
        """Test adding a message to database."""
        message_id = 123
        chat_id = 456
        forward_date = datetime.now()

        result = self.db.add_message(message_id, chat_id, forward_date)
        self.assertTrue(result)

        # Verify message was added by checking if it's in get_messages_to_delete
        # (it won't be returned yet since it's not expired)
        messages = self.db.get_messages_to_delete()
        self.assertEqual(len(messages), 0)

    def test_add_message_with_future_date(self):
        """Test adding a message with future date."""
        message_id = 123
        chat_id = 456
        forward_date = datetime.now() + timedelta(days=1)

        result = self.db.add_message(message_id, chat_id, forward_date)
        self.assertTrue(result)

    def test_get_messages_to_delete(self):
        """Test retrieving messages that should be deleted."""
        # Add a message with past date (should be eligible for deletion)
        # Use 61 days to ensure it's older than the default 60 days (86400 minutes)
        message_id = 123
        chat_id = 456
        past_date = datetime.now() - timedelta(days=61)

        self.db.add_message(message_id, chat_id, past_date)

        # Get messages to delete
        messages = self.db.get_messages_to_delete()
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0][0], message_id)  # message_id
        self.assertEqual(messages[0][1], chat_id)    # chat_id

    def test_delete_message_record(self):
        """Test deleting a message record."""
        # Add a message first
        message_id = 123
        chat_id = 456
        forward_date = datetime.now()

        self.db.add_message(message_id, chat_id, forward_date)

        # Get the record ID from get_messages_to_delete
        messages = self.db.get_messages_to_delete()
        if messages:
            record_id = messages[0][2]  # record ID is the third element

            # Delete the record
            result = self.db.delete_message_record(record_id)
            self.assertTrue(result)

            # Verify it's gone
            messages_after = self.db.get_messages_to_delete()
            self.assertEqual(len(messages_after), 0)

    def test_cleanup_old_records(self):
        """Test cleaning up old records."""
        # Add a message
        message_id = 123
        chat_id = 456
        forward_date = datetime.now()

        self.db.add_message(message_id, chat_id, forward_date)

        # Clean up records older than 1 day (should remove our recent record)
        deleted_count = self.db.cleanup_old_records(days=1)
        self.assertEqual(deleted_count, 0)  # Record is not old enough

        # Clean up records older than 0 days (should remove our record)
        deleted_count = self.db.cleanup_old_records(days=0)
        self.assertEqual(deleted_count, 1)  # Record should be removed

    def test_add_message_invalid_data(self):
        """Test adding message with invalid data."""
        # Test with None values
        result = self.db.add_message(None, 456, datetime.now())
        self.assertFalse(result)

        result = self.db.add_message(123, None, datetime.now())
        self.assertFalse(result)

        result = self.db.add_message(123, 456, None)
        self.assertFalse(result)

    def test_database_connection_error(self):
        """Test database connection error handling."""
        # Create database with invalid path
        invalid_db = MessageDatabase("/invalid/path/database.db")

        # Try to add a message (should fail gracefully)
        result = invalid_db.add_message(123, 456, datetime.now())
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
