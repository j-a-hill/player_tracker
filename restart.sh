#!/bin/bash
# Restart the Player Tracker bot service

set -e

echo "Restarting Player Tracker bot..."
sudo systemctl restart player_tracker.service
echo "✓ Service restarted"
echo ""
echo "To view logs, run:"
echo "  sudo journalctl -u player_tracker -f"
