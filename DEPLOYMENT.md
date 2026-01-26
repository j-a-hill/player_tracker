# Deployment Guide for Oracle VM

This guide covers deploying the Player Tracker Discord bot on an Oracle VM (or any Linux server) using Python virtual environments and systemd.

## Prerequisites

Before deploying, ensure you have:

1. **Oracle VM (or any Linux server)** with:
   - Python 3.8 or higher installed
   - Systemd (standard on most modern Linux distributions)
   - Sudo access

2. **Discord Bot Setup**:
   - Bot token from Discord Developer Portal
   - Bot invited to your Discord server
   - Required intents enabled (Message Content, Server Members)

3. **Google Sheets Setup**:
   - Google Cloud project with Sheets API enabled
   - Service account credentials JSON file
   - Google Sheet created and shared with service account

## Installation Steps

### 1. Connect to Your Oracle VM

```bash
ssh your-username@your-vm-ip
```

### 2. Install Python (if not already installed)

```bash
# For Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-venv python3-pip

# For Oracle Linux/RHEL/CentOS
sudo yum install python3 python3-pip

# Verify installation
python3 --version
```

### 3. Clone the Repository

```bash
cd ~
git clone https://github.com/j-a-hill/player_tracker.git
cd player_tracker
```

### 4. Set Up Configuration Files

#### Create .env file

```bash
cp .env.example .env
nano .env  # or use your preferred editor
```

Add your credentials:
```env
DISCORD_TOKEN=your_actual_discord_bot_token
GOOGLE_SHEET_ID=your_actual_google_sheet_id
GM_ROLE_ID=your_gm_role_id_or_leave_blank
```

#### Add Google Credentials

Upload your `credentials.json` file to the server:

```bash
# Option 1: Use SCP from your local machine
scp /path/to/credentials.json your-username@your-vm-ip:~/player_tracker/

# Option 2: Create the file and paste contents
nano credentials.json
# Paste your JSON credentials and save
```

### 5. Run the Deployment Script

```bash
chmod +x deploy.sh
./deploy.sh
```

The script will:
- ✅ Create a Python virtual environment in `venv/`
- ✅ Install all dependencies from `requirements.txt`
- ✅ Configure the systemd service
- ✅ Ask if you want to start the service immediately

When prompted, choose `y` to enable and start the service.

## Managing the Bot

### Using Helper Scripts

The repository includes convenient management scripts:

```bash
./start.sh      # Start the bot
./stop.sh       # Stop the bot
./restart.sh    # Restart the bot
./status.sh     # Check bot status
./logs.sh       # View last 50 log lines
./logs.sh -f    # Follow logs in real-time (Ctrl+C to exit)
./logs.sh -n 100  # View last 100 log lines
```

### Using Systemctl Directly

```bash
# Start the service
sudo systemctl start player_tracker

# Stop the service
sudo systemctl stop player_tracker

# Restart the service
sudo systemctl restart player_tracker

# Check status
sudo systemctl status player_tracker

# View logs
sudo journalctl -u player_tracker -f
sudo journalctl -u player_tracker -n 100 --no-pager
```

## Auto-Start on Boot

To make the bot start automatically when the VM reboots:

```bash
sudo systemctl enable player_tracker
```

To disable auto-start:

```bash
sudo systemctl disable player_tracker
```

## Updating the Bot

When you need to update the bot with new code changes:

```bash
cd ~/player_tracker
git pull origin main  # or your branch name
source venv/bin/activate
pip install -r requirements.txt  # Update dependencies if needed
deactivate
./restart.sh
```

## Troubleshooting

### Check if the Service is Running

```bash
./status.sh
```

You should see:
- **Active: active (running)** in green
- Process ID (PID)
- Recent log messages

### View Recent Logs

```bash
./logs.sh -n 50
```

Look for:
- `{BotName} has connected to Discord!`
- `Connected to Google Sheets: {sheet_id}`
- `Synced X command(s)`

### Common Issues

#### Bot Not Starting

1. Check the logs for errors:
   ```bash
   ./logs.sh -n 100
   ```

2. Verify configuration files:
   ```bash
   ls -la .env credentials.json
   cat .env  # Make sure credentials are filled in
   ```

3. Test manually outside of systemd:
   ```bash
   source venv/bin/activate
   python bot.py
   # Press Ctrl+C to stop
   deactivate
   ```

#### Permission Errors

If you get permission errors:

```bash
# Make sure you own the directory
sudo chown -R $USER:$USER ~/player_tracker

# Make scripts executable
chmod +x *.sh
```

#### Service Won't Start After Reboot

1. Check if service is enabled:
   ```bash
   sudo systemctl is-enabled player_tracker
   ```

2. If it says "disabled", enable it:
   ```bash
   sudo systemctl enable player_tracker
   ```

#### Python Module Not Found

If you see module import errors:

```bash
source venv/bin/activate
pip install -r requirements.txt --upgrade
deactivate
./restart.sh
```

#### Google Sheets Connection Errors

1. Verify credentials file exists and is valid JSON:
   ```bash
   python3 -m json.tool credentials.json
   ```

2. Check that the Google Sheet is shared with the service account email (found in `credentials.json` as `client_email`)

3. Verify the Sheet ID in `.env` matches your Google Sheet URL

## Firewall Configuration

Oracle VMs often have strict firewall rules. The bot only makes **outbound** connections to:
- Discord API (discord.com)
- Google Sheets API (googleapis.com)

No inbound ports need to be opened. If you have issues:

```bash
# For Oracle Linux 8+
sudo firewall-cmd --list-all

# For Ubuntu with UFW
sudo ufw status
```

Generally, outbound HTTPS (443) should be allowed by default.

## Security Best Practices

1. **Never commit sensitive files**:
   - `.env` should never be in git (already in `.gitignore`)
   - `credentials.json` should never be in git (already in `.gitignore`)

2. **Secure your credentials**:
   ```bash
   chmod 600 .env credentials.json
   ```

3. **Keep the system updated**:
   ```bash
   # Ubuntu/Debian
   sudo apt update && sudo apt upgrade
   
   # Oracle Linux/RHEL
   sudo yum update
   ```

4. **Monitor the bot**:
   - Regularly check logs: `./logs.sh`
   - Monitor system resources: `htop` or `top`

## Resource Usage

The bot is lightweight and should use:
- **Memory**: ~50-100 MB
- **CPU**: <1% when idle, brief spikes during commands
- **Disk**: ~100 MB (including venv and dependencies)

You can monitor resource usage:

```bash
# Check specific process
ps aux | grep python

# Or use systemctl
systemctl status player_tracker
```

## Uninstalling

To completely remove the bot:

```bash
# Stop and disable the service
sudo systemctl stop player_tracker
sudo systemctl disable player_tracker

# Remove the service file
sudo rm /etc/systemd/system/player_tracker.service
sudo systemctl daemon-reload

# Remove the bot directory
cd ~
rm -rf player_tracker
```

## Support

If you encounter issues:

1. Check the logs first: `./logs.sh -n 100`
2. Review this deployment guide
3. Check the main README.md
4. Review Discord and Google Sheets setup in QUICKSTART.md

## Additional Resources

- [Oracle Cloud Infrastructure Documentation](https://docs.oracle.com/en-us/iaas/Content/home.htm)
- [Systemd Service Documentation](https://www.freedesktop.org/software/systemd/man/systemd.service.html)
- [Python Virtual Environments](https://docs.python.org/3/library/venv.html)
- [Discord Developer Portal](https://discord.com/developers/applications)
- [Google Cloud Console](https://console.cloud.google.com/)
