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
        echo -e "${YELLOW}❗ IMPORTANT: You must edit .env and add your credentials before the bot will work!${NC}"
        echo ""
        read -p "Do you want to edit .env now? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            ${EDITOR:-nano} .env
        fi
    else
        echo -e "${RED}Error: .env.example not found${NC}"
        exit 1
    fi
fi

# Verify .env has been configured
if [ -f ".env" ]; then
    if grep -q "your_discord_bot_token_here" .env || grep -q "your_google_sheet_id_here" .env; then
        echo ""
        echo -e "${YELLOW}⚠ Warning: .env file contains placeholder values${NC}"
        echo "Make sure to replace them with your actual credentials:"
        echo "  - DISCORD_TOKEN"
        echo "  - GOOGLE_SHEET_ID"
        echo ""
        read -p "Continue anyway? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "Deployment cancelled. Please configure .env and run again."
            exit 1
        fi
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
echo "Configuring systemd services..."
CURRENT_USER=$(whoami)
CURRENT_DIR="$SCRIPT_DIR"

sed -e "s|YOUR_USERNAME|$CURRENT_USER|g" -e "s|/home/YOUR_USERNAME/player_tracker|$CURRENT_DIR|g" player_tracker.service > player_tracker.service.tmp
sed -e "s|YOUR_USERNAME|$CURRENT_USER|g" -e "s|/home/YOUR_USERNAME/player_tracker|$CURRENT_DIR|g" merchant_bot.service > merchant_bot.service.tmp

# Install systemd services
echo ""
echo "Installing systemd services..."
echo "This requires sudo privileges."
sudo cp player_tracker.service.tmp /etc/systemd/system/player_tracker.service
sudo cp merchant_bot.service.tmp /etc/systemd/system/merchant_bot.service
rm player_tracker.service.tmp
rm merchant_bot.service.tmp
sudo systemctl daemon-reload
echo -e "${GREEN}✓${NC} Systemd services installed"

# Ask if user wants to enable and start the services
echo ""
read -p "Do you want to enable and start both bots now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    sudo systemctl enable player_tracker.service
    sudo systemctl enable merchant_bot.service
    sudo systemctl start player_tracker.service
    sudo systemctl start merchant_bot.service
    echo -e "${GREEN}✓${NC} Services enabled and started"
    echo ""
    echo "Player Tracker Bot status:"
    sudo systemctl status player_tracker.service --no-pager
    echo ""
    echo "Merchant Bot status:"
    sudo systemctl status merchant_bot.service --no-pager
else
    echo ""
    echo "Services installed but not started."
    echo "To start them later, run:"
    echo "  sudo systemctl enable player_tracker.service"
    echo "  sudo systemctl enable merchant_bot.service"
    echo "  sudo systemctl start player_tracker.service"
    echo "  sudo systemctl start merchant_bot.service"
fi

echo ""
echo -e "${GREEN}Deployment complete!${NC}"
echo ""
echo "Useful commands for Player Tracker Bot:"
echo "  sudo systemctl status player_tracker    - Check service status"
echo "  sudo systemctl stop player_tracker      - Stop the bot"
echo "  sudo systemctl start player_tracker     - Start the bot"
echo "  sudo systemctl restart player_tracker   - Restart the bot"
echo "  sudo journalctl -u player_tracker -f    - View live logs"
echo "  sudo journalctl -u player_tracker -n 50 - View last 50 log lines"
echo ""
echo "Useful commands for Merchant Bot:"
echo "  sudo systemctl status merchant_bot      - Check service status"
echo "  sudo systemctl stop merchant_bot        - Stop the bot"
echo "  sudo systemctl start merchant_bot       - Start the bot"
echo "  sudo systemctl restart merchant_bot     - Restart the bot"
echo "  sudo journalctl -u merchant_bot -f      - View live logs"
echo "  sudo journalctl -u merchant_bot -n 50   - View last 50 log lines"
echo ""
