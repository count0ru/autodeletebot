# Auto-Delete Telegram Bot

A Python-based Telegram bot that automatically deletes messages from your channel after 30 days. Perfect for managing content lifecycle and keeping your channel clean.

## Features

- 🤖 **Automatic Deletion**: Messages are automatically deleted after 30 days
- 📱 **Easy Setup**: Just forward messages from your channel to the bot
- ⏰ **Scheduled Cleanup**: Runs every 12 hours via cron job
- 💾 **Database Storage**: SQLite database tracks all scheduled deletions
- 📊 **Status Monitoring**: Check bot status and message counts
- 🧹 **Automatic Cleanup**: Removes old database records
- 🔔 **Deletion Notifications**: Get notified when messages are deleted or fail to delete

## How It Works

1. **Forward Messages**: Forward any message from your Telegram channel to the bot
2. **Automatic Scheduling**: The bot schedules the message for deletion after 30 days
3. **Scheduled Cleanup**: A cron job runs every 12 hours to delete expired messages
4. **Database Management**: All operations are logged and tracked in a SQLite database
5. **User Notifications**: You receive private messages about successful deletions and failures

## Requirements

- Python 3.8 or higher
- Virtual machine with internet access
- Telegram Bot Token (from @BotFather)
- Admin access to your Telegram channel

## Installation

### 1. Clone or Download the Project

```bash
git clone <your-repo-url>
cd autodeletebot
```

### 2. Run the Setup Script

```bash
chmod +x setup.sh
./setup.sh
```

The setup script will:
- Create a Python virtual environment
- Install all required dependencies
- Create a `.env` file for configuration
- Set up a cron job for automatic cleanup
- Make scripts executable

### 3. Configure the Bot

Edit the `.env` file with your bot credentials:

```bash
nano .env
```

Fill in:
- `BOT_TOKEN`: Your bot token from @BotFather
- `CHANNEL_ID`: Your channel ID (get this by forwarding a message to @userinfobot)
- `USER_ID`: Your Telegram user ID (get this by sending /start to @userinfobot)
- `USER_USERNAME`: Your Telegram username (alternative to USER_ID)

### 4. Set Up Bot Permissions

1. Add your bot to your channel as an admin
2. Give the bot permission to delete messages
3. Make sure the bot can read channel messages

## Usage

### Starting the Bot

```bash
# Activate virtual environment
source venv/bin/activate

# Start the bot
python telegram_bot.py
```

### Bot Commands

- `/start` - Start the bot and see welcome message
- `/help` - Show help information
- `/status` - Check bot status and message counts
- `/cleanup` - Manually trigger cleanup of old records

### Forwarding Messages

1. Go to your Telegram channel
2. Forward any message to the bot
3. The bot will confirm the message is scheduled for deletion
4. After 30 days, the message will be automatically deleted
5. You'll receive a private notification about the deletion status

## Deletion Notifications

The bot will send you private messages when:

✅ **Successful Deletions**: 
- Message ID and Channel ID
- Timestamp of deletion
- Confirmation of success

❌ **Failed Deletions**:
- Message ID and Channel ID
- Error message explaining why deletion failed
- Timestamp of the attempt

This helps you monitor the bot's performance and troubleshoot any issues.

## Cron Job

The bot automatically sets up a cron job that runs every 12 hours:

```bash
0 */12 * * * cd /path/to/bot && /path/to/bot/venv/bin/python /path/to/bot/cleanup_script.py >> /path/to/bot/bot.log 2>&1
```

This ensures messages are deleted promptly when they expire.

## File Structure

```
autodeletebot/
├── telegram_bot.py      # Main bot application
├── cleanup_script.py    # Standalone cleanup script for cron
├── database.py          # Database operations
├── config.py            # Configuration settings
├── requirements.txt     # Python dependencies
├── setup.sh            # Automated setup script
├── env_example.txt     # Environment variables template
├── README.md           # This file
└── bot.log             # Bot logs (created automatically)
```

## Configuration Options

You can customize the bot behavior by editing `config.py` or setting environment variables:

- `DELETE_AFTER_DAYS`: How long to wait before deleting messages (default: 30)
- `CHECK_INTERVAL_HOURS`: How often to check for expired messages (default: 12)
- `LOG_LEVEL`: Logging level (default: INFO)
- `USER_ID`: Your Telegram user ID for deletion notifications
- `USER_USERNAME`: Your Telegram username for deletion notifications

## Troubleshooting

### Common Issues

1. **Bot can't delete messages**: Ensure the bot is an admin with delete permissions
2. **Messages not being deleted**: Check the cron job is running and bot.log for errors
3. **Database errors**: Verify SQLite permissions and disk space
4. **No deletion notifications**: Check that USER_ID or USER_USERNAME is set in .env

### Logs

Check the `bot.log` file for detailed information about bot operations:

```bash
tail -f bot.log
```

### Manual Cleanup

If you need to manually trigger cleanup:

```bash
source venv/bin/activate
python cleanup_script.py
```

## Security Considerations

- Keep your bot token secure and never share it
- The bot only processes messages from your configured channel
- All operations are logged for audit purposes
- Database is stored locally on your virtual machine
- Deletion notifications are sent only to your configured user account

## Support

If you encounter issues:

1. Check the logs in `bot.log`
2. Verify your bot has proper permissions
3. Ensure your virtual machine has internet access
4. Check that the cron job is properly configured
5. Verify USER_ID or USER_USERNAME is set correctly

## License

This project is open source and available under the MIT License.

---

**Note**: This bot is designed to run on a virtual machine with continuous internet access. Make sure your VM is properly configured and secured.
