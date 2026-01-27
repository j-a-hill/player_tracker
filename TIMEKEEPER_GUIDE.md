# Timekeeper, Inn, and Training System

This document describes the new game time tracking, inn management, and training features added to the Player Tracker bot system.

## Overview

Three new systems have been added:
1. **Timekeeper Bot** - Tracks in-game time and coordinates weekly events
2. **Inn Bot** - Manages weekly inn charges for players
3. **Training System** - Allows players to train skills and languages during downtime

## Timekeeper Bot

The Timekeeper Bot tracks in-game time and coordinates weekly events like inn charges and training progress.

### Configuration

Edit `timekeeper_config.yaml` to configure the timekeeper:

```yaml
# Time ratio: How many in-game seconds pass per real-world second
# 1.0 = 1:1 (real-time), 2.0 = 2x speed, 0.5 = half speed
time_ratio: 1.0

# Starting in-game date and time
start_date: "1492-01-01 08:00:00"

# Week definition
days_per_week: 7

# When to send weekly notifications
notification_day: 0  # 0 = Sunday
notification_time: "20:00"

# Inn charges
default_inn_cost_copper: 350  # 3.5 gold per week

# Training
training_days_required: 250  # D&D 5e standard downtime training
```

### Commands

**Player Commands:**
- `/current_time` - View current in-game date and time

**GM Commands:**
- `/advance_time [hours] [days] [weeks]` - Manually advance time
  - Example: `/advance_time hours:8 days:3` - Advance 3 days and 8 hours
  - Triggers weekly events if a week or more passes
- `/set_time <date> [time]` - Set specific date/time
  - Example: `/set_time date:1492-03-15 time:14:30`

### Weekly Events

The timekeeper automatically:
- **Charges inn fees** to non-exempt players
- **Updates training progress** (7 days per week)
- **Sends notifications** to a designated channel with a summary of charges and training progress

### Environment Variables

Add to your `.env` file:
```
TIMEKEEPER_BOT_TOKEN=your_timekeeper_bot_token_here
NOTIFICATION_CHANNEL_ID=your_notification_channel_id_here  # Optional
```

### Running the Bot

```bash
python timekeeper_bot.py
```

## Inn Bot

The Inn Bot manages weekly living expenses for players.

### Commands

**Player Commands:**
- `/inn_status` - View your weekly inn cost, exemption status, and current balance

**GM Commands:**
- `/set_inn_cost [cost] [player]` - Set weekly inn cost
  - Without arguments: View current default cost
  - With player: Set custom cost for specific player
  - Example: `/set_inn_cost cost:500 player:@Alice`
- `/exempt_player <player> [exempt]` - Exempt a player from charges
  - Example: `/exempt_player player:@Bob exempt:True`
- `/inn_list` - View all players' inn configurations
- `/charge_inn` - Manually trigger weekly charges (for testing)

### How It Works

1. Default weekly cost is set in `timekeeper_config.yaml` (default: 350 copper = 3.5 gold)
2. Each player can have:
   - **Custom cost** - Overrides the default
   - **Exemption** - No charges applied
3. Charges are automatically deducted by the Timekeeper Bot each in-game week
4. Players with insufficient funds are charged down to 0 (no debt)

### Environment Variables

Add to your `.env` file:
```
INN_BOT_TOKEN=your_inn_bot_token_here
```

### Running the Bot

```bash
python inn_bot.py
```

## Training System

The training system allows players to spend downtime training in skills or languages following D&D 5e rules.

### Commands

These commands are added to the main Player Tracker Bot (`bot.py`):

**Player Commands:**
- `/training view` - See your current training progress
- `/training list <type>` - List available skills or languages
  - `/training list type:skill` - List all D&D 5e skills
  - `/training list type:language` - List all D&D languages
- `/training start <type> <name>` - Start training
  - Example: `/training start type:skill name:Acrobatics`
  - Example: `/training start type:language name:Elvish`

### Available Options

**Skills** (D&D 5e):
- Acrobatics, Animal Handling, Arcana, Athletics, Deception
- History, Insight, Intimidation, Investigation, Medicine
- Nature, Perception, Performance, Persuasion, Religion
- Sleight of Hand, Stealth, Survival

**Languages** (D&D 5e):
- Standard: Common, Dwarvish, Elvish, Giant, Gnomish, Goblin, Halfling, Orc
- Exotic: Abyssal, Celestial, Draconic, Deep Speech, Infernal, Primordial, Sylvan, Undercommon

### How It Works

1. Player starts training with `/training start`
2. Training requires **250 in-game days** by default (configurable in `timekeeper_config.yaml`)
3. Progress is automatically updated each in-game week (7 days) by the Timekeeper Bot
4. Notifications are sent when training is completed
5. Players can train multiple things simultaneously

### Data Storage

Training data is stored in Google Sheets:
- **TrainingOptions** sheet - Available skills and languages (GM can add custom options)
- **Training** sheet - Player training progress

To add custom training options, add rows to the TrainingOptions sheet:
```
Type          | Name           | Description
Skill         | Custom Skill   | Your custom skill description
Language      | Ancient Runes  | Custom language description
```

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

The new dependency is:
- `PyYAML>=6.0` - For configuration file parsing

### 2. Create Discord Bots

Create **two new Discord bot applications**:
1. Timekeeper Bot - For time tracking
2. Inn Bot - For inn management

Get their tokens from the [Discord Developer Portal](https://discord.com/developers/applications).

### 3. Configure Environment

Add the new tokens to your `.env` file:
```bash
TIMEKEEPER_BOT_TOKEN=your_timekeeper_bot_token_here
INN_BOT_TOKEN=your_inn_bot_token_here
NOTIFICATION_CHANNEL_ID=your_notification_channel_id_here  # Optional
```

### 4. Configure Timekeeper

Edit `timekeeper_config.yaml` to adjust:
- Time flow rate (`time_ratio`)
- Starting date (`start_date`)
- Default inn cost (`default_inn_cost_copper`)
- Training requirements (`training_days_required`)

### 5. Invite Bots to Server

Use these OAuth2 URLs (replace `YOUR_CLIENT_ID`):
```
https://discord.com/api/oauth2/authorize?client_id=YOUR_CLIENT_ID&permissions=2048&scope=bot%20applications.commands
```

### 6. Run the Bots

You now need to run **four** bots:
```bash
# Terminal 1
python bot.py

# Terminal 2
python merchant_bot.py

# Terminal 3
python timekeeper_bot.py

# Terminal 4
python inn_bot.py
```

Or use the provided service files for systemd (Linux):
```bash
sudo systemctl start player_tracker
sudo systemctl start merchant_bot
sudo systemctl start timekeeper_bot  # New
sudo systemctl start inn_bot         # New
```

## Integration Example

Here's a typical workflow:

1. **GM sets up the game**:
   ```
   /set_time date:1492-01-01 time:08:00
   /set_inn_cost  # Check default cost
   ```

2. **Player checks status**:
   ```
   /profile          # Check gold
   /inn_status       # Check weekly cost
   /training list type:skill
   ```

3. **Player starts training**:
   ```
   /training start type:skill name:Acrobatics
   ```

4. **Time passes** (GM can advance manually or let it flow):
   ```
   /advance_time weeks:1  # Advance one week
   ```

5. **Weekly event occurs**:
   - Timekeeper sends notification
   - Inn charges applied
   - Training progresses 7 days
   - Summary posted to notification channel

6. **Player checks progress**:
   ```
   /training view     # Check training progress
   /inn_status        # Check remaining gold
   ```

## Google Sheets Structure

The new sheets added to your Google Spreadsheet:

### Training Sheet
| Player ID | Training Type | Skill/Language | Days Spent | Days Required | Status |
|-----------|---------------|----------------|------------|---------------|---------|
| 123456    | Skill         | Acrobatics     | 50         | 250           | In Progress |
| 123456    | Language      | Elvish         | 250        | 250           | Complete |

### TrainingOptions Sheet
| Type     | Name       | Description |
|----------|------------|-------------|
| Skill    | Acrobatics | Dexterity-based physical agility |
| Language | Elvish     | Language of elves |

### Timekeeper Sheet
| Key               | Value                |
|-------------------|----------------------|
| current_game_time | 1492-01-01 08:00:00 |
| last_real_time    | 2024-01-15 12:30:00 |

### Inn Sheet
| Player ID | Exempt | Custom Cost |
|-----------|--------|-------------|
| 123456    | FALSE  | 500         |
| 789012    | TRUE   |             |

## Testing

Run the test suite:
```bash
python test_timekeeper.py
python test_setup.py
```

Test the new features manually:
1. Start all four bots
2. Use `/current_time` to verify timekeeper is working
3. Use `/training list type:skill` to see available skills
4. Use `/training start` to begin training
5. Use `/advance_time weeks:1` to trigger a weekly event
6. Check the notification channel for weekly summary

## Troubleshooting

**Timekeeper not tracking time:**
- Check that `timekeeper_config.yaml` exists
- Verify the bot has read permissions for the file
- Check bot logs for errors

**Weekly notifications not appearing:**
- Set `NOTIFICATION_CHANNEL_ID` in `.env`
- Or ensure a channel with "general" or "game" in the name exists
- Verify bot has permission to post in the channel

**Training not progressing:**
- Verify Timekeeper Bot is running
- Check that game time is advancing
- Use `/advance_time` to manually trigger weekly events

**Inn charges not applying:**
- Verify player is not exempt (`/inn_list`)
- Check player has a profile (`/profile`)
- Ensure Timekeeper Bot is triggering weekly events

## Advanced Configuration

### Custom Time Flow

To make time flow faster (e.g., 2x speed):
```yaml
time_ratio: 2.0
```

To make time flow slower (e.g., half speed):
```yaml
time_ratio: 0.5
```

To pause time (manual advancement only):
```yaml
time_ratio: 0.0
```

### Custom Training Options

Add custom skills or languages by editing the TrainingOptions sheet in Google Sheets:
1. Open your Google Sheet
2. Go to "TrainingOptions" worksheet
3. Add a new row with Type, Name, and Description
4. Players can now train in your custom option

### Variable Inn Costs

Set different costs for different players:
```
/set_inn_cost cost:500 player:@Noble     # Expensive room
/set_inn_cost cost:200 player:@Peasant   # Cheap room
/exempt_player player:@Hermit exempt:True # Lives in the woods
```

## API Reference

### Storage Methods

New methods added to `PlayerStorage` class:

**Training:**
- `get_training_options(training_type: Optional[str] = None) -> List[Dict]`
- `get_player_training(player_id: str) -> List[Dict]`
- `start_training(player_id: str, training_type: str, skill_or_language: str, days_required: int = 250) -> bool`
- `update_training_progress(player_id: str, skill_or_language: str, days_to_add: int) -> bool`

**Timekeeper:**
- `get_game_time() -> Optional[str]`
- `set_game_time(game_time: str) -> bool`
- `get_last_real_time() -> Optional[str]`
- `set_last_real_time(real_time: str) -> bool`

**Inn:**
- `get_inn_config(player_id: str) -> Dict`
- `set_inn_exempt(player_id: str, exempt: bool) -> bool`
- `set_inn_custom_cost(player_id: str, cost: Optional[int]) -> bool`
- `get_all_players() -> List[Dict]`
