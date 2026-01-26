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

### 2. Create a Discord Bot

1. Go to https://discord.com/developers/applications
2. Click "New Application"
3. Give it a name (e.g., "Player Tracker")
4. Go to the "Bot" section
5. Click "Add Bot"
6. Under "Privileged Gateway Intents", enable:
   - MESSAGE CONTENT INTENT
   - SERVER MEMBERS INTENT
7. Click "Reset Token" and copy your bot token
8. Save this token - you'll need it for the `.env` file

### 3. Invite Bot to Your Server

1. In the Discord Developer Portal, go to "OAuth2" → "URL Generator"
2. Select these scopes:
   - `bot`
   - `applications.commands`
3. Select these bot permissions:
   - Send Messages
   - Use Slash Commands
4. Copy the generated URL and open it in your browser
5. Select your server and authorize the bot

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
   DISCORD_TOKEN=paste_your_discord_bot_token_here
   GOOGLE_SHEET_ID=paste_your_sheet_id_here
   GM_ROLE_ID=leave_blank_or_add_role_id
   ```

   **Finding your GM Role ID (optional):**
   - In Discord, go to Server Settings → Roles
   - Right-click on your GM role and copy the Role ID
   - If you don't see this option, enable Developer Mode in Discord settings

### 7. Run the Bot

```bash
python bot.py
```

You should see:
```
{BotName} has connected to Discord!
Connected to Google Sheets: {sheet_id}
Synced X command(s)
```

### 8. Test It Out!

In your Discord server, try these commands:

1. `/help` - See all available commands
2. `/profile` - Create your player profile
3. `/shop` - View the merchant shop

If you have the GM role or admin permissions:
4. `/add_gold @player 100` - Give yourself or another player gold
5. `/give_item @player "Health Potion"` - Give yourself or another player an item

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
