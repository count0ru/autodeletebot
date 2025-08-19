#!/bin/bash

# Auto-Delete Bot Installation Script
# This script sets up the systemd services and Docker Compose environment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default configuration
DEFAULT_INSTALL_DIR="/opt/autodeletebot"
DEFAULT_ENV="prod"
INSTALL_DIR=""
ENVIRONMENT=""
SERVICE_USER="autodeletebot"
SERVICE_GROUP="autodeletebot"

# Function to show usage
show_usage() {
    echo -e "${BLUE}🚀 Auto-Delete Bot Installation Script${NC}"
    echo "=========================================="
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --dest PATH     Installation directory (default: $DEFAULT_INSTALL_DIR)"
    echo "  --env ENV       Environment: dev, prod (default: $DEFAULT_ENV)"
    echo "  --help, -h      Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                                    # Install to default location with production config"
    echo "  $0 --dest /opt/autodeletebot         # Install to specific directory"
    echo "  $0 --env dev                         # Install with development configuration"
    echo "  $0 --dest /home/user/bot --env dev   # Install to custom location with dev config"
    echo ""
    echo "Environments:"
    echo "  dev   - Development setup with debug logging and source code mounting"
    echo "  prod  - Production setup with optimized settings and security"
    echo ""
    echo "Note: This script must be run with sudo privileges"
}

# Function to parse command line arguments
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --dest)
                INSTALL_DIR="$2"
                shift 2
                ;;
            --env)
                ENVIRONMENT="$2"
                shift 2
                ;;
            --help|-h)
                show_usage
                exit 0
                ;;
            *)
                echo -e "${RED}❌ Unknown option: $1${NC}"
                echo ""
                show_usage
                exit 1
                ;;
        esac
    done
    
    # Set defaults if not specified
    if [ -z "$INSTALL_DIR" ]; then
        INSTALL_DIR="$DEFAULT_INSTALL_DIR"
    fi
    
    if [ -z "$ENVIRONMENT" ]; then
        ENVIRONMENT="$DEFAULT_ENV"
    fi
    
    # Validate environment
    if [[ "$ENVIRONMENT" != "dev" && "$ENVIRONMENT" != "prod" ]]; then
        echo -e "${RED}❌ Invalid environment: $ENVIRONMENT${NC}"
        echo "Valid environments: dev, prod"
        exit 1
    fi
}

# Function to check prerequisites
check_prerequisites() {
    echo -e "${BLUE}🔍 Checking prerequisites...${NC}"
    
    # Check if running as root
    if [[ $EUID -ne 0 ]]; then
        echo -e "${RED}❌ This script must be run with sudo privileges${NC}"
        echo "Please run: sudo $0 [OPTIONS]"
        exit 1
    fi
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker is not installed. Please install Docker first.${NC}"
        echo "Installation guide: https://docs.docker.com/engine/install/"
        exit 1
    fi
    
    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null; then
        echo -e "${RED}❌ Docker Compose is not installed. Please install Docker Compose first.${NC}"
        echo "Installation guide: https://docs.docker.com/compose/install/"
        exit 1
    fi
    
    # Check Docker service status
    if ! systemctl is-active --quiet docker; then
        echo -e "${RED}❌ Docker service is not running. Please start Docker first.${NC}"
        echo "Start Docker: sudo systemctl start docker"
        exit 1
    fi
    
    echo -e "${GREEN}✅ All prerequisites are satisfied${NC}"
}

# Function to create service user
create_service_user() {
    echo -e "${BLUE}👤 Creating service user...${NC}"
    
    if ! id "$SERVICE_USER" &>/dev/null; then
        useradd -r -s /bin/false -d "$INSTALL_DIR" "$SERVICE_USER"
        echo -e "${GREEN}✅ Created user: $SERVICE_USER${NC}"
    else
        echo -e "${YELLOW}⚠️  User $SERVICE_USER already exists${NC}"
    fi
    
    if ! getent group "$SERVICE_GROUP" &>/dev/null; then
        groupadd -r "$SERVICE_GROUP"
        echo -e "${GREEN}✅ Created group: $SERVICE_GROUP${NC}"
    else
        echo -e "${YELLOW}⚠️  Group $SERVICE_GROUP already exists${NC}"
    fi
    
    # Add user to group if not already member
    if ! groups "$SERVICE_USER" | grep -q "$SERVICE_GROUP"; then
        usermod -a -G "$SERVICE_GROUP" "$SERVICE_USER"
        echo -e "${GREEN}✅ Added user $SERVICE_USER to group $SERVICE_GROUP${NC}"
    fi
}

# Function to create installation directory
create_install_directory() {
    echo -e "${BLUE}📁 Creating installation directory...${NC}"
    
    mkdir -p "$INSTALL_DIR"/{data,logs,config,deployment,backups}
    echo -e "${GREEN}✅ Created directory: $INSTALL_DIR${NC}"
}

# Function to copy deployment files
copy_deployment_files() {
    echo -e "${BLUE}📋 Copying deployment files...${NC}"
    
    # Get the directory where this script is located
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
    
    # Copy deployment files
    cp -r "$SCRIPT_DIR"/* "$INSTALL_DIR/deployment/"
    
    # Copy project files (excluding deployment directory to avoid recursion)
    rsync -av --exclude='deployment' --exclude='.git' --exclude='venv' --exclude='__pycache__' "$PROJECT_ROOT/" "$INSTALL_DIR/"
    
    echo -e "${GREEN}✅ Deployment files copied successfully${NC}"
}

# Function to configure environment
configure_environment() {
    echo -e "${BLUE}⚙️  Configuring environment: $ENVIRONMENT${NC}"
    
    # Copy appropriate docker-compose file
    if [ "$ENVIRONMENT" = "dev" ]; then
        cp "$INSTALL_DIR/deployment/docker-compose/docker-compose.dev.yml" "$INSTALL_DIR/deployment/docker-compose/docker-compose.yml"
        echo -e "${GREEN}✅ Development configuration applied${NC}"
    else
        cp "$INSTALL_DIR/deployment/docker-compose/docker-compose.prod.yml" "$INSTALL_DIR/deployment/docker-compose/docker-compose.yml"
        echo -e "${GREEN}✅ Production configuration applied${NC}"
    fi
    
    # Copy environment example
    if [ ! -f "$INSTALL_DIR/deployment/docker-compose/.env" ]; then
        cp "$INSTALL_DIR/deployment/docker-compose/env.example" "$INSTALL_DIR/deployment/docker-compose/.env"
        echo -e "${YELLOW}⚠️  Environment file created from template${NC}"
        echo "   Please edit: $INSTALL_DIR/deployment/docker-compose/.env"
    fi
}

# Function to set permissions
set_permissions() {
    echo -e "${BLUE}🔐 Setting permissions...${NC}"
    
    chown -R "$SERVICE_USER:$SERVICE_GROUP" "$INSTALL_DIR"
    chmod -R 755 "$INSTALL_DIR"
    chmod -R 770 "$INSTALL_DIR"/{data,logs,config,backups}
    chmod +x "$INSTALL_DIR/deployment/install.sh"
    chmod +x "$INSTALL_DIR/deployment/manage.sh"
    
    echo -e "${GREEN}✅ Permissions set successfully${NC}"
}

# Function to install systemd services
install_systemd_services() {
    echo -e "${BLUE}⚙️  Installing systemd services...${NC}"
    
    # Copy systemd service files
    cp "$INSTALL_DIR/deployment/systemd/"*.service /etc/systemd/system/
    cp "$INSTALL_DIR/deployment/systemd/"*.timer /etc/systemd/system/
    
    # Update service files with correct paths
    sed -i "s|/opt/autodeletebot|$INSTALL_DIR|g" /etc/systemd/system/autodeletebot*.service
    
    # Reload systemd
    systemctl daemon-reload
    
    # Enable services
    systemctl enable autodeletebot.service
    systemctl enable autodeletebot-cleanup.timer
    
    echo -e "${GREEN}✅ Systemd services installed and enabled${NC}"
}

# Function to create data directories for production
setup_production_directories() {
    if [ "$ENVIRONMENT" = "prod" ]; then
        echo -e "${BLUE}🏗️  Setting up production directories...${NC}"
        
        # Create production directories
        mkdir -p /opt/autodeletebot/{data,logs,config}
        chown -R "$SERVICE_USER:$SERVICE_GROUP" /opt/autodeletebot/{data,logs,config}
        chmod -R 770 /opt/autodeletebot/{data,logs,config}
        
        echo -e "${GREEN}✅ Production directories configured${NC}"
    fi
}

# Function to show completion message
show_completion() {
    echo ""
    echo -e "${GREEN}🎉 Installation completed successfully!${NC}"
    echo "====================================="
    echo ""
    echo -e "${BLUE}📋 Installation Details:${NC}"
    echo "   Directory: $INSTALL_DIR"
    echo "   Environment: $ENVIRONMENT"
    echo "   User: $SERVICE_USER"
    echo "   Group: $SERVICE_GROUP"
    echo ""
    echo -e "${BLUE}📋 Next Steps:${NC}"
    echo "1. Configure your bot credentials:"
    echo "   sudo nano $INSTALL_DIR/deployment/docker-compose/.env"
    echo ""
    echo "2. Start the service:"
    echo "   sudo $INSTALL_DIR/deployment/manage.sh start"
    echo ""
    echo "3. Check service status:"
    echo "   sudo $INSTALL_DIR/deployment/manage.sh status"
    echo ""
    echo "4. View logs:"
    echo "   sudo $INSTALL_DIR/deployment/manage.sh logs-follow"
    echo ""
    echo -e "${BLUE}📋 Management Commands:${NC}"
    echo "   sudo $INSTALL_DIR/deployment/manage.sh start    # Start service"
    echo "   sudo $INSTALL_DIR/deployment/manage.sh stop     # Stop service"
    echo "   sudo $INSTALL_DIR/deployment/manage.sh restart  # Restart service"
    echo "   sudo $INSTALL_DIR/deployment/manage.sh status   # Show status"
    echo "   sudo $INSTALL_DIR/deployment/manage.sh logs     # Show logs"
    echo "   sudo $INSTALL_DIR/deployment/manage.sh backup   # Backup data"
    echo ""
    echo -e "${GREEN}🚀 Your Auto-Delete Bot is ready to deploy!${NC}"
}

# Main installation function
main() {
    echo -e "${BLUE}🚀 Auto-Delete Bot Installation Script${NC}"
    echo "=========================================="
    echo ""
    echo -e "${BLUE}Configuration:${NC}"
    echo "   Installation Directory: $INSTALL_DIR"
    echo "   Environment: $ENVIRONMENT"
    echo "   Service User: $SERVICE_USER"
    echo ""
    
    check_prerequisites
    create_service_user
    create_install_directory
    copy_deployment_files
    configure_environment
    set_permissions
    install_systemd_services
    setup_production_directories
    show_completion
}

# Parse command line arguments
parse_arguments "$@"

# Run main installation
main
