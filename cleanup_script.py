#!/usr/bin/env python3
"""
Standalone cleanup script for the Auto-Delete Telegram Bot.
This script can be run via cron every 12 hours to delete expired messages.
"""

import asyncio
import logging
import sys
import os
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import MessageDatabase
import config

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def send_deletion_notification(bot, message_id: int, chat_id: int, success: bool, error_msg: str = None):
    """Send notification to user about message deletion status"""
    try:
        # Determine who to notify
        notify_user = None
        if config.USER_ID:
            notify_user = config.USER_ID
        elif config.USER_USERNAME:
            notify_user = f"@{config.USER_USERNAME}"
        
        if not notify_user:
            logger.warning("No user configured for deletion notifications")
            return
        
        # Create notification message
        if success:
            notification_text = f"✅ **Message Deleted Successfully**\n\n" \
                              f"**Message ID:** {message_id}\n" \
                              f"**Channel ID:** {chat_id}\n" \
                              f"**Deleted at:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        else:
            notification_text = f"❌ **Message Deletion Failed**\n\n" \
                              f"**Message ID:** {message_id}\n" \
                              f"**Channel ID:** {chat_id}\n" \
                              f"**Error:** {error_msg}\n" \
                              f"**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        # Send notification
        await bot.send_message(
            chat_id=notify_user,
            text=notification_text,
            parse_mode='Markdown'
        )
        logger.info(f"Deletion notification sent to {notify_user}")
        
    except Exception as e:
        logger.error(f"Failed to send deletion notification: {e}")

async def cleanup_expired_messages():
    """Clean up expired messages from the channel"""
    try:
        from telegram import Bot
        
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
        
        logger.info(f"Found {len(messages_to_delete)} messages to delete")
        
        for message_id, chat_id, record_id in messages_to_delete:
            try:
                # Delete the message from the channel
                await bot.delete_message(chat_id=chat_id, message_id=message_id)
                
                # Remove the record from database
                if db.delete_message_record(record_id):
                    deleted_count += 1
                    logger.info(f"Successfully deleted message {message_id} from channel {chat_id}")
                    
                    # Send success notification to user
                    await send_deletion_notification(bot, message_id, chat_id, success=True)
                else:
                    logger.error(f"Failed to remove record {record_id} from database")
                    failed_count += 1
                    
            except Exception as e:
                error_msg = str(e)
                logger.error(f"Error deleting message {message_id}: {error_msg}")
                failed_count += 1
                
                # Send failure notification to user
                await send_deletion_notification(bot, message_id, chat_id, success=False, error_msg=error_msg)
                # If message deletion fails, keep the record for retry
        
        # Clean up old database records
        cleanup_count = db.cleanup_old_records()
        
        logger.info(f"Cleanup completed: {deleted_count} messages deleted, {failed_count} failed, {cleanup_count} old records cleaned")
        
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")
        sys.exit(1)

def main():
    """Main function to run the cleanup"""
    logger.info("Starting cleanup script")
    
    try:
        # Run the async cleanup function
        asyncio.run(cleanup_expired_messages())
        logger.info("Cleanup script completed successfully")
    except Exception as e:
        logger.error(f"Cleanup script failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
