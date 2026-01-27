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
echo "Restarting Timekeeper bot..."
sudo systemctl restart timekeeper_bot.service
echo "✓ Timekeeper Bot service restarted"
echo ""
echo "Restarting Inn bot..."
sudo systemctl restart inn_bot.service
echo "✓ Inn Bot service restarted"
echo ""
echo "Restarting Adventure bot..."
sudo systemctl restart adventure_bot.service
echo "✓ Adventure Bot service restarted"
echo ""
echo "To view logs, run:"
echo "  sudo journalctl -u player_tracker -f    # Player tracker logs"
echo "  sudo journalctl -u merchant_bot -f      # Merchant bot logs"
echo "  sudo journalctl -u timekeeper_bot -f    # Timekeeper bot logs"
echo "  sudo journalctl -u inn_bot -f           # Inn bot logs"
echo "  sudo journalctl -u adventure_bot -f     # Adventure bot logs"
