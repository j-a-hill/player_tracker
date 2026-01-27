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
echo "To view logs, run:"
echo "  sudo journalctl -u player_tracker -f    # Player tracker logs"
echo "  sudo journalctl -u merchant_bot -f      # Merchant bot logs"
