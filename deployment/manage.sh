#!/bin/bash

# Auto-Delete Bot Management Script
# This script provides easy management of the bot services

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
INSTALL_DIR="/opt/autodeletebot"
COMPOSE_FILE="$INSTALL_DIR/deployment/docker-compose/docker-compose.yml"

# Function to show usage
show_usage() {
    echo -e "${BLUE}🚀 Auto-Delete Bot Management Script${NC}"
    echo "====================================="
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start       - Start the bot service"
    echo "  stop        - Stop the bot service"
    echo "  restart     - Restart the bot service"
    echo "  status      - Show service status"
    echo "  logs        - Show service logs"
    echo "  logs-follow - Follow service logs"
    echo "  cleanup     - Run cleanup manually"
    echo "  update      - Update bot image and restart"
    echo "  backup      - Backup bot data"
    echo "  restore     - Restore bot data from backup"
    echo "  help        - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start"
    echo "  $0 status"
    echo "  $0 logs-follow"
}

# Function to check if service is running
check_service() {
    if systemctl is-active --quiet autodeletebot; then
        return 0
    else
        return 1
    fi
}

# Function to start service
start_service() {
    echo -e "${BLUE}🚀 Starting Auto-Delete Bot...${NC}"
    systemctl start autodeletebot
    if check_service; then
        echo -e "${GREEN}✅ Service started successfully${NC}"
    else
        echo -e "${RED}❌ Failed to start service${NC}"
        exit 1
    fi
}

# Function to stop service
stop_service() {
    echo -e "${BLUE}🛑 Stopping Auto-Delete Bot...${NC}"
    systemctl stop autodeletebot
    echo -e "${GREEN}✅ Service stopped successfully${NC}"
}

# Function to restart service
restart_service() {
    echo -e "${BLUE}🔄 Restarting Auto-Delete Bot...${NC}"
    systemctl restart autodeletebot
    if check_service; then
        echo -e "${GREEN}✅ Service restarted successfully${NC}"
    else
        echo -e "${RED}❌ Failed to restart service${NC}"
        exit 1
    fi
}

# Function to show status
show_status() {
    echo -e "${BLUE}📊 Auto-Delete Bot Status${NC}"
    echo "========================="
    echo ""
    systemctl status autodeletebot --no-pager -l
    echo ""
    echo -e "${BLUE}🐳 Docker Container Status${NC}"
    echo "=========================="
    docker ps --filter "name=autodeletebot" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    echo ""
    echo -e "${BLUE}⏰ Timer Status${NC}"
    echo "==============="
    systemctl status autodeletebot-cleanup.timer --no-pager -l
}

# Function to show logs
show_logs() {
    echo -e "${BLUE}📋 Auto-Delete Bot Logs${NC}"
    echo "======================="
    journalctl -u autodeletebot -n 50 --no-pager
}

# Function to follow logs
follow_logs() {
    echo -e "${BLUE}📋 Following Auto-Delete Bot Logs${NC}"
    echo "================================="
    echo "Press Ctrl+C to stop following logs"
    echo ""
    journalctl -u autodeletebot -f
}

# Function to run cleanup manually
run_cleanup() {
    echo -e "${BLUE}🧹 Running cleanup manually...${NC}"
    if check_service; then
        docker exec autodeletebot python3 cleanup_script.py
        echo -e "${GREEN}✅ Cleanup completed${NC}"
    else
        echo -e "${RED}❌ Service is not running. Start it first with: $0 start${NC}"
        exit 1
    fi
}

# Function to update bot
update_bot() {
    echo -e "${BLUE}🔄 Updating Auto-Delete Bot...${NC}"
    cd "$INSTALL_DIR/deployment/docker-compose"
    
    # Pull latest image
    docker-compose pull
    
    # Restart service
    restart_service
    
    echo -e "${GREEN}✅ Bot updated and restarted successfully${NC}"
}

# Function to backup data
backup_data() {
    echo -e "${BLUE}💾 Creating backup...${NC}"
    BACKUP_DIR="$INSTALL_DIR/backups"
    BACKUP_FILE="autodeletebot-backup-$(date +%Y%m%d-%H%M%S).tar.gz"
    
    mkdir -p "$BACKUP_DIR"
    tar -czf "$BACKUP_DIR/$BACKUP_FILE" -C "$INSTALL_DIR" data logs config
    
    echo -e "${GREEN}✅ Backup created: $BACKUP_DIR/$BACKUP_FILE${NC}"
}

# Function to restore data
restore_data() {
    if [ -z "$1" ]; then
        echo -e "${RED}❌ Please specify backup file to restore${NC}"
        echo "Usage: $0 restore <backup-file>"
        exit 1
    fi
    
    BACKUP_FILE="$1"
    if [ ! -f "$BACKUP_FILE" ]; then
        echo -e "${RED}❌ Backup file not found: $BACKUP_FILE${NC}"
        exit 1
    fi
    
    echo -e "${BLUE}🔄 Restoring from backup: $BACKUP_FILE${NC}"
    
    # Stop service
    stop_service
    
    # Restore data
    tar -xzf "$BACKUP_FILE" -C "$INSTALL_DIR"
    
    # Fix permissions
    chown -R autodeletebot:autodeletebot "$INSTALL_DIR"/{data,logs,config}
    
    # Start service
    start_service
    
    echo -e "${GREEN}✅ Data restored successfully${NC}"
}

# Main script logic
case "${1:-help}" in
    start)
        start_service
        ;;
    stop)
        stop_service
        ;;
    restart)
        restart_service
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    logs-follow)
        follow_logs
        ;;
    cleanup)
        run_cleanup
        ;;
    update)
        update_bot
        ;;
    backup)
        backup_data
        ;;
    restore)
        restore_data "$2"
        ;;
    help|--help|-h)
        show_usage
        ;;
    *)
        echo -e "${RED}❌ Unknown command: $1${NC}"
        echo ""
        show_usage
        exit 1
        ;;
esac
