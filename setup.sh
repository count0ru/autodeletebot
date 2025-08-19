#!/bin/bash

# Auto-Delete Telegram Bot Setup Script
# Run this script on your virtual machine to set up the bot

echo "🤖 Setting up Auto-Delete Telegram Bot..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✅ Python $python_version detected"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "⚙️ Creating .env file..."
    cp env_example.txt .env
    echo "📝 Please edit .env file with your bot token and channel ID"
    echo "   - Get bot token from @BotFather"
    echo "   - Get channel ID by forwarding a message to @userinfobot"
else
    echo "✅ .env file already exists"
fi

# Make scripts executable
echo "🔧 Making scripts executable..."
chmod +x cleanup_script.py

# Create log file
echo "📝 Creating log file..."
touch bot.log

# Set up cron job
echo "⏰ Setting up cron job for cleanup (every 12 hours)..."
cron_job="0 */12 * * * cd $(pwd) && $(pwd)/venv/bin/python $(pwd)/cleanup_script.py >> $(pwd)/bot.log 2>&1"

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "cleanup_script.py"; then
    echo "✅ Cron job already exists"
else
    (crontab -l 2>/dev/null; echo "$cron_job") | crontab -
    echo "✅ Cron job added"
fi

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your bot token and channel ID"
echo "2. Make your bot an admin in your channel with delete permissions"
echo "3. Start the bot: python3 telegram_bot.py"
echo "4. Forward messages from your channel to the bot"
echo ""
echo "The cleanup script will run automatically every 12 hours via cron"
echo "Check bot.log for any errors or issues"
