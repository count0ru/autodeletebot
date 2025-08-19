"""Unit tests for configuration validation."""

import os
import sys
import unittest
import config
import tempfile
from unittest.mock import patch, mock_open

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))



class TestConfig(unittest.TestCase):
    """Test cases for configuration."""

    def setUp(self):
        """Set up test environment."""
        # Backup original environment variables
        self.original_env = os.environ.copy()

    def tearDown(self):
        """Clean up test environment."""
        # Restore original environment variables
        os.environ.clear()
        os.environ.update(self.original_env)

    def test_bot_token_required(self):
        """Test that bot token is required."""
        # Clear environment
        if 'BOT_TOKEN' in os.environ:
            del os.environ['BOT_TOKEN']

        # Reload config
        import importlib
        importlib.reload(config)

        # Bot token should be None
        self.assertIsNone(config.BOT_TOKEN)

    def test_channel_id_required(self):
        """Test that channel ID is required."""
        # Clear environment
        if 'CHANNEL_ID' in os.environ:
            del os.environ['CHANNEL_ID']

        # Reload config
        import importlib
        importlib.reload(config)

        # Channel ID should be None
        self.assertIsNone(config.CHANNEL_ID)

    def test_user_id_configuration(self):
        """Test user ID configuration."""
        # Set user ID
        os.environ['USER_ID'] = '12345'

        # Reload config
        import importlib
        importlib.reload(config)

        # User ID should be set
        self.assertEqual(config.USER_ID, '12345')

    def test_username_configuration(self):
        """Test username configuration."""
        # Set username
        os.environ['USER_USERNAME'] = 'testuser'

        # Reload config
        import importlib
        importlib.reload(config)

        # Username should be set
        self.assertEqual(config.USER_USERNAME, 'testuser')

    def test_default_values(self):
        """Test default configuration values."""
        # Clear environment
        os.environ.clear()

        # Reload config
        import importlib
        importlib.reload(config)

        # Check default values
        self.assertEqual(config.DELETE_AFTER_MINUTES, 86400)
        self.assertEqual(config.CHECK_INTERVAL_MINUTES, 720)
        self.assertEqual(config.LOG_LEVEL, 'INFO')
        self.assertEqual(config.DATABASE_PATH, 'messages.db')
        self.assertEqual(config.LOG_FILE, 'bot.log')

    def test_custom_delete_minutes(self):
        """Test custom delete minutes configuration."""
        # Set custom delete minutes
        os.environ['DELETE_AFTER_MINUTES'] = '129600'  # 90 days in minutes

        # Reload config
        import importlib
        importlib.reload(config)

        # Custom value should be used
        self.assertEqual(config.DELETE_AFTER_MINUTES, 129600)

    def test_custom_check_interval(self):
        """Test custom check interval configuration."""
        # Set custom check interval
        os.environ['CHECK_INTERVAL_MINUTES'] = '1440'  # 24 hours = 1440 minutes

        # Reload config
        import importlib
        importlib.reload(config)

        # Custom value should be used
        self.assertEqual(config.CHECK_INTERVAL_MINUTES, 1440)

    def test_custom_log_level(self):
        """Test custom log level configuration."""
        # Set custom log level
        os.environ['LOG_LEVEL'] = 'DEBUG'

        # Reload config
        import importlib
        importlib.reload(config)

        # Custom value should be used
        self.assertEqual(config.LOG_LEVEL, 'DEBUG')

    def test_environment_variable_priority(self):
        """Test that environment variables take priority over defaults."""
        # Set environment variables
        os.environ['BOT_TOKEN'] = 'test_token'
        os.environ['CHANNEL_ID'] = 'test_channel'
        os.environ['USER_ID'] = 'test_user'

        # Reload config
        import importlib
        importlib.reload(config)

        # Environment values should be used
        self.assertEqual(config.BOT_TOKEN, 'test_token')
        self.assertEqual(config.CHANNEL_ID, 'test_channel')
        self.assertEqual(config.USER_ID, 'test_user')

    def test_missing_dotenv_file(self):
        """Test behavior when .env file is missing."""
        # Clear environment
        os.environ.clear()

        # Reload config (should not fail)
        try:
            import importlib
            importlib.reload(config)
        except Exception as e:
            self.fail(f"Config loading failed: {e}")


if __name__ == '__main__':
    unittest.main()
