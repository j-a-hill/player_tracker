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
echo ""
echo "Stopping Timekeeper bot..."
sudo systemctl stop timekeeper_bot.service
echo "✓ Timekeeper Bot service stopped"
echo ""
echo "Stopping Inn bot..."
sudo systemctl stop inn_bot.service
echo "✓ Inn Bot service stopped"
echo ""
echo "Stopping Adventure bot..."
sudo systemctl stop adventure_bot.service
echo "✓ Adventure Bot service stopped"
