"""Integration tests for the Auto-Delete Telegram Bot."""

import unittest
import tempfile
import os
import asyncio
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock, AsyncMock

# Add parent directory to path for imports
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import MessageDatabase
from utils import delete_message_notify
import config


class TestIntegration(unittest.TestCase):
    """Integration test cases."""

    def setUp(self):
        """Set up test environment."""
        # Create temporary database file
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db = MessageDatabase(self.temp_db.name)

    def tearDown(self):
        """Clean up test environment."""
        # Remove temporary database file
        os.unlink(self.temp_db.name)

    def test_message_lifecycle(self):
        """Test complete message lifecycle from creation to deletion."""
        # 1. Add message to database
        message_id = 123
        chat_id = 456
        forward_date = datetime.now() - timedelta(days=31)  # Past date

        result = self.db.add_message(message_id, chat_id, forward_date)
        self.assertTrue(result)

        # 2. Verify message is in database
        messages = self.db.get_messages_to_delete()
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0][0], message_id)
        self.assertEqual(messages[0][1], chat_id)

        # 3. Simulate message deletion
        record_id = messages[0][2]
        result = self.db.delete_message_record(record_id)
        self.assertTrue(result)

        # 4. Verify message is removed from database
        messages_after = self.db.get_messages_to_delete()
        self.assertEqual(len(messages_after), 0)

    def test_bot_database_integration(self):
        """Test integration between bot operations and database."""
        # Mock bot
        mock_bot = AsyncMock()

        # Add message to database
        message_id = 789
        chat_id = 101
        forward_date = datetime.now() - timedelta(days=31)

        self.db.add_message(message_id, chat_id, forward_date)

        # Get message for deletion
        messages = self.db.get_messages_to_delete()
        self.assertEqual(len(messages), 1)
        record_id = messages[0][2]

        # Test integrated deletion using asyncio.run
        import asyncio
        success, error_msg = asyncio.run(delete_message_notify(mock_bot, self.db, message_id, chat_id, record_id))

        # Verify success
        self.assertTrue(success)
        self.assertIsNone(error_msg)

        # Verify bot.delete_message was called
        mock_bot.delete_message.assert_called_once_with(chat_id=chat_id, message_id=message_id)

        # Verify message record was removed from database
        messages_after = self.db.get_messages_to_delete()
        self.assertEqual(len(messages_after), 0)

    def test_multiple_messages_cleanup(self):
        """Test cleanup of multiple messages."""
        # Add multiple messages with different dates
        messages_data = [
            (111, 222, datetime.now() - timedelta(days=31)),  # Expired
            (333, 444, datetime.now() - timedelta(days=15)),  # Not expired
            (555, 666, datetime.now() - timedelta(days=32)),  # Expired
        ]

        for message_id, chat_id, forward_date in messages_data:
            self.db.add_message(message_id, chat_id, forward_date)

        # Get expired messages
        expired_messages = self.db.get_messages_to_delete()
        self.assertEqual(len(expired_messages), 2)  # Only expired ones

        # Verify correct messages are expired
        expired_ids = [msg[0] for msg in expired_messages]
        self.assertIn(111, expired_ids)
        self.assertIn(555, expired_ids)
        self.assertNotIn(333, expired_ids)

    def test_database_persistence(self):
        """Test that database persists data between instances."""
        # Add message
        message_id = 999
        chat_id = 888
        forward_date = datetime.now() - timedelta(days=31)

        self.db.add_message(message_id, chat_id, forward_date)

        # Create new database instance (simulating restart)
        new_db = MessageDatabase(self.temp_db.name)

        # Verify message still exists
        messages = new_db.get_messages_to_delete()
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0][0], message_id)

    def test_error_handling_integration(self):
        """Test error handling across components."""
        # Test with invalid database path
        invalid_db = MessageDatabase("/invalid/path/database.db")

        # Try to add message (should fail gracefully)
        result = invalid_db.add_message(123, 456, datetime.now())
        self.assertFalse(result)

        # Try to get messages (should return empty list)
        messages = invalid_db.get_messages_to_delete()
        self.assertEqual(len(messages), 0)

    def test_configuration_integration(self):
        """Test configuration integration with components."""
        # Mock configuration
        with patch('config.DATABASE_PATH', self.temp_db.name):
            # Create database with mocked config
            test_db = MessageDatabase(self.temp_db.name)

            # Test that it works
            result = test_db.add_message(123, 456, datetime.now())
            self.assertTrue(result)

    def test_logging_integration(self):
        """Test logging integration across components."""
        # Test that setup_logging returns a logger
        from utils import setup_logging
        logger = setup_logging()

        # Verify logger is properly configured
        self.assertIsNotNone(logger)
        self.assertEqual(logger.level, 20)  # INFO level

        # Test that logger can log messages (pytest will capture them)
        logger.info("Test message")
        logger.warning("Test warning")
        logger.error("Test error")

        # Verify logger has handlers
        self.assertTrue(len(logger.handlers) > 0)


if __name__ == '__main__':
    unittest.main()
