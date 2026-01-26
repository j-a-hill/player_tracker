# Player Tracker - Discord D&D 5e Bot

A Discord bot system for tracking player inventory, XP, and gold in tabletop RPG campaigns. Features two bots: a main player tracker and a separate merchant bot for in-game shopping with inventory management.

## Features

- **Player Management**: Track XP, gold, and inventory for each player
- **GM Commands**: Add/remove XP, gold, and items from players
- **Merchant System**: Separate bot for managing shops with custom item lists and stock tracking
- **Inventory Tracking**: Items can have limited stock that decreases with purchases
- **Quantity Purchases**: Buy multiple items at once with the `/buy` command
- **Google Sheets Backend**: All data is stored in Google Sheets for easy access and editing

## Setup

### Prerequisites

- Python 3.8 or higher
- Two Discord Bot Tokens ([Create them here](https://discord.com/developers/applications))
  - One for the main player tracker bot
  - One for the merchant bot
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
GOOGLE_SHEET_ID=your_google_sheet_id_here
GM_ROLE_ID=your_gm_role_id_here  # Optional
```

5. Place your Google Service Account credentials in the project directory as `credentials.json`

### Google Sheets Setup

1. Create a new Google Sheet
2. Share the sheet with your service account email (found in `credentials.json`)
3. Copy the Sheet ID from the URL: `https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit`
4. Add the Sheet ID to your `.env` file

The bot will automatically create the required worksheets:
- **Players**: Stores player data (ID, Name, XP, Gold, Inventory)
- **Shop**: Stores merchant items (Item Name, Price, Description, Stock)

### Discord Bot Setup

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Create **two** applications (one for main bot, one for merchant bot)
3. For each application, add a bot and enable these intents in the Bot section:
   - MESSAGE CONTENT INTENT
   - SERVER MEMBERS INTENT
4. Copy both bot tokens and add them to your `.env` file as `DISCORD_TOKEN` and `MERCHANT_BOT_TOKEN`
5. Invite both bots to your server using this URL for each (replace `YOUR_CLIENT_ID`):
```
https://discord.com/api/oauth2/authorize?client_id=YOUR_CLIENT_ID&permissions=2048&scope=bot%20applications.commands
```

## Usage

### Running the Bots Locally

To run the main player tracker bot:
```bash
python bot.py
```

To run the merchant bot (in a separate terminal):
```bash
python merchant_bot.py
```

Both bots will connect to Discord and sync their slash commands.

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
- Configure a systemd service
- Optionally start the bot

#### Managing the Service

After deployment, use these commands to manage the bot:

```bash
./start.sh      # Start the bot
./stop.sh       # Stop the bot
./restart.sh    # Restart the bot
./status.sh     # Check bot status
./logs.sh       # View logs (last 50 lines)
./logs.sh -f    # Follow logs in real-time
./logs.sh -n 100  # View last 100 lines
```

Or use systemctl directly:
```bash
sudo systemctl start player_tracker
sudo systemctl stop player_tracker
sudo systemctl restart player_tracker
sudo systemctl status player_tracker
sudo journalctl -u player_tracker -f  # View logs
```

#### Auto-start on Boot

To make the bot start automatically when the server reboots:
```bash
sudo systemctl enable player_tracker
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
- `/help` - Show all available player commands

**Merchant Bot:**
- `/shop` - Browse items available in the merchant's shop
- `/buy <item> [quantity]` - Purchase items from the shop (quantity defaults to 1)
- `/help` - Show all available merchant commands

### GM Commands

**Main Bot** - These commands require the GM role (or administrator permissions):

**XP Management:**
- `/add_xp <player> <amount>` - Add XP to a player (displays level-up message when thresholds are reached!)
- `/remove_xp <player> <amount>` - Remove XP from a player

**Currency Management:**
- `/add_currency <player> <amount> <type>` - Add any type of currency (cp, sp, ep, gp, pp)
- `/remove_currency <player> <amount> <type>` - Remove any type of currency
- `/add_gold <player> <amount>` - Quick command to add gold
- `/remove_gold <player> <amount>` - Quick command to remove gold

**Inventory Management:**
- `/give_item <player> <item>` - Give an item to a player
- `/remove_item <player> <item>` - Remove an item from a player

**Merchant Bot** - These commands require the GM role (or administrator permissions):

- `/add_item <name> <price> <description> [stock]` - Add a new item to the shop (stock defaults to -1 for unlimited)
- `/remove_shop_item <item>` - Remove an item from the shop
- `/restock <item> <quantity>` - Update item stock quantity (-1 for unlimited)
- `/clear_shop` - Clear all items from the shop

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

- **bot.py**: Main Discord bot for player tracking (XP, gold, inventory)
- **merchant_bot.py**: Separate Discord bot for merchant/shop system
- **storage.py**: Google Sheets integration for data persistence
- **dnd_utils.py**: D&D 5e game mechanics (XP thresholds, currency conversion, level calculations)
- **requirements.txt**: Python dependencies
- **.env**: Configuration file (not committed to git)
- **credentials.json**: Google service account credentials (not committed to git)

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
