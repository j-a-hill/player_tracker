#!/bin/bash
# Restart the Player Tracker bot services

set -e

echo "Restarting Player Tracker bot..."
sudo systemctl restart player_tracker.service
echo "✓ Player Tracker service restarted"
echo ""
echo "Restarting Merchant bot..."
sudo systemctl restart merchant_bot.service
echo "✓ Merchant Bot service restarted"
echo ""
echo "To view logs, run:"
echo "  sudo journalctl -u player_tracker -f    # Player tracker logs"
echo "  sudo journalctl -u merchant_bot -f      # Merchant bot logs"
