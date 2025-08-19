#!/usr/bin/env python3
"""
Standalone cleanup script for the Auto-Delete Telegram Bot.
This script can be run via cron every 12 hours to delete expired messages.
"""

import asyncio
import sys
import os

from telegram import Bot

import config
from database import MessageDatabase
from utils import setup_logging, delete_message_notify

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logger = setup_logging()

async def cleanup_expired_messages():
    """Clean up expired messages from the channel"""
    try:
        # Initialize bot and database
        bot = Bot(token=config.BOT_TOKEN)
        db = MessageDatabase(config.DATABASE_PATH)

        # Get messages that need to be deleted
        messages_to_delete = db.get_messages_to_delete()

        if not messages_to_delete:
            logger.info("No messages to delete at this time")
            return

        deleted_count = 0
        failed_count = 0

        logger.info("Found %s messages to delete", len(messages_to_delete))

        for message_id, chat_id, record_id in messages_to_delete:
            success, _ = await delete_message_notify(
                bot, db, message_id, chat_id, record_id
            )

            if success:
                deleted_count += 1
            else:
                failed_count += 1
                # If message deletion fails, keep the record for retry

        # Clean up old database records
        cleanup_count = db.cleanup_old_records()

        logger.info(
            "Cleanup completed: %s messages deleted, %s failed, %s old records cleaned",
            deleted_count, failed_count, cleanup_count
        )

    except Exception as e:
        logger.error("Error during cleanup: %s", e)
        sys.exit(1)

def main():
    """Main function to run the cleanup"""
    logger.info("Starting cleanup script")

    try:
        # Run the async cleanup function
        asyncio.run(cleanup_expired_messages())
        logger.info("Cleanup script completed successfully")
    except Exception as e:
        logger.error("Cleanup script failed: %s", e)
        sys.exit(1)

if __name__ == "__main__":
    main()
