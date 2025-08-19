import logging
import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
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

class AutoDeleteBot:
    def __init__(self):
        self.db = MessageDatabase(config.DATABASE_PATH)
        self.application = None
    
    async def send_deletion_notification(self, message_id: int, chat_id: int, success: bool, error_msg: str = None):
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
                                  f"**Deleted at:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            else:
                notification_text = f"❌ **Message Deletion Failed**\n\n" \
                                  f"**Message ID:** {message_id}\n" \
                                  f"**Channel ID:** {chat_id}\n" \
                                  f"**Error:** {error_msg}\n" \
                                  f"**Time:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            # Send notification
            await self.application.bot.send_message(
                chat_id=notify_user,
                text=notification_text,
                parse_mode='Markdown'
            )
            logger.info(f"Deletion notification sent to {notify_user}")
            
        except Exception as e:
            logger.error(f"Failed to send deletion notification: {e}")
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        await update.message.reply_text(
            "🤖 Auto-Delete Bot is running!\n\n"
            "Forward any message from your channel to me, and I'll automatically delete it after 30 days.\n\n"
            "Use /help for more information."
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
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
2. The bot will automatically schedule it for deletion after 30 days
3. Messages are checked every 12 hours and deleted when their time is up

**Note:** The bot must be an admin in your channel with delete message permissions.
        """
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
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
**Deletion delay:** 30 days

Bot is running and monitoring messages.
            """
            await update.message.reply_text(status_text, parse_mode='Markdown')
        except Exception as e:
            logger.error(f"Error getting status: {e}")
            await update.message.reply_text("❌ Error getting status. Check logs for details.")
    
    async def cleanup_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /cleanup command - manual cleanup trigger"""
        try:
            deleted_count = self.db.cleanup_old_records()
            await update.message.reply_text(f"🧹 Cleanup completed! Removed {deleted_count} old records.")
        except Exception as e:
            logger.error(f"Error during manual cleanup: {e}")
            await update.message.reply_text("❌ Error during cleanup. Check logs for details.")
    
    async def handle_forwarded_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle forwarded messages from the channel"""
        try:
            message = update.message
            
            # Check if this is a forwarded message
            if not message.forward_from_chat:
                return
            
            # Check if it's from the configured channel
            if str(message.forward_from_chat.id) != config.CHANNEL_ID:
                await message.reply_text("❌ This message is not from the configured channel.")
                return
            
            # Get the original message ID and forward date
            original_message_id = message.forward_from_message_id
            forward_date = message.forward_date or datetime.datetime.now()
            
            # Add to database for future deletion
            if self.db.add_message(original_message_id, message.forward_from_chat.id, forward_date):
                await message.reply_text(
                    f"✅ Message scheduled for deletion on {forward_date + datetime.timedelta(days=30)}"
                )
                logger.info(f"Message {original_message_id} from channel {message.forward_from_chat.id} scheduled for deletion")
            else:
                await message.reply_text("❌ Failed to schedule message for deletion.")
                
        except Exception as e:
            logger.error(f"Error handling forwarded message: {e}")
            await update.message.reply_text("❌ Error processing message. Check logs for details.")
    
    async def delete_expired_messages(self):
        """Delete all expired messages from the channel"""
        try:
            messages_to_delete = self.db.get_messages_to_delete()
            deleted_count = 0
            failed_count = 0
            
            for message_id, chat_id, record_id in messages_to_delete:
                try:
                    # Delete the message from the channel
                    await self.application.bot.delete_message(chat_id=chat_id, message_id=message_id)
                    
                    # Remove the record from database
                    if self.db.delete_message_record(record_id):
                        deleted_count += 1
                        logger.info(f"Successfully deleted message {message_id} from channel {chat_id}")
                        
                        # Send success notification to user
                        await self.send_deletion_notification(message_id, chat_id, success=True)
                    else:
                        logger.error(f"Failed to remove record {record_id} from database")
                        failed_count += 1
                        
                except Exception as e:
                    error_msg = str(e)
                    logger.error(f"Error deleting message {message_id}: {error_msg}")
                    failed_count += 1
                    
                    # Send failure notification to user
                    await self.send_deletion_notification(message_id, chat_id, success=False, error_msg=error_msg)
                    # If message deletion fails, keep the record for retry
            
            if deleted_count > 0:
                logger.info(f"Cleanup completed: {deleted_count} messages deleted, {failed_count} failed")
            else:
                logger.info("No messages to delete at this time")
                
        except Exception as e:
            logger.error(f"Error during message deletion cleanup: {e}")
    
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
            self.application.add_handler(MessageHandler(filters.ALL, self.handle_forwarded_message))
            
            logger.info("Bot started successfully")
            
            # Start the bot
            self.application.run_polling(allowed_updates=Update.ALL_TYPES)
            
        except Exception as e:
            logger.error(f"Error starting bot: {e}")

if __name__ == "__main__":
    bot = AutoDeleteBot()
    bot.run()
