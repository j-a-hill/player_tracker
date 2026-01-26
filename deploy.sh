#!/bin/bash
# Deployment script for Oracle VM with Python venv
# This script sets up the bot to run as a systemd service

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Player Tracker Bot - Deployment Script${NC}"
echo "=========================================="
echo ""

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo -e "${RED}Error: Do not run this script as root${NC}"
    echo "Run it as your regular user. It will ask for sudo when needed."
    exit 1
fi

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed${NC}"
    echo "Please install Python 3.8 or higher first"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo -e "${GREEN}✓${NC} Found Python $PYTHON_VERSION"

# Check if required files exist
if [ ! -f "bot.py" ] || [ ! -f "storage.py" ] || [ ! -f "requirements.txt" ]; then
    echo -e "${RED}Error: Required files missing${NC}"
    echo "Make sure you're in the player_tracker directory"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo ""
    echo "Creating Python virtual environment..."
    python3 -m venv venv
    echo -e "${GREEN}✓${NC} Virtual environment created"
else
    echo -e "${GREEN}✓${NC} Virtual environment already exists"
fi

# Activate virtual environment and install dependencies
echo ""
echo "Installing dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo -e "${GREEN}✓${NC} Dependencies installed"

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo ""
    echo -e "${YELLOW}Warning: .env file not found${NC}"
    if [ -f ".env.example" ]; then
        echo "Creating .env from .env.example..."
        cp .env.example .env
        echo -e "${YELLOW}Please edit .env and add your credentials${NC}"
    else
        echo -e "${RED}Error: .env.example not found${NC}"
        exit 1
    fi
fi

# Check if credentials.json exists
if [ ! -f "credentials.json" ]; then
    echo ""
    echo -e "${YELLOW}Warning: credentials.json not found${NC}"
    echo "Please add your Google Service Account credentials file"
fi

# Update the service file with current user and path
echo ""
echo "Configuring systemd service..."
CURRENT_USER=$(whoami)
CURRENT_DIR="$SCRIPT_DIR"

sed "s|YOUR_USERNAME|$CURRENT_USER|g" player_tracker.service > player_tracker.service.tmp
sed -i "s|/home/YOUR_USERNAME/player_tracker|$CURRENT_DIR|g" player_tracker.service.tmp

# Install systemd service
echo ""
echo "Installing systemd service..."
echo "This requires sudo privileges."
sudo cp player_tracker.service.tmp /etc/systemd/system/player_tracker.service
rm player_tracker.service.tmp
sudo systemctl daemon-reload
echo -e "${GREEN}✓${NC} Systemd service installed"

# Ask if user wants to enable and start the service
echo ""
read -p "Do you want to enable and start the service now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    sudo systemctl enable player_tracker.service
    sudo systemctl start player_tracker.service
    echo -e "${GREEN}✓${NC} Service enabled and started"
    echo ""
    echo "Service status:"
    sudo systemctl status player_tracker.service --no-pager
else
    echo ""
    echo "Service installed but not started."
    echo "To start it later, run:"
    echo "  sudo systemctl enable player_tracker.service"
    echo "  sudo systemctl start player_tracker.service"
fi

echo ""
echo -e "${GREEN}Deployment complete!${NC}"
echo ""
echo "Useful commands:"
echo "  sudo systemctl status player_tracker    - Check service status"
echo "  sudo systemctl stop player_tracker      - Stop the bot"
echo "  sudo systemctl start player_tracker     - Start the bot"
echo "  sudo systemctl restart player_tracker   - Restart the bot"
echo "  sudo journalctl -u player_tracker -f    - View live logs"
echo "  sudo journalctl -u player_tracker -n 50 - View last 50 log lines"
echo ""
