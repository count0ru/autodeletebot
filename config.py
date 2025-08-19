import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Bot configuration
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHANNEL_ID = os.getenv('CHANNEL_ID')  # Your channel ID where messages will be deleted

# User notification configuration
USER_ID = os.getenv('USER_ID')  # Your Telegram user ID for deletion notifications
USER_USERNAME = os.getenv('USER_USERNAME')  # Your Telegram username (alternative to USER_ID)

# Database configuration
DATABASE_PATH = 'messages.db'

# Message deletion settings
DELETE_AFTER_DAYS = 30
CHECK_INTERVAL_HOURS = 12

# Logging configuration
LOG_LEVEL = 'INFO'
LOG_FILE = 'bot.log'
