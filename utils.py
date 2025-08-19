"""Shared utilities for the Auto-Delete Telegram Bot."""

import logging
from datetime import datetime
import config


def setup_logging():
    """Configure logging for the application."""
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(config.LOG_FILE),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


async def send_deletion_notification(bot, message_id: int, chat_id: int, success: bool, error_msg: str = None):
    """Send notification to user about message deletion status."""
    logger = logging.getLogger(__name__)

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
        logger.info("Deletion notification sent to %s", notify_user)

    except Exception as e:
        logger.error("Failed to send deletion notification: %s", e)


async def delete_message_notify(bot, db, message_id: int, chat_id: int, record_id: int):
    """Handle message deletion and send appropriate notifications."""
    logger = logging.getLogger(__name__)

    try:
        # Delete the message from the channel
        await bot.delete_message(chat_id=chat_id, message_id=message_id)

        # Remove the record from database
        if db.delete_message_record(record_id):
            logger.info("Successfully deleted message %s from channel %s", message_id, chat_id)

            # Send success notification to user
            await send_deletion_notification(bot, message_id, chat_id, success=True)
            return True, None

        error_msg = "Failed to remove record from database"
        logger.error("Failed to remove record %s from database", record_id)
        return False, error_msg

    except Exception as e:
        error_msg = str(e)
        logger.error("Error deleting message %s: %s", message_id, error_msg)

        # Send failure notification to user
        await send_deletion_notification(bot, message_id, chat_id, success=False, error_msg=error_msg)
        return False, error_msg
