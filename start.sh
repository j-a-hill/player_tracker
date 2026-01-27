#!/bin/bash
# Start the Player Tracker bot services

set -e

echo "Starting Player Tracker bot..."
sudo systemctl start player_tracker.service
echo "✓ Player Tracker service started"
echo ""
echo "Starting Merchant bot..."
sudo systemctl start merchant_bot.service
echo "✓ Merchant Bot service started"
echo ""
echo "Starting Timekeeper bot..."
sudo systemctl start timekeeper_bot.service
echo "✓ Timekeeper Bot service started"
echo ""
echo "Starting Inn bot..."
sudo systemctl start inn_bot.service
echo "✓ Inn Bot service started"
echo ""
echo "Starting Adventure bot..."
sudo systemctl start adventure_bot.service
echo "✓ Adventure Bot service started"
echo ""
echo "To view logs, run:"
echo "  sudo journalctl -u player_tracker -f    # Player tracker logs"
echo "  sudo journalctl -u merchant_bot -f      # Merchant bot logs"
echo "  sudo journalctl -u timekeeper_bot -f    # Timekeeper bot logs"
echo "  sudo journalctl -u inn_bot -f           # Inn bot logs"
echo "  sudo journalctl -u adventure_bot -f     # Adventure bot logs"
