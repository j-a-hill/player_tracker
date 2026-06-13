"""
Discord bot for TTRPG in-game time tracking.
Manages game calendar and coordinates weekly events.
"""
import discord
from discord.ext import commands, tasks
from discord import app_commands
import os
from dotenv import load_dotenv
from storage import PlayerStorage
from dnd_utils import format_currency
from datetime import datetime, timedelta
import yaml
from typing import Optional

# Load environment variables
load_dotenv()

# Bot configuration
TOKEN = os.getenv('TIMEKEEPER_BOT_TOKEN')
SHEET_ID = os.getenv('GOOGLE_SHEET_ID')
GM_ROLE_ID = os.getenv('GM_ROLE_ID')
NOTIFICATION_CHANNEL_ID = os.getenv('NOTIFICATION_CHANNEL_ID')

# Default timekeeper configuration
DEFAULT_CONFIG = {
    'time_ratio': 1.0,
    'start_date': '1492-01-01 08:00:00',
    'days_per_week': 7,
    'notification_day': 0,
    'notification_time': '20:00',
    'default_inn_cost_copper': 350,
    'training_days_required': 100
}

# Load timekeeper config - with error handling
try:
    with open('timekeeper_config.yaml', 'r') as f:
        config = yaml.safe_load(f)
except FileNotFoundError:
    print("Warning: timekeeper_config.yaml not found. Using default configuration.")
    config = DEFAULT_CONFIG.copy()
except Exception as e:
    print(f"Error loading timekeeper_config.yaml: {e}")
    config = DEFAULT_CONFIG.copy()

# Initialize bot with intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)
storage = None


def is_gm():
    """Check if user has GM role."""
    async def predicate(interaction: discord.Interaction) -> bool:
        if not GM_ROLE_ID:
            # If no GM role is set, allow server admins
            return interaction.user.guild_permissions.administrator
        
        try:
            role_id = int(GM_ROLE_ID)
            role = discord.utils.get(interaction.user.roles, id=role_id)
            return role is not None or interaction.user.guild_permissions.administrator
        except (ValueError, TypeError):
            # If role ID is invalid, fall back to admin check
            return interaction.user.guild_permissions.administrator
    
    return app_commands.check(predicate)


def parse_game_time(time_str: str) -> datetime:
    """Parse game time string to datetime."""
    return datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')


def format_game_time(dt: datetime) -> str:
    """Format datetime to game time string."""
    return dt.strftime('%Y-%m-%d %H:%M:%S')


def format_game_time_readable(dt: datetime) -> str:
    """Format datetime to readable string."""
    return dt.strftime('%B %d, %Y at %I:%M %p')


@bot.event
async def on_ready():
    """Bot startup event."""
    global storage
    print(f'{bot.user} has connected to Discord!')
    
    # Initialize storage
    if SHEET_ID:
        storage = PlayerStorage(SHEET_ID)
        print(f'Connected to Google Sheets: {SHEET_ID}')
        
        # Initialize game time if not set
        current_time = storage.get_game_time()
        if not current_time:
            start_time = config['start_date']
            success_time = storage.set_game_time(start_time)
            success_real = storage.set_last_real_time(format_game_time(datetime.now()))
            if success_time and success_real:
                print(f'Initialized game time to: {start_time}')
            else:
                print(f'Warning: Failed to initialize game time. Timekeeper sheet may not be accessible.')
        else:
            print(f'Game time already set to: {current_time}')
        
        # Start background task for time tracking
        time_tracker.start()
        print('Started time tracking task')
    else:
        print('Warning: No Google Sheet ID provided. Data will not persist.')
    
    # Sync commands
    try:
        synced = await bot.tree.sync()
        print(f'Synced {len(synced)} command(s)')
    except Exception as e:
        print(f'Failed to sync commands: {e}')


@tasks.loop(minutes=5)
async def time_tracker():
    """Background task to update game time and check for weekly events."""
    if not storage:
        return
    
    try:
        # Get current game time and last real time
        game_time_str = storage.get_game_time()
        last_real_time_str = storage.get_last_real_time()
        
        if not game_time_str or not last_real_time_str:
            return
        
        game_time = parse_game_time(game_time_str)
        last_real_time = parse_game_time(last_real_time_str)
        current_real_time = datetime.now()
        
        # Calculate elapsed real time
        real_elapsed = (current_real_time - last_real_time).total_seconds()
        
        # Calculate game time progression based on ratio
        time_ratio = config.get('time_ratio', 1.0)
        game_elapsed = real_elapsed * time_ratio
        
        # Update game time
        new_game_time = game_time + timedelta(seconds=game_elapsed)
        
        # Check if we crossed a week boundary (more robust method)
        # Calculate total days from epoch for both times
        old_total_days = (game_time - datetime(1970, 1, 1)).days
        new_total_days = (new_game_time - datetime(1970, 1, 1)).days
        old_weeks = old_total_days // 7
        new_weeks = new_total_days // 7
        
        if new_weeks > old_weeks:
            # Week boundary crossed, trigger weekly events
            await trigger_weekly_events(new_game_time)
        
        # Save new times
        storage.set_game_time(format_game_time(new_game_time))
        storage.set_last_real_time(format_game_time(current_real_time))
        
    except Exception as e:
        print(f'Error in time tracker: {e}')


async def trigger_weekly_events(current_time: datetime):
    """Trigger weekly events like inn charges and training progress."""
    if not storage:
        return
    
    print(f'Triggering weekly events for {format_game_time(current_time)}')
    
    # Get notification channel
    channel = None
    if NOTIFICATION_CHANNEL_ID:
        try:
            channel = bot.get_channel(int(NOTIFICATION_CHANNEL_ID))
        except (ValueError, TypeError):
            pass
    
    # If no channel configured, try to find a general channel
    if not channel:
        for guild in bot.guilds:
            for ch in guild.text_channels:
                if 'general' in ch.name.lower() or 'game' in ch.name.lower():
                    channel = ch
                    break
            if channel:
                break
    
    if not channel:
        print('Warning: No notification channel found')
        return
    
    # Charge inn fees
    inn_cost = config.get('default_inn_cost_copper', 350)
    players = storage.get_all_players()
    
    embed = discord.Embed(
        title="📅 Weekly Update",
        description=f"**{format_game_time_readable(current_time)}**",
        color=discord.Color.blue()
    )
    
    # Track charges
    charges_text = ""
    for player_data in players:
        player_id = player_data['player_id']
        inn_config = storage.get_inn_config(player_id)
        
        # Skip exempt players
        if inn_config.get('exempt', False):
            continue
        
        # Determine cost
        cost = inn_config.get('custom_cost') or inn_cost
        
        # Charge the player
        new_copper = max(0, player_data['copper'] - cost)
        storage.update_player(player_id, player_data, copper=new_copper)
        
        # Track for notification
        player_name = player_data['name']
        cost_display = format_currency(cost)
        charges_text += f"• {player_name}: {cost_display}\n"
    
    if charges_text:
        embed.add_field(name="🏨 Inn Charges", value=charges_text, inline=False)
    
    # Update training progress (7 days per week)
    training_updates = []
    for player_data in players:
        player_id = player_data['player_id']
        training_list = storage.get_player_training(player_id)
        
        for training in training_list:
            if training['status'] == 'In Progress':
                success = storage.update_training_progress(
                    player_id,
                    training['skill_or_language'],
                    7  # One week = 7 days
                )
                
                if success:
                    # Check if completed
                    updated_training = storage.get_player_training(player_id)
                    for t in updated_training:
                        if t['skill_or_language'] == training['skill_or_language']:
                            if t['status'] == 'Complete':
                                training_updates.append(
                                    f"✅ **{player_data['name']}** completed training in **{t['skill_or_language']}**!"
                                )
                            else:
                                progress = t['days_spent']
                                required = t['days_required']
                                training_updates.append(
                                    f"📚 {player_data['name']}: {t['skill_or_language']} ({progress}/{required} days)"
                                )
                            break
    
    if training_updates:
        training_text = "\n".join(training_updates)
        embed.add_field(name="📖 Training Progress", value=training_text, inline=False)
    
    # Send notification
    try:
        await channel.send(embed=embed)
        print(f'Sent weekly notification to {channel.name}')
    except Exception as e:
        print(f'Error sending weekly notification: {e}')


@bot.tree.command(name="current_time", description="Display current in-game date and time")
async def current_time(interaction: discord.Interaction):
    """Display current game time."""
    if not storage:
        await interaction.response.send_message("Storage not configured!", ephemeral=True)
        return
    
    game_time_str = storage.get_game_time()
    if not game_time_str:
        await interaction.response.send_message("Game time not initialized!", ephemeral=True)
        return
    
    game_time = parse_game_time(game_time_str)
    
    embed = discord.Embed(
        title="🕐 Current In-Game Time",
        description=format_game_time_readable(game_time),
        color=discord.Color.green()
    )
    
    # Add day of week
    day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    day_of_week = day_names[game_time.weekday()]
    embed.add_field(name="Day", value=day_of_week, inline=True)
    
    # Add time ratio info
    time_ratio = config.get('time_ratio', 1.0)
    if time_ratio == 1.0:
        ratio_text = "Real-time (1:1)"
    else:
        ratio_text = f"{time_ratio}x speed"
    embed.add_field(name="Time Flow", value=ratio_text, inline=True)
    
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="advance_time", description="[GM] Manually advance in-game time")
@app_commands.describe(
    hours="Number of hours to advance (default: 0)",
    days="Number of days to advance (default: 0)",
    weeks="Number of weeks to advance (default: 0)"
)
@is_gm()
async def advance_time(
    interaction: discord.Interaction,
    hours: int = 0,
    days: int = 0,
    weeks: int = 0
):
    """Advance game time."""
    if not storage:
        await interaction.response.send_message("Storage not configured!", ephemeral=True)
        return
    
    if hours == 0 and days == 0 and weeks == 0:
        await interaction.response.send_message(
            "Please specify at least one time value to advance!",
            ephemeral=True
        )
        return
    
    game_time_str = storage.get_game_time()
    if not game_time_str:
        await interaction.response.send_message("Game time not initialized!", ephemeral=True)
        return
    
    old_time = parse_game_time(game_time_str)
    
    # Calculate total time to advance
    total_hours = hours + (days * 24) + (weeks * 7 * 24)
    new_time = old_time + timedelta(hours=total_hours)
    
    # Check if we're advancing by a week or more
    if weeks > 0 or days >= 7:
        # Trigger weekly events for each week crossed
        current = old_time
        while current < new_time:
            next_week = current + timedelta(days=7)
            if next_week <= new_time:
                await trigger_weekly_events(next_week)
            current = next_week
    
    # Save new time
    storage.set_game_time(format_game_time(new_time))
    storage.set_last_real_time(format_game_time(datetime.now()))
    
    await interaction.response.send_message(
        f"✅ Advanced time by {weeks} week(s), {days} day(s), {hours} hour(s).\n"
        f"**New time:** {format_game_time_readable(new_time)}"
    )


@bot.tree.command(name="set_time", description="[GM] Set specific in-game date and time")
@app_commands.describe(
    date="Date in format YYYY-MM-DD",
    time="Time in format HH:MM (24-hour)"
)
@is_gm()
async def set_time(interaction: discord.Interaction, date: str, time: str = "08:00"):
    """Set game time to specific value."""
    if not storage:
        await interaction.response.send_message("Storage not configured!", ephemeral=True)
        return
    
    try:
        # Parse the input
        datetime_str = f"{date} {time}:00"
        new_time = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
        
        # Save new time
        storage.set_game_time(format_game_time(new_time))
        storage.set_last_real_time(format_game_time(datetime.now()))
        
        await interaction.response.send_message(
            f"✅ Set game time to: {format_game_time_readable(new_time)}"
        )
    except ValueError as e:
        await interaction.response.send_message(
            f"❌ Invalid date/time format! Use YYYY-MM-DD for date and HH:MM for time.\nError: {e}",
            ephemeral=True
        )


@bot.tree.command(name="help", description="Show all available timekeeper commands")
async def help_command(interaction: discord.Interaction):
    """Show help information."""
    embed = discord.Embed(
        title="🕐 Timekeeper Bot - Help",
        description="Track in-game time and coordinate weekly events!",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="⏰ Player Commands",
        value="`/current_time` - View current in-game date and time",
        inline=False
    )
    
    embed.add_field(
        name="⚙️ GM Commands",
        value=(
            "`/advance_time [hours] [days] [weeks]` - Advance time manually\n"
            "`/set_time <date> [time]` - Set specific date/time (YYYY-MM-DD HH:MM)"
        ),
        inline=False
    )
    
    embed.add_field(
        name="📅 Weekly Events",
        value=(
            "The timekeeper automatically:\n"
            "• Charges inn fees to players\n"
            "• Updates training progress\n"
            "• Sends notifications when weeks pass"
        ),
        inline=False
    )
    
    await interaction.response.send_message(embed=embed)


# Run the bot
if __name__ == '__main__':
    if not TOKEN:
        print("Error: TIMEKEEPER_BOT_TOKEN not found in environment variables!")
        print("Please add TIMEKEEPER_BOT_TOKEN to your .env file.")
        exit(1)
    
    bot.run(TOKEN)
