# Player Tracker - Discord D&D 5e Bot

A comprehensive Discord bot system for tracking player inventory, XP, gold, and in-game time in tabletop RPG campaigns. Features five specialized bots working together: player tracker, merchant system, timekeeper, inn management, and choose-your-own-adventure events.

## Features

### Core Features
- **Player Management**: Track XP, gold, and inventory for each player
- **GM Commands**: Add/remove XP, gold, and items from players
- **Level System**: Automatic level-up notifications based on D&D 5e XP thresholds
- **Currency System**: Copper, silver, and gold with automatic conversion
- **Google Sheets Backend**: All data is stored in Google Sheets for easy access and editing

### Merchant System
- **Shop Management**: Separate bot for managing shops with custom item lists
- **Stock Tracking**: Items can have limited stock that decreases with purchases
- **Quantity Purchases**: Buy multiple items at once with the `/buy` command
- **Dynamic Pricing**: Support for different currency types (cp, sp, gp)

### Time & Downtime System (NEW)
- **In-Game Time Tracking**: Automatic or manual time progression with configurable time flow
- **Training System**: Players can train skills and languages during downtime
- **Inn Management**: Weekly living expenses with customizable costs per player
- **Weekly Events**: Automatic notifications for charges and training progress

See [TIMEKEEPER_GUIDE.md](TIMEKEEPER_GUIDE.md) for detailed documentation on the new time tracking features.

### Adventure System (NEW)
- **Choose-Your-Own-Adventure Events**: Interactive story-based quicktime events for players
- **Decision Trees**: Branching narratives with multiple outcomes
- **Button-Based Choices**: Engaging Discord button interface for player decisions
- **Rewards & Penalties**: Adventures can give or take gold, XP, and items
- **Easy Configuration**: YAML-based adventure creation - no coding required!
- **Perfect for Westmarches**: Solo adventures for players who aren't actively in sessions

See [ADVENTURE_GUIDE.md](ADVENTURE_GUIDE.md) for detailed documentation on creating and managing adventures.

## Setup

### Prerequisites

- Python 3.8 or higher
- Five Discord Bot Tokens ([Create them here](https://discord.com/developers/applications))
  - One for the main player tracker bot
  - One for the merchant bot
  - One for the timekeeper bot
  - One for the inn bot
  - One for the adventure bot (NEW)
- A Google Cloud Project with Sheets API enabled ([Guide](https://developers.google.com/sheets/api/quickstart/python))
- Google Service Account credentials JSON file

### Installation

1. Clone the repository:
```bash
git clone https://github.com/j-a-hill/player_tracker.git
cd player_tracker
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file based on `.env.example`:
```bash
cp .env.example .env
```

4. Configure your `.env` file:
```env
DISCORD_TOKEN=your_discord_bot_token_here
MERCHANT_BOT_TOKEN=your_merchant_bot_token_here
TIMEKEEPER_BOT_TOKEN=your_timekeeper_bot_token_here  # NEW
INN_BOT_TOKEN=your_inn_bot_token_here  # NEW
ADVENTURE_BOT_TOKEN=your_adventure_bot_token_here  # NEW
GOOGLE_SHEET_ID=your_google_sheet_id_here
GM_ROLE_ID=your_gm_role_id_here  # Optional
NOTIFICATION_CHANNEL_ID=your_notification_channel_id_here  # Optional, for weekly notifications
```

5. (Optional) Configure timekeeper settings in `timekeeper_config.yaml`:
   - Adjust time flow rate
   - Set default inn costs
   - Configure training requirements

6. Place your Google Service Account credentials in the project directory as `credentials.json`

### Google Sheets Setup

1. Create a new Google Sheet
2. Share the sheet with your service account email (found in `credentials.json`)
3. Copy the Sheet ID from the URL: `https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit`
4. Add the Sheet ID to your `.env` file

The bots will automatically create the required worksheets:
- **Players**: Stores player data (ID, Name, XP, Gold, Inventory)
- **Shop**: Stores merchant items (Item Name, Price, Description, Stock)
- **Training**: Stores player training progress (NEW)
- **TrainingOptions**: Available skills and languages (NEW)
- **Timekeeper**: In-game time tracking (NEW)
- **Inn**: Inn cost and exemption configuration (NEW)

### Discord Bot Setup

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Create **five** applications (one for each bot: tracker, merchant, timekeeper, inn, adventure)
3. For each application, add a bot and enable these intents in the Bot section:
   - MESSAGE CONTENT INTENT
   - SERVER MEMBERS INTENT
4. Copy all bot tokens and add them to your `.env` file
5. Invite all bots to your server using this URL for each (replace `YOUR_CLIENT_ID`):
```
https://discord.com/api/oauth2/authorize?client_id=YOUR_CLIENT_ID&permissions=2048&scope=bot%20applications.commands
```

## Usage

### Running the Bots Locally

Run all five bots (each in a separate terminal):

```bash
# Terminal 1 - Main Player Tracker
python bot.py

# Terminal 2 - Merchant Bot
python merchant_bot.py

# Terminal 3 - Timekeeper Bot
python timekeeper_bot.py

# Terminal 4 - Inn Bot
python inn_bot.py

# Terminal 5 - Adventure Bot (NEW)
python adventure_bot.py
```

All bots will connect to Discord and sync their slash commands.

### Deploying on Oracle VM (or any Linux server)

The repository includes deployment scripts for running the bot as a systemd service with a Python virtual environment.

#### Quick Deployment

1. Clone the repository on your Oracle VM:
```bash
git clone https://github.com/j-a-hill/player_tracker.git
cd player_tracker
```

2. Make sure you have your `.env` and `credentials.json` files set up

3. Run the deployment script:
```bash
./deploy.sh
```

The script will:
- Create a Python virtual environment
- Install all dependencies
- Configure systemd services for both bots (Player Tracker and Merchant Bot)
- Optionally start both bots

#### Managing the Service

After deployment, use these commands to manage both bots:

```bash
./start.sh      # Start both bots
./stop.sh       # Stop both bots
./restart.sh    # Restart both bots
./status.sh     # Check status of both bots
./logs.sh       # View Player Tracker logs (last 50 lines)
./logs.sh merchant -f    # Follow Merchant Bot logs in real-time
./logs.sh -n 100  # View last 100 lines of Player Tracker logs
```

Or use systemctl directly:
```bash
# Player Tracker Bot
sudo systemctl start player_tracker
sudo systemctl stop player_tracker
sudo systemctl restart player_tracker
sudo systemctl status player_tracker
sudo journalctl -u player_tracker -f

# Merchant Bot
sudo systemctl start merchant_bot
sudo systemctl stop merchant_bot
sudo systemctl restart merchant_bot
sudo systemctl status merchant_bot
sudo journalctl -u merchant_bot -f

# Timekeeper Bot (NEW - requires systemd service file)
sudo systemctl start timekeeper_bot
sudo systemctl stop timekeeper_bot
sudo systemctl restart timekeeper_bot
sudo systemctl status timekeeper_bot
sudo journalctl -u timekeeper_bot -f

# Inn Bot (NEW - requires systemd service file)
sudo systemctl start inn_bot
sudo systemctl stop inn_bot
sudo systemctl restart inn_bot
sudo systemctl status inn_bot
sudo journalctl -u inn_bot -f

# Adventure Bot (NEW)
sudo systemctl start adventure_bot
sudo systemctl stop adventure_bot
sudo systemctl restart adventure_bot
sudo systemctl status adventure_bot
sudo journalctl -u adventure_bot -f
```

#### Auto-start on Boot

To make all bots start automatically when the server reboots:
```bash
sudo systemctl enable player_tracker
sudo systemctl enable merchant_bot
sudo systemctl enable timekeeper_bot
sudo systemctl enable inn_bot
sudo systemctl enable adventure_bot
```

#### Updating the Bot

To update the bot after pulling changes from git:
```bash
git pull
source venv/bin/activate
pip install -r requirements.txt
./restart.sh
```

### Player Commands

**Main Bot:**
- `/profile` - View your character profile with XP, gold, and inventory
- `/inventory` - View your inventory in detail
- `/training view` - View your current training progress (NEW)
- `/training list <type>` - List available skills or languages to train (NEW)
- `/training start <type> <name>` - Start training in a skill or language (NEW)
- `/help` - Show all available player commands

**Merchant Bot:**
- `/shop` - Browse items available in the merchant's shop
- `/buy <item> [quantity]` - Purchase items from the shop (quantity defaults to 1)
- `/help` - Show all available merchant commands

**Timekeeper Bot (NEW):**
- `/current_time` - View current in-game date and time
- `/help` - Show timekeeper commands

**Inn Bot (NEW):**
- `/inn_status` - View your weekly inn cost and current balance
- `/help` - Show inn commands

**Adventure Bot (NEW):**
- `/adventure <name>` - Start a choose-your-own-adventure event
- `/adventure_list` - View all available adventures
- `/help` - Show adventure commands

### GM Commands

**Main Bot** - These commands require the GM role (or administrator permissions):

**XP Management:**
- `/add_xp <player> <amount>` - Add XP to a player (displays level-up message when thresholds are reached!)
- `/remove_xp <player> <amount>` - Remove XP from a player

**Currency Management:**
- `/add_gold <player> <amount> [currency_type]` - Add currency to a player (defaults to gold, supports cp, sp, gp)
- `/remove_gold <player> <amount> [currency_type]` - Remove currency from a player (defaults to gold, supports cp, sp, gp)

**Inventory Management:**
- `/give_item <player> <item>` - Give an item to a player
- `/remove_item <player> <item>` - Remove an item from a player

**Merchant Bot** - These commands require the GM role (or administrator permissions):

- `/add_item <name> <price> <description> [stock]` - Add a new item to the shop (stock defaults to -1 for unlimited)
- `/remove_shop_item <item>` - Remove an item from the shop
- `/restock <item> <quantity>` - Update item stock quantity (-1 for unlimited)
- `/clear_shop` - Clear all items from the shop

**Timekeeper Bot (NEW)** - These commands require the GM role (or administrator permissions):

- `/advance_time [hours] [days] [weeks]` - Manually advance in-game time
- `/set_time <date> [time]` - Set specific in-game date and time

**Inn Bot (NEW)** - These commands require the GM role (or administrator permissions):

- `/set_inn_cost [cost] [player]` - Set weekly inn cost (default or per-player)
- `/exempt_player <player> [exempt]` - Exempt a player from inn charges
- `/inn_list` - View all players' inn configurations
- `/charge_inn` - Manually trigger weekly charges (for testing)

**Adventure Bot (NEW)** - These commands require the GM role (or administrator permissions):

- `/start_adventure <player> <name>` - Start an adventure for a specific player
- `/reload_adventures` - Reload adventures from the adventures.yaml file

### Editing Shop Items

You can edit shop items directly in the Google Sheet:

1. Open your Google Sheet
2. Go to the "Shop" worksheet
3. Add/edit/remove items with columns: Item Name, Price, Description, Stock
4. Stock values: -1 for unlimited, 0 for out of stock, or any positive number for limited quantity
5. Changes are reflected immediately in both bots

### Creating Custom Item Lists

Using the merchant bot's GM commands, you can create custom shops for different scenarios:

1. Use `/clear_shop` to start fresh (optional)
2. Add items with `/add_item`:
   - Example: `/add_item name:Healing Potion price:50 description:Restores 50 HP stock:10`
   - Example: `/add_item name:Magic Scroll price:100 description:One-time spell stock:-1` (unlimited)
3. Players can view with `/shop` and buy with `/buy`
4. Restock items as needed with `/restock`

## Architecture

- **bot.py**: Main Discord bot for player tracking (XP, gold, inventory, training)
- **merchant_bot.py**: Separate Discord bot for merchant/shop system
- **timekeeper_bot.py**: Separate Discord bot for in-game time tracking
- **inn_bot.py**: Separate Discord bot for inn management
- **adventure_bot.py**: Separate Discord bot for choose-your-own-adventure events (NEW)
- **storage.py**: Google Sheets integration for data persistence
- **dnd_utils.py**: D&D 5e game mechanics (XP thresholds, currency conversion, level calculations)
- **timekeeper_config.yaml**: Configuration for time tracking and weekly events
- **adventures.yaml**: Configuration for adventure scenarios and decision trees (NEW)
- **requirements.txt**: Python dependencies
- **.env**: Configuration file (not committed to git)
- **credentials.json**: Google service account credentials (not committed to git)

## Time Tracking & Downtime Features

The new timekeeper system adds in-game time tracking, training, and weekly living expenses:

### Quick Start

1. Start the Timekeeper and Inn bots alongside your main bots
2. Use `/current_time` to see the current in-game date
3. Players can start training with `/training start type:skill name:Acrobatics`
4. As time passes (automatically or via `/advance_time`), players:
   - Progress in their training (7 days per week)
   - Get charged weekly inn fees
   - Receive notifications at the end of each week

### Example Workflow

```
# GM sets up the game
/set_time date:1492-01-01 time:08:00

# Player starts training
/training list type:skill
/training start type:skill name:Stealth

# GM advances time by one week
/advance_time weeks:1

# Timekeeper automatically:
# - Charges inn fees (default 3.5 gp/week)
# - Progresses training by 7 days
# - Sends a weekly summary notification
```

For detailed documentation on the time tracking features, see [TIMEKEEPER_GUIDE.md](TIMEKEEPER_GUIDE.md).

## Security Notes

- Never commit `.env` or `credentials.json` to version control
- Keep your Discord bot token and Google credentials secure
- Only share your Google Sheet with the service account email
- Use Discord role permissions to restrict GM commands

## Troubleshooting

**Bot doesn't respond to commands:**
- Make sure commands are synced (check bot startup logs)
- Verify the bot has permissions in your Discord server
- Check that required intents are enabled

**Google Sheets errors:**
- Verify `credentials.json` is in the correct location
- Ensure the sheet is shared with your service account email
- Check that the Sheet ID in `.env` is correct

**GM commands don't work:**
- Verify you have administrator permissions or the GM role
- Check that `GM_ROLE_ID` in `.env` matches your Discord role ID

## License

MIT License - Feel free to use and modify for your campaigns!
