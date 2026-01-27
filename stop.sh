#!/bin/bash
# Stop the Player Tracker bot services

set -e

echo "Stopping Player Tracker bot..."
sudo systemctl stop player_tracker.service
echo "✓ Player Tracker service stopped"
echo ""
echo "Stopping Merchant bot..."
sudo systemctl stop merchant_bot.service
echo "✓ Merchant Bot service stopped"
