#!/bin/bash
# Stop the Player Tracker bot service

set -e

echo "Stopping Player Tracker bot..."
sudo systemctl stop player_tracker.service
echo "✓ Service stopped"
