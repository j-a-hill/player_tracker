"""
Discord bot for TTRPG inn management.
Manages weekly inn charges for players.
"""
import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv
from storage import PlayerStorage
from dnd_utils import format_currency, parse_currency_input
import yaml
from typing import Optional

# Load environment variables
load_dotenv()

# Bot configuration
TOKEN = os.getenv('INN_BOT_TOKEN')
SHEET_ID = os.getenv('GOOGLE_SHEET_ID')
GM_ROLE_ID = os.getenv('GM_ROLE_ID')

# Load timekeeper config for default inn cost
with open('timekeeper_config.yaml', 'r') as f:
    config = yaml.safe_load(f)

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


@bot.tree.command(name="inn_status", description="View your inn cost and exemption status")
async def inn_status(interaction: discord.Interaction):
    """View inn status."""
    if not storage:
        await interaction.response.send_message("Storage not configured!", ephemeral=True)
        return
    
    player_id = str(interaction.user.id)
    player = storage.get_player(player_id)
    
    if not player:
        player = storage.create_player(player_id, interaction.user.display_name)
    
    inn_config = storage.get_inn_config(player_id)
    default_cost = config.get('default_inn_cost_copper', 350)
    
    embed = discord.Embed(
        title=f"🏨 {player['name']}'s Inn Status",
        color=discord.Color.gold()
    )
    
    # Current balance
    balance = format_currency(player['copper'])
    embed.add_field(name="💰 Current Balance", value=balance, inline=False)
    
    # Exemption status
    if inn_config.get('exempt', False):
        exempt_text = "✅ Yes (No weekly charges)"
    else:
        exempt_text = "❌ No (Charges apply)"
    embed.add_field(name="Exempt from Charges", value=exempt_text, inline=True)
    
    # Weekly cost
    if inn_config.get('exempt', False):
        cost_text = "Free (Exempt)"
    else:
        cost = inn_config.get('custom_cost') or default_cost
        cost_text = format_currency(cost)
    embed.add_field(name="Weekly Inn Cost", value=cost_text, inline=True)
    
    # Info about automatic charges
    embed.set_footer(text="Inn charges are automatically deducted each in-game week by the Timekeeper")
    
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="set_inn_cost", description="[GM] Set weekly inn cost for the server or a player")
@app_commands.describe(
    cost="Weekly cost in copper (leave empty to view current default)",
    player="Specific player to set custom cost for (optional)"
)
@is_gm()
async def set_inn_cost(
    interaction: discord.Interaction,
    cost: Optional[int] = None,
    player: Optional[discord.Member] = None
):
    """Set inn cost."""
    if not storage:
        await interaction.response.send_message("Storage not configured!", ephemeral=True)
        return
    
    if cost is None:
        # Show current default cost
        default_cost = config.get('default_inn_cost_copper', 350)
        cost_display = format_currency(default_cost)
        await interaction.response.send_message(
            f"ℹ️ Current default weekly inn cost: **{cost_display}**\n"
            f"To change it, edit the `timekeeper_config.yaml` file and restart the bot.",
            ephemeral=True
        )
        return
    
    if cost < 0:
        await interaction.response.send_message("Cost cannot be negative!", ephemeral=True)
        return
    
    if player:
        # Set custom cost for specific player
        player_id = str(player.id)
        player_data = storage.get_player(player_id)
        
        if not player_data:
            player_data = storage.create_player(player_id, player.display_name)
        
        success = storage.set_inn_custom_cost(player_id, cost)
        
        if success:
            cost_display = format_currency(cost)
            await interaction.response.send_message(
                f"✅ Set custom weekly inn cost for {player.mention} to **{cost_display}**"
            )
        else:
            await interaction.response.send_message(
                "❌ Failed to set custom cost!",
                ephemeral=True
            )
    else:
        # Can't change default via bot, must edit config
        await interaction.response.send_message(
            "ℹ️ To change the default inn cost, edit the `default_inn_cost_copper` value in `timekeeper_config.yaml` and restart the bot.\n"
            "You can set a custom cost for a specific player using `/set_inn_cost <cost> <player>`.",
            ephemeral=True
        )


@bot.tree.command(name="exempt_player", description="[GM] Exempt a player from weekly inn charges")
@app_commands.describe(
    player="Player to exempt or un-exempt",
    exempt="True to exempt, False to remove exemption"
)
@is_gm()
async def exempt_player(interaction: discord.Interaction, player: discord.Member, exempt: bool = True):
    """Set player exemption status."""
    if not storage:
        await interaction.response.send_message("Storage not configured!", ephemeral=True)
        return
    
    player_id = str(player.id)
    player_data = storage.get_player(player_id)
    
    if not player_data:
        player_data = storage.create_player(player_id, player.display_name)
    
    success = storage.set_inn_exempt(player_id, exempt)
    
    if success:
        if exempt:
            await interaction.response.send_message(
                f"✅ {player.mention} is now **exempt** from weekly inn charges."
            )
        else:
            await interaction.response.send_message(
                f"✅ {player.mention} is **no longer exempt** from weekly inn charges."
            )
    else:
        await interaction.response.send_message(
            "❌ Failed to update exemption status!",
            ephemeral=True
        )


@bot.tree.command(name="charge_inn", description="[GM] Manually trigger weekly inn charges (for testing)")
@is_gm()
async def charge_inn(interaction: discord.Interaction):
    """Manually charge inn fees."""
    if not storage:
        await interaction.response.send_message("Storage not configured!", ephemeral=True)
        return
    
    await interaction.response.defer()
    
    # Get all players
    players = storage.get_all_players()
    default_cost = config.get('default_inn_cost_copper', 350)
    
    charges = []
    for player_data in players:
        player_id = player_data['player_id']
        inn_config = storage.get_inn_config(player_id)
        
        # Skip exempt players
        if inn_config.get('exempt', False):
            continue
        
        # Determine cost
        cost = inn_config.get('custom_cost') or default_cost
        
        # Charge the player
        new_copper = max(0, player_data['copper'] - cost)
        storage.update_player(player_id, player_data, copper=new_copper)
        
        # Track for response
        player_name = player_data['name']
        cost_display = format_currency(cost)
        charges.append(f"• {player_name}: {cost_display}")
    
    if charges:
        charges_text = "\n".join(charges)
        embed = discord.Embed(
            title="🏨 Inn Charges Applied",
            description=charges_text,
            color=discord.Color.blue()
        )
        await interaction.followup.send(embed=embed)
    else:
        await interaction.followup.send("No players to charge (all exempt or no players found).")


@bot.tree.command(name="inn_list", description="[GM] List all players and their inn configurations")
@is_gm()
async def inn_list(interaction: discord.Interaction):
    """List all player inn configurations."""
    if not storage:
        await interaction.response.send_message("Storage not configured!", ephemeral=True)
        return
    
    players = storage.get_all_players()
    default_cost = config.get('default_inn_cost_copper', 350)
    
    embed = discord.Embed(
        title="🏨 Inn Configuration for All Players",
        color=discord.Color.blue()
    )
    
    if players:
        for player_data in players:
            player_id = player_data['player_id']
            inn_config = storage.get_inn_config(player_id)
            
            # Build status text
            status_parts = []
            if inn_config.get('exempt', False):
                status_parts.append("✅ **Exempt**")
            else:
                cost = inn_config.get('custom_cost') or default_cost
                cost_display = format_currency(cost)
                status_parts.append(f"💰 {cost_display}/week")
            
            balance = format_currency(player_data['copper'])
            status_parts.append(f"Balance: {balance}")
            
            status_text = " | ".join(status_parts)
            embed.add_field(
                name=player_data['name'],
                value=status_text,
                inline=False
            )
    else:
        embed.description = "No players found."
    
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="help", description="Show all available inn commands")
async def help_command(interaction: discord.Interaction):
    """Show help information."""
    embed = discord.Embed(
        title="🏨 Inn Bot - Help",
        description="Manage weekly inn charges for your campaign!",
        color=discord.Color.gold()
    )
    
    embed.add_field(
        name="🛏️ Player Commands",
        value="`/inn_status` - View your weekly inn cost and exemption status",
        inline=False
    )
    
    embed.add_field(
        name="⚙️ GM Commands - Configuration",
        value=(
            "`/set_inn_cost [cost] [player]` - Set weekly cost (for specific player or view default)\n"
            "`/exempt_player <player> [exempt]` - Exempt a player from charges\n"
            "`/inn_list` - View all players' inn configurations"
        ),
        inline=False
    )
    
    embed.add_field(
        name="🧪 GM Commands - Testing",
        value="`/charge_inn` - Manually trigger weekly charges (for testing)",
        inline=False
    )
    
    embed.add_field(
        name="ℹ️ How It Works",
        value=(
            "Inn charges are automatically deducted each in-game week by the Timekeeper Bot.\n"
            "The default cost is set in `timekeeper_config.yaml`.\n"
            "Individual players can have custom costs or be exempt from charges."
        ),
        inline=False
    )
    
    await interaction.response.send_message(embed=embed)


# Run the bot
if __name__ == '__main__':
    if not TOKEN:
        print("Error: INN_BOT_TOKEN not found in environment variables!")
        print("Please add INN_BOT_TOKEN to your .env file.")
        exit(1)
    
    bot.run(TOKEN)
