#!/bin/bash
# View logs for the Player Tracker bot service

# Default to follow mode
if [ "$1" = "-f" ] || [ "$1" = "--follow" ]; then
    echo "Following logs (Ctrl+C to exit)..."
    sudo journalctl -u player_tracker -f
elif [ "$1" = "-n" ] && [ -n "$2" ]; then
    echo "Showing last $2 log lines..."
    sudo journalctl -u player_tracker -n "$2" --no-pager
else
    echo "Showing last 50 log lines..."
    sudo journalctl -u player_tracker -n 50 --no-pager
    echo ""
    echo "Usage:"
    echo "  ./logs.sh           - Show last 50 lines"
    echo "  ./logs.sh -n 100    - Show last 100 lines"
    echo "  ./logs.sh -f        - Follow logs in real-time"
fi
