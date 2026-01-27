#!/bin/bash
# View logs for the Player Tracker bot services

# If user specifies which bot, show only that bot's logs
if [ "$1" = "merchant" ]; then
    shift
    SERVICE="merchant_bot"
    SERVICE_NAME="Merchant Bot"
elif [ "$1" = "timekeeper" ]; then
    shift
    SERVICE="timekeeper_bot"
    SERVICE_NAME="Timekeeper Bot"
elif [ "$1" = "inn" ]; then
    shift
    SERVICE="inn_bot"
    SERVICE_NAME="Inn Bot"
elif [ "$1" = "adventure" ]; then
    shift
    SERVICE="adventure_bot"
    SERVICE_NAME="Adventure Bot"
elif [ "$1" = "tracker" ] || [ "$1" = "player" ]; then
    shift
    SERVICE="player_tracker"
    SERVICE_NAME="Player Tracker"
else
    # Default to player tracker
    SERVICE="player_tracker"
    SERVICE_NAME="Player Tracker"
fi

# Default to follow mode
if [ "$1" = "-f" ] || [ "$1" = "--follow" ]; then
    echo "Following $SERVICE_NAME logs (Ctrl+C to exit)..."
    sudo journalctl -u "$SERVICE" -f
elif [ "$1" = "-n" ] && [ -n "$2" ] && [[ "$2" =~ ^[0-9]+$ ]]; then
    echo "Showing last $2 $SERVICE_NAME log lines..."
    sudo journalctl -u "$SERVICE" -n "$2" --no-pager
else
    echo "Showing last 50 $SERVICE_NAME log lines..."
    sudo journalctl -u "$SERVICE" -n 50 --no-pager
    echo ""
    echo "Usage:"
    echo "  ./logs.sh [bot]           - Show last 50 lines"
    echo "  ./logs.sh [bot] -n 100    - Show last 100 lines"
    echo "  ./logs.sh [bot] -f        - Follow logs in real-time"
    echo ""
    echo "Where [bot] is one of:"
    echo "  tracker/player  - Player Tracker bot (default)"
    echo "  merchant        - Merchant bot"
    echo "  timekeeper      - Timekeeper bot"
    echo "  inn             - Inn bot"
    echo "  adventure       - Adventure bot"
fi
