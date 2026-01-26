# Quick Start Guide

This guide will help you get the Player Tracker bot up and running quickly.

## Prerequisites Checklist

- [ ] Python 3.8+ installed
- [ ] Discord account
- [ ] Google account

## Step-by-Step Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Create Discord Bots

You'll need to create **two** Discord bots - one for player tracking and one for the merchant system.

**Main Bot (Player Tracker):**
1. Go to https://discord.com/developers/applications
2. Click "New Application"
3. Give it a name (e.g., "Player Tracker")
4. Go to the "Bot" section
5. Click "Add Bot"
6. Under "Privileged Gateway Intents", enable:
   - MESSAGE CONTENT INTENT
   - SERVER MEMBERS INTENT
7. Click "Reset Token" and copy your bot token
8. Save this token - you'll need it as `DISCORD_TOKEN` in the `.env` file

**Merchant Bot:**
1. Go back to https://discord.com/developers/applications
2. Click "New Application"
3. Give it a name (e.g., "Merchant Bot")
4. Go to the "Bot" section
5. Click "Add Bot"
6. Under "Privileged Gateway Intents", enable:
   - MESSAGE CONTENT INTENT
   - SERVER MEMBERS INTENT
7. Click "Reset Token" and copy your bot token
8. Save this token - you'll need it as `MERCHANT_BOT_TOKEN` in the `.env` file

### 3. Invite Bots to Your Server

You need to invite **both** bots to your server.

**For each bot:**
1. In the Discord Developer Portal, go to that bot's "OAuth2" → "URL Generator"
2. Select these scopes:
   - `bot`
   - `applications.commands`
3. Select these bot permissions:
   - Send Messages
   - Use Slash Commands
4. Copy the generated URL and open it in your browser
5. Select your server and authorize the bot
6. Repeat for the other bot

### 4. Set Up Google Sheets

1. Go to https://console.cloud.google.com/
2. Create a new project or select an existing one
3. Enable the Google Sheets API:
   - Go to "APIs & Services" → "Library"
   - Search for "Google Sheets API"
   - Click "Enable"
4. Create a service account:
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "Service Account"
   - Fill in the details and click "Create"
   - Click "Done" (no need to grant roles)
5. Create a key for the service account:
   - Click on the service account you just created
   - Go to the "Keys" tab
   - Click "Add Key" → "Create new key"
   - Choose JSON format
   - Download the file and save it as `credentials.json` in the project directory

### 5. Create a Google Sheet

1. Go to https://docs.google.com/spreadsheets/
2. Create a new blank spreadsheet
3. Name it "Player Tracker Data" (or whatever you prefer)
4. Copy the Sheet ID from the URL:
   ```
   https://docs.google.com/spreadsheets/d/COPY_THIS_PART/edit
   ```
5. Share the sheet with your service account:
   - Click "Share" in the top right
   - Paste the service account email (found in `credentials.json` as `client_email`)
   - Give it "Editor" access
   - Uncheck "Notify people"
   - Click "Share"

### 6. Configure Environment Variables

1. Copy the example file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your favorite text editor:
   ```env
   DISCORD_TOKEN=paste_your_player_tracker_bot_token_here
   MERCHANT_BOT_TOKEN=paste_your_merchant_bot_token_here
   GOOGLE_SHEET_ID=paste_your_sheet_id_here
   GM_ROLE_ID=leave_blank_or_add_role_id
   ```

   **Finding your GM Role ID (optional):**
   - In Discord, go to Server Settings → Roles
   - Right-click on your GM role and copy the Role ID
   - If you don't see this option, enable Developer Mode in Discord settings

### 7. Run the Bots

**Main Player Tracker Bot:**
```bash
python bot.py
```

**Merchant Bot (in a separate terminal):**
```bash
python merchant_bot.py
```

You should see for each bot:
```
{BotName} has connected to Discord!
Connected to Google Sheets: {sheet_id}
Synced X command(s)
```

### 8. Test It Out!

In your Discord server, try these commands:

**Player Tracker Bot:**
1. `/help` - See all available commands
2. `/profile` - Create your player profile
3. `/inventory` - View your inventory

**Merchant Bot:**
4. `/shop` - View the merchant shop
5. `/buy Health Potion` - Buy an item
6. `/buy Health Potion quantity:3` - Buy multiple items

If you have the GM role or admin permissions:

**Player Tracker Bot:**
7. `/add_gold @player 100` - Give yourself or another player gold
8. `/give_item @player "Health Potion"` - Give an item

**Merchant Bot:**
9. `/add_item name:"Magic Sword" price:200 description:"A powerful blade" stock:1` - Add a limited item
10. `/restock Health Potion quantity:20` - Restock an item
11. `/clear_shop` - Clear all items (to create a new shop)

## Troubleshooting

### Bot doesn't show up in Discord
- Make sure you invited the bot using the OAuth2 URL
- Check that the bot is online (green dot in server member list)

### Commands don't appear
- Wait a few minutes for Discord to sync the commands
- Try leaving and rejoining the server
- Check the bot has the "Use Slash Commands" permission

### Google Sheets errors
- Verify you shared the sheet with the service account email
- Check that the Sheet ID in `.env` is correct
- Make sure `credentials.json` is in the project directory

### "Storage not configured" message
- Check that `GOOGLE_SHEET_ID` is set in `.env`
- Verify `credentials.json` exists and is valid JSON

### GM commands don't work
- Verify you have administrator permissions in the server
- If using a GM role, check the `GM_ROLE_ID` in `.env` is correct

## Next Steps

- Customize the shop items in the Google Sheet
- Add more players using `/profile`
- Start your campaign and track progress!

## Need Help?

Check the main README.md for more detailed information and documentation.

## Deploying on Oracle VM (Production)

If you want to run the bot on an Oracle VM (or any Linux server) as a persistent service:

### 1. Set Up on Your VM

SSH into your Oracle VM and clone the repository:
```bash
git clone https://github.com/j-a-hill/player_tracker.git
cd player_tracker
```

### 2. Configure Your Environment

Set up your `.env` file and `credentials.json` as described in steps 4-6 above.

### 3. Deploy as a Service

Run the deployment script:
```bash
chmod +x deploy.sh
./deploy.sh
```

This will:
- Create a Python virtual environment
- Install all dependencies in the venv
- Set up a systemd service to run the bot
- Configure auto-restart on failure

### 4. Manage Your Bot

Use the provided scripts:
```bash
./start.sh      # Start the bot
./stop.sh       # Stop the bot
./restart.sh    # Restart the bot (useful after code updates)
./status.sh     # Check if bot is running
./logs.sh -f    # View live logs
```

### 5. Enable Auto-start (Optional)

If you want the bot to start automatically when the VM reboots:
```bash
sudo systemctl enable player_tracker
```

### Benefits of Service Deployment

- **Auto-restart**: Bot automatically restarts if it crashes
- **Background execution**: Runs in the background, SSH session can be closed
- **Easy management**: Simple commands to start/stop/restart
- **Logging**: All output is captured by systemd for easy debugging
- **Boot persistence**: Can auto-start when server reboots
