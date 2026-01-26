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
from typing import Optional

# Load environment variables
load_dotenv()

# Bot configuration
TOKEN = os.getenv('DISCORD_TOKEN')
SHEET_ID = os.getenv('GOOGLE_SHEET_ID')
GM_ROLE_ID = os.getenv('GM_ROLE_ID')

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
        
        role = discord.utils.get(interaction.user.roles, id=int(GM_ROLE_ID))
        return role is not None or interaction.user.guild_permissions.administrator
    
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
    
    embed = discord.Embed(
        title=f"📋 {player['name']}'s Profile",
        color=discord.Color.blue()
    )
    embed.add_field(name="⭐ XP", value=str(player['xp']), inline=True)
    embed.add_field(name="💰 Gold", value=str(player['gold']), inline=True)
    
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
    embed.add_field(name="💰 Gold", value=str(player['gold']), inline=False)
    
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
    
    new_xp = player_data['xp'] + amount
    storage.update_player(player_id, xp=new_xp)
    
    await interaction.response.send_message(
        f"✅ Added {amount} XP to {player.mention}. New total: {new_xp} XP"
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
    
    new_xp = max(0, player_data['xp'] - amount)
    storage.update_player(player_id, xp=new_xp)
    
    await interaction.response.send_message(
        f"✅ Removed {amount} XP from {player.mention}. New total: {new_xp} XP"
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
                name=f"{item['name']} - {item['price']} gold",
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
    
    # Check if player has enough gold
    if player['gold'] < shop_item['price']:
        await interaction.response.send_message(
            f"❌ You don't have enough gold! You need {shop_item['price']} gold but only have {player['gold']} gold.",
            ephemeral=True
        )
        return
    
    # Purchase item
    new_gold = player['gold'] - shop_item['price']
    inventory = player['inventory']
    inventory.append(shop_item['name'])
    
    storage.update_player(player_id, gold=new_gold, inventory=inventory)
    
    await interaction.response.send_message(
        f"✅ Purchased **{shop_item['name']}** for {shop_item['price']} gold! You now have {new_gold} gold remaining."
    )


@bot.tree.command(name="help", description="Show all available commands")
async def help_command(interaction: discord.Interaction):
    """Show help information."""
    embed = discord.Embed(
        title="🎮 Player Tracker Bot - Help",
        description="Track your TTRPG character's progress!",
        color=discord.Color.purple()
    )
    
    embed.add_field(
        name="📊 Player Commands",
        value=(
            "`/profile` - View your character profile\n"
            "`/inventory` - View your inventory\n"
            "`/shop` - Browse the merchant's shop\n"
            "`/buy <item>` - Purchase an item from the shop"
        ),
        inline=False
    )
    
    embed.add_field(
        name="🎲 GM Commands",
        value=(
            "`/add_xp <player> <amount>` - Give XP to a player\n"
            "`/remove_xp <player> <amount>` - Remove XP from a player\n"
            "`/add_gold <player> <amount>` - Give gold to a player\n"
            "`/remove_gold <player> <amount>` - Remove gold from a player\n"
            "`/give_item <player> <item>` - Give an item to a player\n"
            "`/remove_item <player> <item>` - Remove an item from a player"
        ),
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
