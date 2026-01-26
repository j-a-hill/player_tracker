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
    get_xp_for_level
)
from typing import Optional

# Load environment variables
load_dotenv()

# Bot configuration
TOKEN = os.getenv('DISCORD_TOKEN')
SHEET_ID = os.getenv('GOOGLE_SHEET_ID')
GM_ROLE_ID = os.getenv('GM_ROLE_ID')

# Currency mapping constants
CURRENCY_MAP = {
    'cp': 'copper',
    'sp': 'silver',
    'ep': 'electrum',
    'gp': 'gold',
    'pp': 'platinum'
}

CURRENCY_NAMES = {
    'cp': 'copper',
    'sp': 'silver',
    'ep': 'electrum',
    'gp': 'gold',
    'pp': 'platinum'
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
    
    # Currency info
    currency_text = format_currency(
        cp=player['copper'],
        sp=player['silver'],
        ep=player['electrum'],
        gp=player['gold'],
        pp=player['platinum']
    )
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
    
    # Currency info
    currency_text = format_currency(
        cp=player['copper'],
        sp=player['silver'],
        ep=player['electrum'],
        gp=player['gold'],
        pp=player['platinum']
    )
    embed.add_field(name="💰 Currency", value=currency_text, inline=False)
    
    await interaction.response.send_message(embed=embed)


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
    
    storage.update_player(player_id, xp=new_xp)
    
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
    
    storage.update_player(player_id, xp=new_xp)
    
    # Check for level down
    if new_level < old_level:
        await interaction.response.send_message(
            f"✅ Removed {amount} XP from {player.mention}. New total: {new_xp} XP (Level {new_level}, down from {old_level})"
        )
    else:
        await interaction.response.send_message(
            f"✅ Removed {amount} XP from {player.mention}. New total: {new_xp} XP (Level {new_level})"
        )


@bot.tree.command(name="add_gold", description="[GM] Add gold to a player")
@app_commands.describe(player="The player to give gold to", amount="Amount of gold to add")
@is_gm()
async def add_gold(interaction: discord.Interaction, player: discord.Member, amount: int):
    """Add gold to a player."""
    if not storage:
        await interaction.response.send_message("Storage not configured!", ephemeral=True)
        return
    
    player_id = str(player.id)
    player_data = storage.get_player(player_id)
    
    if not player_data:
        player_data = storage.create_player(player_id, player.display_name)
    
    new_gold = player_data['gold'] + amount
    storage.update_player(player_id, gold=new_gold)
    
    await interaction.response.send_message(
        f"✅ Added {amount} gold to {player.mention}. New total: {new_gold} gold"
    )


@bot.tree.command(name="remove_gold", description="[GM] Remove gold from a player")
@app_commands.describe(player="The player to remove gold from", amount="Amount of gold to remove")
@is_gm()
async def remove_gold(interaction: discord.Interaction, player: discord.Member, amount: int):
    """Remove gold from a player."""
    if not storage:
        await interaction.response.send_message("Storage not configured!", ephemeral=True)
        return
    
    player_id = str(player.id)
    player_data = storage.get_player(player_id)
    
    if not player_data:
        player_data = storage.create_player(player_id, player.display_name)
    
    new_gold = max(0, player_data['gold'] - amount)
    storage.update_player(player_id, gold=new_gold)
    
    await interaction.response.send_message(
        f"✅ Removed {amount} gold from {player.mention}. New total: {new_gold} gold"
    )


@bot.tree.command(name="add_currency", description="[GM] Add currency to a player")
@app_commands.describe(
    player="The player to give currency to",
    amount="Amount of currency to add",
    currency_type="Type of currency (cp, sp, ep, gp, pp)"
)
@app_commands.choices(currency_type=[
    app_commands.Choice(name="Copper (cp)", value="cp"),
    app_commands.Choice(name="Silver (sp)", value="sp"),
    app_commands.Choice(name="Electrum (ep)", value="ep"),
    app_commands.Choice(name="Gold (gp)", value="gp"),
    app_commands.Choice(name="Platinum (pp)", value="pp"),
])
@is_gm()
async def add_currency(interaction: discord.Interaction, player: discord.Member, amount: int, currency_type: str):
    """Add currency to a player."""
    if not storage:
        await interaction.response.send_message("Storage not configured!", ephemeral=True)
        return
    
    player_id = str(player.id)
    player_data = storage.get_player(player_id)
    
    if not player_data:
        player_data = storage.create_player(player_id, player.display_name)
    
    field_name = CURRENCY_MAP[currency_type]
    current_amount = player_data[field_name]
    new_amount = current_amount + amount
    
    # Update the specific currency
    storage.update_player(player_id, **{field_name: new_amount})
    
    await interaction.response.send_message(
        f"✅ Added {amount} {CURRENCY_NAMES[currency_type]} to {player.mention}. New total: {new_amount} {currency_type}"
    )


@bot.tree.command(name="remove_currency", description="[GM] Remove currency from a player")
@app_commands.describe(
    player="The player to remove currency from",
    amount="Amount of currency to remove",
    currency_type="Type of currency (cp, sp, ep, gp, pp)"
)
@app_commands.choices(currency_type=[
    app_commands.Choice(name="Copper (cp)", value="cp"),
    app_commands.Choice(name="Silver (sp)", value="sp"),
    app_commands.Choice(name="Electrum (ep)", value="ep"),
    app_commands.Choice(name="Gold (gp)", value="gp"),
    app_commands.Choice(name="Platinum (pp)", value="pp"),
])
@is_gm()
async def remove_currency(interaction: discord.Interaction, player: discord.Member, amount: int, currency_type: str):
    """Remove currency from a player."""
    if not storage:
        await interaction.response.send_message("Storage not configured!", ephemeral=True)
        return
    
    player_id = str(player.id)
    player_data = storage.get_player(player_id)
    
    if not player_data:
        player_data = storage.create_player(player_id, player.display_name)
    
    field_name = CURRENCY_MAP[currency_type]
    current_amount = player_data[field_name]
    new_amount = max(0, current_amount - amount)
    
    # Update the specific currency
    storage.update_player(player_id, **{field_name: new_amount})
    
    await interaction.response.send_message(
        f"✅ Removed {amount} {CURRENCY_NAMES[currency_type]} from {player.mention}. New total: {new_amount} {currency_type}"
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
    storage.update_player(player_id, inventory=inventory)
    
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
        storage.update_player(player_id, inventory=inventory)
        await interaction.response.send_message(
            f"✅ Removed **{item}** from {player.mention}"
        )
    else:
        await interaction.response.send_message(
            f"❌ {player.mention} doesn't have **{item}**",
            ephemeral=True
        )


# Merchant Commands
@bot.tree.command(name="shop", description="View available items in the shop")
async def shop(interaction: discord.Interaction):
    """View shop items."""
    if not storage:
        await interaction.response.send_message("Storage not configured!", ephemeral=True)
        return
    
    items = storage.get_shop_items()
    
    embed = discord.Embed(
        title="🏪 Merchant Shop",
        description="Welcome to the shop! Use `/buy` to purchase items.",
        color=discord.Color.gold()
    )
    
    if items:
        for item in items:
            embed.add_field(
                name=f"{item['name']} - {item['price']} {item['currency']}",
                value=item['description'],
                inline=False
            )
    else:
        embed.description = "The shop is currently empty!"
    
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="buy", description="Buy an item from the shop")
@app_commands.describe(item="Name of the item to buy")
async def buy(interaction: discord.Interaction, item: str):
    """Buy an item from the shop."""
    if not storage:
        await interaction.response.send_message("Storage not configured!", ephemeral=True)
        return
    
    # Get shop items
    shop_items = storage.get_shop_items()
    shop_item = None
    
    for si in shop_items:
        if si['name'].lower() == item.lower():
            shop_item = si
            break
    
    if not shop_item:
        await interaction.response.send_message(
            f"❌ **{item}** is not available in the shop!",
            ephemeral=True
        )
        return
    
    # Get player data
    player_id = str(interaction.user.id)
    player = storage.get_player(player_id)
    
    if not player:
        player = storage.create_player(player_id, interaction.user.display_name)
    
    currency_type = shop_item['currency']
    field_name = CURRENCY_MAP[currency_type]
    player_currency = player[field_name]
    
    # Check if player has enough currency
    if player_currency < shop_item['price']:
        await interaction.response.send_message(
            f"❌ You don't have enough {currency_type}! You need {shop_item['price']} {currency_type} but only have {player_currency} {currency_type}.",
            ephemeral=True
        )
        return
    
    # Purchase item
    new_currency = player_currency - shop_item['price']
    inventory = player['inventory']
    inventory.append(shop_item['name'])
    
    storage.update_player(player_id, inventory=inventory, **{field_name: new_currency})
    
    await interaction.response.send_message(
        f"✅ Purchased **{shop_item['name']}** for {shop_item['price']} {currency_type}! You now have {new_currency} {currency_type} remaining."
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
            "`/shop` - Browse the merchant's shop\n"
            "`/buy <item>` - Purchase an item from the shop"
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
            "`/add_currency <player> <amount> <type>` - Add any currency\n"
            "`/remove_currency <player> <amount> <type>` - Remove currency\n"
            "`/add_gold <player> <amount>` - Quick add gold\n"
            "`/remove_gold <player> <amount>` - Quick remove gold"
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
        value="cp (copper), sp (silver), ep (electrum), gp (gold), pp (platinum)",
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
