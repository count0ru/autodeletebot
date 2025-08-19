"""Unit tests for utility functions."""

import unittest
import tempfile
import os
from unittest.mock import patch, MagicMock, AsyncMock

# Add parent directory to path for imports
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import setup_logging, send_deletion_notification, delete_message_notify


class TestUtils(unittest.TestCase):
    """Test cases for utility functions."""

    def setUp(self):
        """Set up test environment."""
        # Create temporary log file
        self.temp_log = tempfile.NamedTemporaryFile(delete=False, suffix='.log')
        self.temp_log.close()

        # Mock config values
        self.config_patcher = patch('utils.config')
        self.mock_config = self.config_patcher.start()
        self.mock_config.LOG_LEVEL = 'INFO'
        self.mock_config.LOG_FILE = self.temp_log.name
        self.mock_config.USER_ID = '12345'
        self.mock_config.USER_USERNAME = None

    def tearDown(self):
        """Clean up test environment."""
        # Remove temporary log file
        os.unlink(self.temp_log.name)
        self.config_patcher.stop()

    def test_setup_logging(self):
        """Test logging setup."""
        logger = setup_logging()
        self.assertIsNotNone(logger)
        self.assertEqual(logger.level, 20)  # INFO level

    def test_setup_logging_with_custom_level(self):
        """Test logging setup with custom level."""
        self.mock_config.LOG_LEVEL = 'DEBUG'
        logger = setup_logging()
        self.assertEqual(logger.level, 10)  # DEBUG level

    @patch('utils.config.USER_ID', '12345')
    @patch('utils.config.USER_USERNAME', None)
    def test_send_deletion_notification_success(self):
        """Test sending success notification."""
        # Mock bot
        mock_bot = AsyncMock()

        # Test success notification using asyncio.run
        import asyncio
        asyncio.run(send_deletion_notification(mock_bot, 123, 456, True))

        # Verify bot.send_message was called
        mock_bot.send_message.assert_called_once()
        call_args = mock_bot.send_message.call_args
        self.assertEqual(call_args[1]['chat_id'], '12345')
        self.assertIn('✅ **Message Deleted Successfully**', call_args[1]['text'])

    @patch('utils.config.USER_ID', None)
    @patch('utils.config.USER_USERNAME', 'testuser')
    def test_send_deletion_notification_with_username(self):
        """Test sending notification using username."""
        # Mock bot
        mock_bot = AsyncMock()

        # Test failure notification using asyncio.run
        import asyncio
        asyncio.run(send_deletion_notification(mock_bot, 123, 456, False, "Test error"))

        # Verify bot.send_message was called with username
        mock_bot.send_message.assert_called_once()
        call_args = mock_bot.send_message.call_args
        self.assertEqual(call_args[1]['chat_id'], '@testuser')
        self.assertIn('❌ **Message Deletion Failed**', call_args[1]['text'])

    @patch('utils.config.USER_ID', None)
    @patch('utils.config.USER_USERNAME', None)
    def test_send_deletion_notification_no_user(self):
        """Test notification when no user is configured."""
        # Mock bot
        mock_bot = AsyncMock()

        # Test notification (should not send anything) using asyncio.run
        import asyncio
        asyncio.run(send_deletion_notification(mock_bot, 123, 456, True))

        # Verify bot.send_message was not called
        mock_bot.send_message.assert_not_called()

    def test_delete_message_notify_success(self):
        """Test successful message deletion with notification."""
        # Mock bot and database
        mock_bot = AsyncMock()
        mock_db = MagicMock()
        mock_db.delete_message_record.return_value = True

        # Test successful deletion using asyncio.run
        import asyncio
        success, error_msg = asyncio.run(delete_message_notify(mock_bot, mock_db, 123, 456, 789))

        # Verify results
        self.assertTrue(success)
        self.assertIsNone(error_msg)

        # Verify bot.delete_message was called
        mock_bot.delete_message.assert_called_once_with(chat_id=456, message_id=123)

        # Verify database.delete_message_record was called
        mock_db.delete_message_record.assert_called_once_with(789)

    def test_delete_message_notify_db_failure(self):
        """Test message deletion when database operation fails."""
        # Mock bot and database
        mock_bot = AsyncMock()
        mock_db = MagicMock()
        mock_db.delete_message_record.return_value = False

        # Test database failure using asyncio.run
        import asyncio
        success, error_msg = asyncio.run(delete_message_notify(mock_bot, mock_db, 123, 456, 789))

        # Verify results
        self.assertFalse(success)
        self.assertEqual(error_msg, "Failed to remove record from database")

        # Verify bot.delete_message was still called
        mock_bot.delete_message.assert_called_once_with(chat_id=456, message_id=123)

    def test_delete_message_notify_bot_failure(self):
        """Test message deletion when bot operation fails."""
        # Mock bot and database
        mock_bot = AsyncMock()
        mock_bot.delete_message.side_effect = Exception("Bot error")
        mock_db = MagicMock()

        # Test bot failure using asyncio.run
        import asyncio
        success, error_msg = asyncio.run(delete_message_notify(mock_bot, mock_db, 123, 456, 789))

        # Verify results
        self.assertFalse(success)
        self.assertEqual(error_msg, "Bot error")

        # Verify database.delete_message_record was not called
        mock_db.delete_message_record.assert_not_called()

    def test_send_deletion_notification_exception_handling(self):
        """Test exception handling in notification function."""
        # Mock bot that raises exception
        mock_bot = AsyncMock()
        mock_bot.send_message.side_effect = Exception("Bot error")

        # This should not raise an exception
        try:
            import asyncio
            asyncio.run(send_deletion_notification(mock_bot, 123, 456, True))
        except Exception as e:
            self.fail(f"send_deletion_notification raised an exception: {e}")


if __name__ == '__main__':
    unittest.main()
