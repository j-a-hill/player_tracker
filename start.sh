#!/bin/bash
# Start the Player Tracker bot service

set -e

echo "Starting Player Tracker bot..."
sudo systemctl start player_tracker.service
echo "✓ Service started"
echo ""
echo "To view logs, run:"
echo "  sudo journalctl -u player_tracker -f"
