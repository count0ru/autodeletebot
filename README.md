# Auto-Delete Telegram Bot

A Python-based Telegram bot that automatically deletes messages from your channel after 60 days. Perfect for managing content lifecycle and keeping your channel clean.

## Features

- 🤖 **Automatic Deletion**: Messages are automatically deleted after 60 days
- 📱 **Easy Setup**: Just forward messages from your channel to the bot
- ⏰ **Scheduled Cleanup**: Runs every 720 minutes (12 hours) via cron job
- 💾 **Database Storage**: SQLite database tracks all scheduled deletions
- 📊 **Status Monitoring**: Check bot status and message counts
- 🧹 **Automatic Cleanup**: Removes old database records
- 🔔 **Deletion Notifications**: Get notified when messages are deleted or fail to delete

## How It Works

1. **Forward Messages**: Forward any message from your Telegram channel to the bot
2. **Automatic Scheduling**: The bot schedules the message for deletion after 60 days
3. **Scheduled Cleanup**: A cron job runs every 720 minutes (12 hours) to delete expired messages
4. **Database Management**: All operations are logged and tracked in a SQLite database
5. **User Notifications**: You receive private messages about successful deletions and failures

## Requirements

- Python 3.8 or higher
- Virtual machine with internet access
- Telegram Bot Token (from @BotFather)
- Admin access to your Telegram channel

## Installation

### **Option 1: Docker Compose + Systemd (Recommended for Production)**

#### 1. Clone the Project
```bash
git clone <your-repo-url>
cd autodeletebot
```

#### 2. Run the Installation Script
```bash
# Install to default location (/opt/autodeletebot) with production config
sudo deployment/install.sh

# Install to custom location
sudo deployment/install.sh --dest /home/user/bot

# Install with development configuration
sudo deployment/install.sh --env dev

# Install to custom location with development config
sudo deployment/install.sh --dest /home/user/bot --env dev

# Show help
deployment/install.sh --help
```

#### 3. Configure the Bot
Edit the environment file with your bot credentials:
```bash
sudo nano /opt/autodeletebot/deployment/docker-compose/.env
```

Fill in:
- `BOT_TOKEN`: Your bot token from @BotFather
- `CHANNEL_ID`: Your channel ID (get this by forwarding a message to @userinfobot)
- `USER_ID`: Your Telegram user ID (get this by sending /start to @userinfobot)
- `USER_USERNAME`: Your Telegram username (alternative to USER_ID)

#### 4. Start the Service
```bash
# Start the bot
sudo /opt/autodeletebot/deployment/manage.sh start

# Check status
sudo /opt/autodeletebot/deployment/manage.sh status

# View logs
sudo /opt/autodeletebot/deployment/manage.sh logs-follow
```

#### 5. Management Commands
```bash
# Service control
sudo /opt/autodeletebot/deployment/manage.sh start     # Start service
sudo /opt/autodeletebot/deployment/manage.sh stop      # Stop service
sudo /opt/autodeletebot/deployment/manage.sh restart   # Restart service

# Monitoring
sudo /opt/autodeletebot/deployment/manage.sh status   # Show status
sudo /opt/autodeletebot/deployment/manage.sh logs     # Show logs
sudo /opt/autodeletebot/deployment/manage.sh logs-follow # Follow logs

# Maintenance
sudo /opt/autodeletebot/deployment/manage.sh backup   # Backup data
sudo /opt/autodeletebot/deployment/manage.sh cleanup  # Run cleanup manually
sudo /opt/autodeletebot/deployment/manage.sh update   # Update bot image
```

### **Option 2: Traditional Setup (Development)**

#### 1. Clone or Download the Project
```bash
git clone <your-repo-url>
cd autodeletebot
```

#### 2. Run the Setup Script
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

#### 3. Configure the Bot
Edit the `.env` file with your bot credentials:
```bash
nano .env
```

Fill in:
- `BOT_TOKEN`: Your bot token from @BotFather
- `CHANNEL_ID`: Your channel ID (get this by forwarding a message to @userinfobot)
- `USER_ID`: Your Telegram user ID (get this by sending /start to @userinfobot)
- `USER_USERNAME`: Your Telegram username (alternative to USER_ID)

#### 4. Set Up Bot Permissions

1. Add your bot to your channel as an admin
2. Give the bot permission to delete messages
3. Make sure the bot can read channel messages

## 🐳 **Docker & Deployment**

### **Docker Compose Configurations**

The project includes multiple Docker Compose configurations for different environments:

- **`docker-compose.yml`** - Main configuration (auto-selected based on environment)
- **`docker-compose.dev.yml`** - Development setup with debug logging and source mounting
- **`docker-compose.prod.yml`** - Production setup with security and resource limits

### **Systemd Services**

Automated systemd service installation with:

- **`autodeletebot.service`** - Main bot service
- **`autodeletebot-cleanup.service`** - Cleanup script service
- **`autodeletebot-cleanup.timer`** - Automated cleanup scheduling (every 12 hours)

### **Installation & Management**

- **`install.sh`** - Automated installation script with environment selection
- **`manage.sh`** - Service management and monitoring script
- **Automatic user/group creation** with proper permissions
- **Production-ready directory structure** at `/opt/autodeletebot`

## Development with Makefile

The project includes a comprehensive Makefile for easy development and deployment:

### Available Make Targets

```bash
# Show all available targets
make help

# Install virtual environment and main requirements
make deps

# Install virtual environment and all requirements (including tests)
make deps-tests

# Run all tests
make tests

# Run tests with coverage
make tests-cov

# Run specific test file
make test-file FILE=tests/test_database.py

# Build Docker container
make build

# Run pylint code analysis
make lint

# Run flake8 linting
make lint-flake8

# Format code with black
make format

# Run all checks (lint + tests)
make check

# Install development tools
make dev-tools

# Quick setup for development
make setup

# Clean up generated files and virtual environment
make clean
```

### Quick Development Setup

```bash
# Set up complete development environment
make setup

# Run tests
make tests

# Check code quality
make lint

# Format code
make format

# Run all checks
make check
```

### Docker Build

```bash
# Build Docker container
make build

# Run the container
docker run -d --name autodeletebot autodeletebot:latest
```

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
├── utils.py             # Shared utility functions
├── requirements.txt     # Python dependencies
├── requirements-test.txt # Testing dependencies
├── setup.sh            # Automated setup script
├── env_example.txt     # Environment variables template
├── Makefile            # Development and build automation
├── Dockerfile          # Docker container configuration
├── .dockerignore       # Docker build exclusions
├── .pylintrc          # Pylint configuration
├── tests/              # Test suite
│   ├── test_database.py
│   ├── test_utils.py
│   ├── test_config.py
│   └── test_integration.py
├── README.md           # This file
└── bot.log             # Bot logs (created automatically)
```

## Testing

The project includes a comprehensive test suite with 34 test cases covering:

- **Unit Tests**: Individual component testing
- **Integration Tests**: Component interaction testing  
- **Configuration Tests**: Environment variable validation
- **Database Tests**: SQLite operations testing

### Running Tests

```bash
# Run all tests
make tests

# Run tests with coverage
make tests-cov

# Run specific test file
make test-file FILE=tests/test_database.py

# Run tests directly with pytest
venv/bin/python3 -m pytest tests/ -v
```

### Test Coverage

Tests cover:
- Database operations (CRUD, cleanup, error handling)
- Configuration management (environment variables, defaults)
- Utility functions (logging, notifications, message deletion)
- Integration scenarios (message lifecycle, error handling)
- Async operations (Telegram bot API simulation)

## Configuration Options

You can customize the bot behavior by editing `config.py` or setting environment variables:

- `DELETE_AFTER_DAYS`: How long to wait before deleting messages (default: 60)
- `CHECK_INTERVAL_MINUTES`: How often to check for expired messages in minutes (default: 720)
- `LOG_LEVEL`: Logging level (default: INFO)
- `USER_ID`: Your Telegram user ID for deletion notifications
- `USER_USERNAME`: Your Telegram username for deletion notifications

## CI/CD Pipeline

The project includes a comprehensive CI/CD pipeline using GitHub Actions:

### **🚀 Automated Workflows**

- **Quality & Testing**: Runs on every push/PR
- **Docker Build**: Automated container builds
- **Security Scan**: Vulnerability detection
- **Deployment**: Multi-environment deployment
- **Dependency Updates**: Weekly security updates via Dependabot

### **📊 Pipeline Status**

- **Quality Gates**: Pylint ≥9.0, All tests passing
- **Build Status**: Docker images built and tested
- **Security**: Bandit + Safety vulnerability scanning
- **Deployment**: Automatic staging/production deployment

### **🔧 Quick Setup**

1. **Enable Actions**: Go to Actions tab in your repository
2. **Configure Secrets**: Add deployment tokens if needed
3. **Enable Dependabot**: Go to Security → Dependabot

📖 **Full Setup Guide**: See [CI_CD_SETUP.md](CI_CD_SETUP.md) for detailed instructions.

## Code Quality

The project maintains high code quality standards with automated tools:

### Linting and Code Analysis

```bash
# Run pylint (10.00/10 score)
make lint

# Run flake8 for additional style checks
make lint-flake8

# Format code with black
make format

# Run all quality checks
make check
```

### Current Quality Metrics

- **Pylint Score**: 10.00/10 (Perfect)
- **Test Coverage**: 34/34 tests passing (100%)
- **Code Style**: PEP 8 compliant with black formatting
- **Import Organization**: Proper import ordering and structure

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
# Test container registry push
