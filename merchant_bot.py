"""
Discord bot for TTRPG merchant system.
Allows GMs to create custom item lists and players to purchase from them.
"""
import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv
from storage import PlayerStorage
from dnd_utils import format_currency, parse_currency_input
from typing import Optional

# Load environment variables
load_dotenv()

# Bot configuration
TOKEN = os.getenv('MERCHANT_BOT_TOKEN')
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
            stock_text = f"({item['stock']} in stock)" if item['stock'] >= 0 else "(Unlimited)"
            if item['stock'] == 0:
                stock_text = "(OUT OF STOCK)"
            
            # Get currency display name
            currency = item.get('currency', 'gp')
            
            embed.add_field(
                name=f"{item['name']} - {item['price']} {currency} {stock_text}",
                value=item['description'],
                inline=False
            )
    else:
        embed.description = "The shop is currently empty!"
    
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="buy", description="Buy an item from the shop")
@app_commands.describe(
    item="Name of the item to buy",
    quantity="Number of items to purchase (default: 1)"
)
async def buy(interaction: discord.Interaction, item: str, quantity: int = 1):
    """Buy an item from the shop."""
    if not storage:
        await interaction.response.send_message("Storage not configured!", ephemeral=True)
        return
    
    if quantity < 1:
        await interaction.response.send_message("Quantity must be at least 1!", ephemeral=True)
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
    
    # Check stock availability
    if shop_item['stock'] >= 0:  # -1 means unlimited
        if shop_item['stock'] < quantity:
            available_text = "out of stock" if shop_item['stock'] == 0 else f"only {shop_item['stock']} available"
            await interaction.response.send_message(
                f"❌ Cannot purchase {quantity} **{shop_item['name']}** - {available_text}!",
                ephemeral=True
            )
            return
    
    # Get player data
    player_id = str(interaction.user.id)
    player = storage.get_player(player_id)
    
    if not player:
        player = storage.create_player(player_id, interaction.user.display_name)
    
    # Calculate total cost
    total_cost = shop_item['price'] * quantity
    
    # Get currency type
    currency_type = shop_item.get('currency', 'gp')
    
    # Convert cost to copper
    cost_in_copper = parse_currency_input(total_cost, currency_type)
    player_copper = player['copper']
    
    # Check if player has enough currency
    if player_copper < cost_in_copper:
        needed = format_currency(cost_in_copper)
        have = format_currency(player_copper)
        await interaction.response.send_message(
            f"❌ You don't have enough currency! You need {needed} but only have {have}.",
            ephemeral=True
        )
        return
    
    # Purchase items
    new_copper = player_copper - cost_in_copper
    inventory = player['inventory']
    for _ in range(quantity):
        inventory.append(shop_item['name'])
    
    storage.update_player(player_id, player, inventory=inventory, copper=new_copper)
    
    # Update stock
    if shop_item['stock'] >= 0:
        new_stock = shop_item['stock'] - quantity
        storage.update_item_stock(shop_item['name'], new_stock)
    
    quantity_text = f"{quantity}x " if quantity > 1 else ""
    await interaction.response.send_message(
        f"✅ Purchased {quantity_text}**{shop_item['name']}** for {total_cost} {currency_type}! You now have {format_currency(new_copper)} remaining."
    )


# GM Commands
@bot.tree.command(name="add_item", description="[GM] Add an item to the shop")
@app_commands.describe(
    name="Name of the item",
    price="Price in currency",
    currency="Type of currency (cp, sp, ep, gp, pp)",
    description="Item description",
    stock="Number available (-1 for unlimited)"
)
@app_commands.choices(currency=[
    app_commands.Choice(name="Copper (cp)", value="cp"),
    app_commands.Choice(name="Silver (sp)", value="sp"),
    app_commands.Choice(name="Gold (gp)", value="gp"),
])
@is_gm()
async def add_item(
    interaction: discord.Interaction,
    name: str,
    price: int,
    currency: str,
    description: str,
    stock: int = -1
):
    """Add an item to the shop."""
    if not storage:
        await interaction.response.send_message("Storage not configured!", ephemeral=True)
        return
    
    if price < 0:
        await interaction.response.send_message("Price cannot be negative!", ephemeral=True)
        return
    
    success = storage.add_shop_item(name, price, currency, description, stock)
    
    if success:
        stock_text = f" ({stock} in stock)" if stock >= 0 else " (unlimited stock)"
        await interaction.response.send_message(
            f"✅ Added **{name}** to the shop for {price} {currency}{stock_text}!"
        )
    else:
        await interaction.response.send_message(
            "❌ Failed to add item to shop!",
            ephemeral=True
        )


@bot.tree.command(name="remove_shop_item", description="[GM] Remove an item from the shop")
@app_commands.describe(item="Name of the item to remove")
@is_gm()
async def remove_shop_item(interaction: discord.Interaction, item: str):
    """Remove an item from the shop."""
    if not storage:
        await interaction.response.send_message("Storage not configured!", ephemeral=True)
        return
    
    success = storage.remove_shop_item(item)
    
    if success:
        await interaction.response.send_message(
            f"✅ Removed **{item}** from the shop!"
        )
    else:
        await interaction.response.send_message(
            f"❌ Item **{item}** not found in shop!",
            ephemeral=True
        )


@bot.tree.command(name="restock", description="[GM] Update the stock quantity of an item")
@app_commands.describe(
    item="Name of the item",
    quantity="New stock quantity (-1 for unlimited)"
)
@is_gm()
async def restock(interaction: discord.Interaction, item: str, quantity: int):
    """Update item stock."""
    if not storage:
        await interaction.response.send_message("Storage not configured!", ephemeral=True)
        return
    
    success = storage.update_item_stock(item, quantity)
    
    if success:
        stock_text = f"{quantity}" if quantity >= 0 else "unlimited"
        await interaction.response.send_message(
            f"✅ Updated **{item}** stock to {stock_text}!"
        )
    else:
        await interaction.response.send_message(
            f"❌ Item **{item}** not found in shop!",
            ephemeral=True
        )


@bot.tree.command(name="clear_shop", description="[GM] Clear all items from the shop")
@is_gm()
async def clear_shop(interaction: discord.Interaction):
    """Clear all shop items."""
    if not storage:
        await interaction.response.send_message("Storage not configured!", ephemeral=True)
        return
    
    success = storage.clear_shop()
    
    if success:
        await interaction.response.send_message(
            "✅ Cleared all items from the shop!"
        )
    else:
        await interaction.response.send_message(
            "❌ Failed to clear shop!",
            ephemeral=True
        )


@bot.tree.command(name="help", description="Show all available merchant commands")
async def help_command(interaction: discord.Interaction):
    """Show help information."""
    embed = discord.Embed(
        title="🏪 Merchant Bot - Help",
        description="Manage your in-game shop and purchases!",
        color=discord.Color.gold()
    )
    
    embed.add_field(
        name="🛒 Player Commands",
        value=(
            "`/shop` - View available items in the shop\n"
            "`/buy <item> [quantity]` - Purchase items from the shop"
        ),
        inline=False
    )
    
    embed.add_field(
        name="⚙️ GM Commands",
        value=(
            "`/add_item <name> <price> <description> [stock]` - Add a new item to the shop\n"
            "`/remove_shop_item <item>` - Remove an item from the shop\n"
            "`/restock <item> <quantity>` - Update item stock quantity\n"
            "`/clear_shop` - Clear all items from the shop"
        ),
        inline=False
    )
    
    await interaction.response.send_message(embed=embed)


# Run the bot
if __name__ == '__main__':
    if not TOKEN:
        print("Error: MERCHANT_BOT_TOKEN not found in environment variables!")
        print("Please add MERCHANT_BOT_TOKEN to your .env file.")
        exit(1)
    
    bot.run(TOKEN)
