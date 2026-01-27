#!/bin/bash
# Check the status of the Player Tracker bot services

echo "Player Tracker Bot Status:"
echo "=========================="
sudo systemctl status player_tracker.service --no-pager
echo ""
echo "Merchant Bot Status:"
echo "===================="
sudo systemctl status merchant_bot.service --no-pager
echo ""
echo "Timekeeper Bot Status:"
echo "======================"
sudo systemctl status timekeeper_bot.service --no-pager
echo ""
echo "Inn Bot Status:"
echo "==============="
sudo systemctl status inn_bot.service --no-pager
echo ""
echo "Adventure Bot Status:"
echo "====================="
sudo systemctl status adventure_bot.service --no-pager
