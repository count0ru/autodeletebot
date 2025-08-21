import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from database import MessageDatabase
from utils import setup_logging, delete_message_notify
import config

# Configure logging
logger = setup_logging()

class AutoDeleteBot:
    """Telegram bot for automatically deleting channel messages after a specified time.
    
    This bot handles message forwarding, scheduling deletions, and sending
    notifications to users about deletion status.
    """
    def __init__(self):
        self.db = MessageDatabase(config.DATABASE_PATH)
        self.application = None



    async def start_command(self, update: Update, _context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        try:
            if not update or not update.message:
                logger.warning("Start command received but no message in update")
                return

            await update.message.reply_text(
                "🤖 Auto-Delete Bot is running!\n\n"
                "Forward any message from your channel to me, and I'll automatically delete it after 60 days.\n\n"
                "Use /help for more information."
            )
        except Exception as e:
            logger.error("Error in start command: %s", e)

    async def help_command(self, update: Update, _context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = """
📚 **Auto-Delete Bot Help**

**Commands:**
/start - Start the bot
/help - Show this help message
/status - Show bot status and message count
/cleanup - Manually trigger cleanup of old records

**How to use:**
1. Forward any message from your Telegram channel to this bot
2. The bot will automatically schedule it for deletion after 60 days
3. Messages are checked every 12 hours and deleted when their time is up

**Note:** The bot must be an admin in your channel with delete message permissions.
        """
        try:
            await update.message.reply_text(help_text, parse_mode='Markdown')
        except Exception as e:
            logger.error("Error in help command: %s", e)

    async def status_command(self, update: Update, _context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        try:
            # Get message count from database
            with self.db.db_path as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM messages')
                total_messages = cursor.fetchone()[0]

                cursor.execute('SELECT COUNT(*) FROM messages WHERE delete_date <= ?',
                            (datetime.datetime.now(),))
                pending_deletion = cursor.fetchone()[0]

            status_text = f"""
📊 **Bot Status**

**Total messages tracked:** {total_messages}
**Pending deletion:** {pending_deletion}
**Next cleanup:** Every 12 hours
**Deletion delay:** 60 days

Bot is running and monitoring messages.
            """
            await update.message.reply_text(status_text, parse_mode='Markdown')
        except Exception as e:
            logger.error("Error getting status: %s", e)
            await update.message.reply_text("❌ Error getting status. Check logs for details.")

    async def cleanup_command(self, update: Update, _context: ContextTypes.DEFAULT_TYPE):
        """Handle /cleanup command - manual cleanup trigger"""
        try:
            deleted_count = self.db.cleanup_old_records()
            await update.message.reply_text(f"🧹 Cleanup completed! Removed {deleted_count} old records.")
        except Exception as e:
            logger.error("Error during manual cleanup: %s", e)
            await update.message.reply_text("❌ Error during cleanup. Check logs for details.")

    async def handle_forwarded_message(self, update: Update, _context: ContextTypes.DEFAULT_TYPE):
        """Handle forwarded messages from the channel"""
        try:
            # Check if update has a message
            if not update or not update.message:
                logger.debug("Update or message is None, skipping")
                return

            message = update.message

            # Check if this is a forwarded message
            if not message.forward_from_chat:
                logger.debug("Message is not forwarded, skipping")
                return

            # Check if it's from the configured channel
            if str(message.forward_from_chat.id) != config.CHANNEL_ID:
                logger.debug("Message not from configured channel: %s", message.forward_from_chat.id)
                return

            # Get the original message ID and forward date
            original_message_id = message.forward_from_message_id
            if not original_message_id:
                logger.warning("Forwarded message missing message ID")
                return

            forward_date = message.forward_date or datetime.datetime.now()

            # Add to database for future deletion
            if self.db.add_message(original_message_id, message.forward_from_chat.id, forward_date):
                await message.reply_text(
                    f"✅ Message scheduled for deletion on {forward_date + datetime.timedelta(minutes=config.DELETE_AFTER_MINUTES)}"
                )
                logger.info(
                    "Message %s from channel %s scheduled for deletion",
                    original_message_id, message.forward_from_chat.id
                )
            else:
                await message.reply_text("❌ Failed to schedule message for deletion.")

        except Exception as e:
            logger.error("Error handling forwarded message: %s", e)
            # Only try to reply if we have a valid message
            if update and update.message:
                try:
                    await update.message.reply_text("❌ Error processing message. Check logs for details.")
                except Exception as reply_error:
                    logger.error("Failed to send error reply: %s", reply_error)

    async def delete_expired_messages(self):
        """Delete all expired messages from the channel"""
        try:
            messages_to_delete = self.db.get_messages_to_delete()
            deleted_count = 0
            failed_count = 0

            for message_id, chat_id, record_id in messages_to_delete:
                success, _ = await delete_message_notify(
                    self.application.bot, self.db, message_id, chat_id, record_id
                )

                if success:
                    deleted_count += 1
                else:
                    failed_count += 1
                    # If message deletion fails, keep the record for retry

            if deleted_count > 0:
                logger.info("Cleanup completed: %s messages deleted, %s failed", deleted_count, failed_count)
            else:
                logger.info("No messages to delete at this time")

        except Exception as e:
            logger.error("Error during message deletion cleanup: %s", e)

    def run(self):
        """Initialize and run the bot"""
        try:
            # Create application
            self.application = Application.builder().token(config.BOT_TOKEN).build()

            # Add handlers
            self.application.add_handler(CommandHandler("start", self.start_command))
            self.application.add_handler(CommandHandler("help", self.help_command))
            self.application.add_handler(CommandHandler("status", self.status_command))
            self.application.add_handler(CommandHandler("cleanup", self.cleanup_command))
            # Only handle forwarded messages, not all messages
            self.application.add_handler(MessageHandler(filters.FORWARDED, self.handle_forwarded_message))

            logger.info("Bot started successfully")

            # Start the bot
            self.application.run_polling(allowed_updates=Update.ALL_TYPES)

        except Exception as e:
            logger.error("Error starting bot: %s", e)

if __name__ == "__main__":
    bot = AutoDeleteBot()
    bot.run()
