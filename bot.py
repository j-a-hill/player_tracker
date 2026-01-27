"""
Discord bot for TTRPG player tracking.
Manages player inventory, XP, gold, and provides a merchant system.
"""
import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv
from storage import PlayerStorage
from dnd_utils import (
    get_level_from_xp, 
    get_xp_progress, 
    format_currency,
    create_progress_bar,
    get_xp_for_level,
    parse_currency_input
)
from typing import Optional

# Load environment variables
load_dotenv()

# Bot configuration
TOKEN = os.getenv('DISCORD_TOKEN')
SHEET_ID = os.getenv('GOOGLE_SHEET_ID')
GM_ROLE_ID = os.getenv('GM_ROLE_ID')

# Currency mapping constants (removed pp and ep)
CURRENCY_NAMES = {
    'cp': 'copper',
    'sp': 'silver',
    'gp': 'gold'
}

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


@bot.event
async def on_ready():
    """Bot startup event."""
    global storage
    print(f'{bot.user} has connected to Discord!')
    
    # Initialize storage
    if SHEET_ID:
        storage = PlayerStorage(SHEET_ID)
        print(f'Connected to Google Sheets: {SHEET_ID}')
    else:
        print('Warning: No Google Sheet ID provided. Data will not persist.')
    
    # Sync commands
    try:
        synced = await bot.tree.sync()
        print(f'Synced {len(synced)} command(s)')
    except Exception as e:
        print(f'Failed to sync commands: {e}')


# Player Commands
@bot.tree.command(name="profile", description="View your character profile")
async def profile(interaction: discord.Interaction):
    """View player profile."""
    if not storage:
        await interaction.response.send_message("Storage not configured!", ephemeral=True)
        return
    
    player_id = str(interaction.user.id)
    player = storage.get_player(player_id)
    
    if not player:
        player = storage.create_player(player_id, interaction.user.display_name)
    
    # Calculate level and XP progress
    level, current_level_xp, next_level_xp, progress = get_xp_progress(player['xp'])
    progress_bar = create_progress_bar(progress)
    
    embed = discord.Embed(
        title=f"📋 {player['name']}'s Profile",
        color=discord.Color.blue()
    )
    
    # XP and Level info
    if level < 20:
        xp_text = f"Level {level}\n{player['xp']} / {next_level_xp} XP\n{progress_bar}"
    else:
        xp_text = f"Level {level} (Max Level)\n{player['xp']} XP"
    
    embed.add_field(name="⭐ Experience", value=xp_text, inline=False)
    
    # Currency info - display from copper value
    currency_text = format_currency(player['copper'])
    embed.add_field(name="💰 Currency", value=currency_text, inline=False)
    
    inventory_text = "\n".join(player['inventory']) if player['inventory'] else "Empty"
    embed.add_field(name="🎒 Inventory", value=inventory_text, inline=False)
    
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="inventory", description="View your inventory")
async def inventory(interaction: discord.Interaction):
    """View player inventory."""
    if not storage:
        await interaction.response.send_message("Storage not configured!", ephemeral=True)
        return
    
    player_id = str(interaction.user.id)
    player = storage.get_player(player_id)
    
    if not player:
        player = storage.create_player(player_id, interaction.user.display_name)
    
    embed = discord.Embed(
        title=f"🎒 {player['name']}'s Inventory",
        color=discord.Color.green()
    )
    
    if player['inventory']:
        # Count items
        item_counts = {}
        for item in player['inventory']:
            item_counts[item] = item_counts.get(item, 0) + 1
        
        inventory_text = "\n".join([f"• {item} (x{count})" for item, count in item_counts.items()])
    else:
        inventory_text = "Your inventory is empty!"
    
    embed.description = inventory_text
    
    # Currency info - display from copper value
    currency_text = format_currency(player['copper'])
    embed.add_field(name="💰 Currency", value=currency_text, inline=False)
    
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="training", description="View or start training in a skill or language")
@app_commands.describe(
    action="What to do with training",
    training_type="Type of training (skill or language)",
    name="Name of the skill or language to train"
)
@app_commands.choices(
    action=[
        app_commands.Choice(name="View Progress", value="view"),
        app_commands.Choice(name="Start Training", value="start"),
        app_commands.Choice(name="List Available", value="list")
    ],
    training_type=[
        app_commands.Choice(name="Skill", value="skill"),
        app_commands.Choice(name="Language", value="language")
    ]
)
async def training(
    interaction: discord.Interaction,
    action: str,
    training_type: Optional[str] = None,
    name: Optional[str] = None
):
    """Manage character training."""
    if not storage:
        await interaction.response.send_message("Storage not configured!", ephemeral=True)
        return
    
    player_id = str(interaction.user.id)
    player = storage.get_player(player_id)
    
    if not player:
        player = storage.create_player(player_id, interaction.user.display_name)
    
    if action == "view":
        # Show current training progress
        training_list = storage.get_player_training(player_id)
        
        embed = discord.Embed(
            title=f"📚 {player['name']}'s Training Progress",
            color=discord.Color.blue()
        )
        
        if training_list:
            for training in training_list:
                progress_pct = (training['days_spent'] / training['days_required']) * 100
                progress_bar = create_progress_bar(progress_pct / 100)
                status_emoji = "✅" if training['status'] == 'Complete' else "⏳"
                
                embed.add_field(
                    name=f"{status_emoji} {training['training_type']}: {training['skill_or_language']}",
                    value=f"{training['days_spent']} / {training['days_required']} days\n{progress_bar}",
                    inline=False
                )
        else:
            embed.description = "You are not currently training in any skills or languages.\nUse `/training start` to begin!"
        
        await interaction.response.send_message(embed=embed)
    
    elif action == "list":
        # List available training options
        if not training_type:
            await interaction.response.send_message(
                "Please specify a training type (skill or language) to list options!",
                ephemeral=True
            )
            return
        
        options = storage.get_training_options(training_type)
        
        embed = discord.Embed(
            title=f"📖 Available {training_type.title()}s for Training",
            color=discord.Color.green()
        )
        
        if options:
            # Group into chunks for better display
            option_text = ""
            for opt in options:
                option_text += f"**{opt['name']}**: {opt['description']}\n"
            embed.description = option_text
        else:
            embed.description = f"No {training_type}s available for training."
        
        await interaction.response.send_message(embed=embed)
    
    elif action == "start":
        # Start training
        if not training_type or not name:
            await interaction.response.send_message(
                "Please specify both training type and name to start training!",
                ephemeral=True
            )
            return
        
        # Check if option exists
        options = storage.get_training_options(training_type)
        option_exists = any(opt['name'].lower() == name.lower() for opt in options)
        
        if not option_exists:
            await interaction.response.send_message(
                f"❌ **{name}** is not a valid {training_type}! Use `/training list` to see available options.",
                ephemeral=True
            )
            return
        
        # Check if already training this
        current_training = storage.get_player_training(player_id)
        for training in current_training:
            if training['skill_or_language'].lower() == name.lower():
                if training['status'] == 'Complete':
                    await interaction.response.send_message(
                        f"✅ You have already completed training in **{name}**!",
                        ephemeral=True
                    )
                else:
                    await interaction.response.send_message(
                        f"⏳ You are already training in **{name}** ({training['days_spent']}/{training['days_required']} days).",
                        ephemeral=True
                    )
                return
        
        # Start the training
        success = storage.start_training(player_id, training_type.title(), name.title())
        
        if success:
            await interaction.response.send_message(
                f"✅ Started training in **{name.title()}**! Training requires 250 days of downtime. Progress will be tracked automatically by the timekeeper."
            )
        else:
            await interaction.response.send_message(
                "❌ Failed to start training. Please try again.",
                ephemeral=True
            )


# GM Commands
@bot.tree.command(name="add_xp", description="[GM] Add XP to a player")
@app_commands.describe(player="The player to give XP to", amount="Amount of XP to add")
@is_gm()
async def add_xp(interaction: discord.Interaction, player: discord.Member, amount: int):
    """Add XP to a player."""
    if not storage:
        await interaction.response.send_message("Storage not configured!", ephemeral=True)
        return
    
    player_id = str(player.id)
    player_data = storage.get_player(player_id)
    
    if not player_data:
        player_data = storage.create_player(player_id, player.display_name)
    
    old_xp = player_data['xp']
    new_xp = old_xp + amount
    old_level = get_level_from_xp(old_xp)
    new_level = get_level_from_xp(new_xp)
    
    storage.update_player(player_id, player_data, xp=new_xp)
    
    # Check for level up
    if new_level > old_level:
        # Level up occurred!
        embed = discord.Embed(
            title="🎉 LEVEL UP! 🎉",
            description=f"{player.mention} has reached **Level {new_level}**!",
            color=discord.Color.gold()
        )
        embed.add_field(name="Previous Level", value=str(old_level), inline=True)
        embed.add_field(name="New Level", value=str(new_level), inline=True)
        embed.add_field(name="Total XP", value=str(new_xp), inline=True)
        
        if new_level < 20:
            next_level_xp = get_xp_for_level(new_level + 1)
            embed.add_field(
                name="Next Level",
                value=f"{next_level_xp - new_xp} XP until level {new_level + 1}",
                inline=False
            )
        else:
            embed.add_field(name="Achievement", value="Maximum level reached!", inline=False)
        
        await interaction.response.send_message(embed=embed)
    else:
        # No level up, just show XP gain
        await interaction.response.send_message(
            f"✅ Added {amount} XP to {player.mention}. New total: {new_xp} XP (Level {new_level})"
        )


@bot.tree.command(name="remove_xp", description="[GM] Remove XP from a player")
@app_commands.describe(player="The player to remove XP from", amount="Amount of XP to remove")
@is_gm()
async def remove_xp(interaction: discord.Interaction, player: discord.Member, amount: int):
    """Remove XP from a player."""
    if not storage:
        await interaction.response.send_message("Storage not configured!", ephemeral=True)
        return
    
    player_id = str(player.id)
    player_data = storage.get_player(player_id)
    
    if not player_data:
        player_data = storage.create_player(player_id, player.display_name)
    
    old_xp = player_data['xp']
    new_xp = max(0, old_xp - amount)
    old_level = get_level_from_xp(old_xp)
    new_level = get_level_from_xp(new_xp)
    
    storage.update_player(player_id, player_data, xp=new_xp)
    
    # Check for level down
    if new_level < old_level:
        await interaction.response.send_message(
            f"✅ Removed {amount} XP from {player.mention}. New total: {new_xp} XP (Level {new_level}, down from {old_level})"
        )
    else:
        await interaction.response.send_message(
            f"✅ Removed {amount} XP from {player.mention}. New total: {new_xp} XP (Level {new_level})"
        )


@bot.tree.command(name="add_gold", description="[GM] Add currency to a player")
@app_commands.describe(
    player="The player to give currency to",
    amount="Amount of currency to add",
    currency_type="Type of currency (cp, sp, gp)"
)
@app_commands.choices(currency_type=[
    app_commands.Choice(name="Copper (cp)", value="cp"),
    app_commands.Choice(name="Silver (sp)", value="sp"),
    app_commands.Choice(name="Gold (gp)", value="gp"),
])
@is_gm()
async def add_gold(interaction: discord.Interaction, player: discord.Member, amount: int, currency_type: str = "gp"):
    """Add currency to a player."""
    if not storage:
        await interaction.response.send_message("Storage not configured!", ephemeral=True)
        return
    
    player_id = str(player.id)
    player_data = storage.get_player(player_id)
    
    if not player_data:
        player_data = storage.create_player(player_id, player.display_name)
    
    # Convert to copper and add
    copper_to_add = parse_currency_input(amount, currency_type)
    new_copper = player_data['copper'] + copper_to_add
    storage.update_player(player_id, player_data, copper=new_copper)
    
    currency_display = format_currency(new_copper)
    await interaction.response.send_message(
        f"✅ Added {amount} {CURRENCY_NAMES[currency_type]} to {player.mention}. New total: {currency_display}"
    )


@bot.tree.command(name="remove_gold", description="[GM] Remove currency from a player")
@app_commands.describe(
    player="The player to remove currency from",
    amount="Amount of currency to remove",
    currency_type="Type of currency (cp, sp, gp)"
)
@app_commands.choices(currency_type=[
    app_commands.Choice(name="Copper (cp)", value="cp"),
    app_commands.Choice(name="Silver (sp)", value="sp"),
    app_commands.Choice(name="Gold (gp)", value="gp"),
])
@is_gm()
async def remove_gold(interaction: discord.Interaction, player: discord.Member, amount: int, currency_type: str = "gp"):
    """Remove currency from a player."""
    if not storage:
        await interaction.response.send_message("Storage not configured!", ephemeral=True)
        return
    
    player_id = str(player.id)
    player_data = storage.get_player(player_id)
    
    if not player_data:
        player_data = storage.create_player(player_id, player.display_name)
    
    # Convert to copper and remove
    copper_to_remove = parse_currency_input(amount, currency_type)
    new_copper = max(0, player_data['copper'] - copper_to_remove)
    storage.update_player(player_id, player_data, copper=new_copper)
    
    currency_display = format_currency(new_copper)
    await interaction.response.send_message(
        f"✅ Removed {amount} {CURRENCY_NAMES[currency_type]} from {player.mention}. New total: {currency_display}"
    )


@bot.tree.command(name="give_item", description="[GM] Give an item to a player")
@app_commands.describe(player="The player to give the item to", item="Name of the item")
@is_gm()
async def give_item(interaction: discord.Interaction, player: discord.Member, item: str):
    """Give an item to a player."""
    if not storage:
        await interaction.response.send_message("Storage not configured!", ephemeral=True)
        return
    
    player_id = str(player.id)
    player_data = storage.get_player(player_id)
    
    if not player_data:
        player_data = storage.create_player(player_id, player.display_name)
    
    inventory = player_data['inventory']
    inventory.append(item)
    storage.update_player(player_id, player_data, inventory=inventory)
    
    await interaction.response.send_message(
        f"✅ Gave **{item}** to {player.mention}"
    )


@bot.tree.command(name="remove_item", description="[GM] Remove an item from a player")
@app_commands.describe(player="The player to remove the item from", item="Name of the item")
@is_gm()
async def remove_item(interaction: discord.Interaction, player: discord.Member, item: str):
    """Remove an item from a player."""
    if not storage:
        await interaction.response.send_message("Storage not configured!", ephemeral=True)
        return
    
    player_id = str(player.id)
    player_data = storage.get_player(player_id)
    
    if not player_data:
        await interaction.response.send_message("Player not found!", ephemeral=True)
        return
    
    inventory = player_data['inventory']
    if item in inventory:
        inventory.remove(item)
        storage.update_player(player_id, player_data, inventory=inventory)
        await interaction.response.send_message(
            f"✅ Removed **{item}** from {player.mention}"
        )
    else:
        await interaction.response.send_message(
            f"❌ {player.mention} doesn't have **{item}**",
            ephemeral=True
        )


@bot.tree.command(name="help", description="Show all available commands")
async def help_command(interaction: discord.Interaction):
    """Show help information."""
    embed = discord.Embed(
        title="🎮 Player Tracker Bot - Help",
        description="Track your D&D 5e character's progress!",
        color=discord.Color.purple()
    )
    
    embed.add_field(
        name="📊 Player Commands",
        value=(
            "`/profile` - View your character profile with level and XP\n"
            "`/inventory` - View your inventory and currency\n"
            "`/training <action>` - Manage skill/language training"
        ),
        inline=False
    )
    
    embed.add_field(
        name="📚 Training",
        value=(
            "`/training view` - See your training progress\n"
            "`/training list <type>` - List available skills or languages\n"
            "`/training start <type> <name>` - Start training in a skill/language"
        ),
        inline=False
    )
    
    embed.add_field(
        name="🎲 GM Commands - XP",
        value=(
            "`/add_xp <player> <amount>` - Give XP (shows level-up!)\n"
            "`/remove_xp <player> <amount>` - Remove XP from a player"
        ),
        inline=False
    )
    
    embed.add_field(
        name="💰 GM Commands - Currency",
        value=(
            "`/add_gold <player> <amount> [type]` - Add currency (default: gold)\n"
            "`/remove_gold <player> <amount> [type]` - Remove currency (default: gold)"
        ),
        inline=False
    )
    
    embed.add_field(
        name="🎒 GM Commands - Items",
        value=(
            "`/give_item <player> <item>` - Give an item to a player\n"
            "`/remove_item <player> <item>` - Remove an item from a player"
        ),
        inline=False
    )
    
    embed.add_field(
        name="💵 Currency Types",
        value="cp (copper), sp (silver), gp (gold)\n\nConversions: 1 gp = 10 sp = 100 cp",
        inline=False
    )
    
    embed.add_field(
        name="🏪 Shop Commands",
        value="Shop commands are available in the Merchant Bot. Use `/help` in the Merchant Bot for details.",
        inline=False
    )
    
    await interaction.response.send_message(embed=embed)


# Run the bot
if __name__ == '__main__':
    if not TOKEN:
        print("Error: DISCORD_TOKEN not found in environment variables!")
        print("Please create a .env file with your Discord bot token.")
        exit(1)
    
    bot.run(TOKEN)
