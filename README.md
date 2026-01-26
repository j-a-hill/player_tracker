# Player Tracker - Discord TTRPG Bot

A Discord bot for tracking player inventory, XP, and gold in tabletop RPG campaigns. Features GM commands for managing players and a merchant system for in-game shopping.

## Features

- **Player Management**: Track XP, gold, and inventory for each player
- **GM Commands**: Add/remove XP, gold, and items from players
- **Merchant System**: Players can browse and purchase items from a shop
- **Google Sheets Backend**: All data is stored in Google Sheets for easy access and editing

## Setup

### Prerequisites

- Python 3.8 or higher
- A Discord Bot Token ([Create one here](https://discord.com/developers/applications))
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
- **Shop**: Stores merchant items (Item Name, Price, Description)

### Discord Bot Setup

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application and add a bot
3. Enable these intents in the Bot section:
   - MESSAGE CONTENT INTENT
   - SERVER MEMBERS INTENT
4. Copy the bot token and add it to your `.env` file
5. Invite the bot to your server using this URL (replace `YOUR_CLIENT_ID`):
```
https://discord.com/api/oauth2/authorize?client_id=YOUR_CLIENT_ID&permissions=2048&scope=bot%20applications.commands
```

## Usage

### Running the Bot

```bash
python bot.py
```

The bot will connect to Discord and sync all slash commands.

### Player Commands

- `/profile` - View your character profile with XP, gold, and inventory
- `/inventory` - View your inventory in detail
- `/shop` - Browse items available in the merchant's shop
- `/buy <item>` - Purchase an item from the shop
- `/help` - Show all available commands

### GM Commands

These commands require the GM role (or administrator permissions):

- `/add_xp <player> <amount>` - Add XP to a player
- `/remove_xp <player> <amount>` - Remove XP from a player
- `/add_gold <player> <amount>` - Give gold to a player
- `/remove_gold <player> <amount>` - Remove gold from a player
- `/give_item <player> <item>` - Give an item to a player
- `/remove_item <player> <item>` - Remove an item from a player

### Editing Shop Items

You can edit shop items directly in the Google Sheet:

1. Open your Google Sheet
2. Go to the "Shop" worksheet
3. Add/edit/remove items with columns: Item Name, Price, Description
4. Changes are reflected immediately in the bot

## Architecture

- **bot.py**: Main Discord bot with all commands
- **storage.py**: Google Sheets integration for data persistence
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
