"""
Discord bot for choose-your-own-adventure style quicktime events.
Manages interactive story prompts and decision trees for westmarches campaigns.
"""
import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv
from storage import PlayerStorage
import yaml
from typing import Optional, Dict, List
import asyncio

# Load environment variables
load_dotenv()

# Bot configuration
TOKEN = os.getenv('ADVENTURE_BOT_TOKEN')
SHEET_ID = os.getenv('GOOGLE_SHEET_ID')
GM_ROLE_ID = os.getenv('GM_ROLE_ID')

# Initialize bot with intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)
storage = None
adventures = {}  # Will store loaded adventures from YAML


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


def load_adventures(config_file: str = 'adventures.yaml'):
    """Load adventure scenarios from YAML file."""
    global adventures
    try:
        with open(config_file, 'r') as f:
            adventures = yaml.safe_load(f)
            print(f"Loaded {len(adventures.get('adventures', {}))} adventure(s) from {config_file}")
    except FileNotFoundError:
        print(f"Warning: {config_file} not found. Creating example file...")
        create_example_adventures()
        try:
            with open(config_file, 'r') as f:
                adventures = yaml.safe_load(f)
        except:
            adventures = {'adventures': {}}
    except Exception as e:
        print(f"Error loading adventures: {e}")
        adventures = {'adventures': {}}


def create_example_adventures():
    """Create an example adventures.yaml file."""
    example = {
        'adventures': {
            'mysterious_stranger': {
                'name': 'The Mysterious Stranger',
                'description': 'A cloaked figure approaches you in the tavern',
                'start_node': 'intro',
                'nodes': {
                    'intro': {
                        'text': 'A mysterious cloaked figure approaches you in the dimly lit tavern. They slide a sealed letter across the table without a word. What do you do?',
                        'choices': [
                            {
                                'label': 'Open the letter',
                                'emoji': '📜',
                                'next': 'open_letter'
                            },
                            {
                                'label': 'Question the stranger',
                                'emoji': '❓',
                                'next': 'question_stranger'
                            },
                            {
                                'label': 'Ignore them',
                                'emoji': '🚫',
                                'next': 'ignore'
                            }
                        ]
                    },
                    'open_letter': {
                        'text': 'The letter reveals a treasure map with cryptic symbols. The stranger whispers "Follow it if you dare" before vanishing. You gain a Treasure Map!',
                        'rewards': {
                            'items': ['Treasure Map']
                        },
                        'is_end': True
                    },
                    'question_stranger': {
                        'text': 'The stranger smiles and says "Your curiosity is admirable." They toss you a pouch of gold coins. "Perhaps we\'ll meet again." You gain 50 gold!',
                        'rewards': {
                            'gold': 50
                        },
                        'is_end': True
                    },
                    'ignore': {
                        'text': 'The stranger sighs, disappointed. "Very well." They take back the letter and leave. You missed an opportunity.',
                        'is_end': True
                    }
                }
            },
            'goblin_ambush': {
                'name': 'Goblin Ambush',
                'description': 'Goblins attack on the road!',
                'start_node': 'ambush',
                'nodes': {
                    'ambush': {
                        'text': 'While traveling down a forest road, three goblins leap from the bushes! They demand your gold. What do you do?',
                        'choices': [
                            {
                                'label': 'Fight them',
                                'emoji': '⚔️',
                                'next': 'fight'
                            },
                            {
                                'label': 'Pay them off (10 gp)',
                                'emoji': '💰',
                                'next': 'pay',
                                'requirement': {
                                    'gold': 10
                                }
                            },
                            {
                                'label': 'Try to negotiate',
                                'emoji': '🤝',
                                'next': 'negotiate'
                            }
                        ]
                    },
                    'fight': {
                        'text': 'You draw your weapon and fight! After a fierce battle, you defeat the goblins and search their belongings. You gain 25 gold and 100 XP!',
                        'rewards': {
                            'gold': 25,
                            'xp': 100
                        },
                        'is_end': True
                    },
                    'pay': {
                        'text': 'You hand over 10 gold pieces. The goblins laugh and run off. At least you\'re safe.',
                        'penalties': {
                            'gold': 10
                        },
                        'is_end': True
                    },
                    'negotiate': {
                        'text': 'You attempt to reason with the goblins, but they\'re not interested in talk. They attack! In the chaos, you manage to escape but lose 5 gold that fell from your pouch.',
                        'penalties': {
                            'gold': 5
                        },
                        'is_end': True
                    }
                }
            }
        }
    }
    
    try:
        with open('adventures.yaml', 'w') as f:
            yaml.dump(example, f, default_flow_style=False, sort_keys=False)
        print("Created example adventures.yaml file")
    except Exception as e:
        print(f"Error creating example adventures file: {e}")


class AdventureView(discord.ui.View):
    """View for adventure choices with buttons."""
    
    def __init__(self, adventure_id: str, node_id: str, user_id: str):
        super().__init__(timeout=300)  # 5 minute timeout
        self.adventure_id = adventure_id
        self.node_id = node_id
        self.user_id = user_id
        
        # Load the node data
        adventure = adventures.get('adventures', {}).get(adventure_id, {})
        node = adventure.get('nodes', {}).get(node_id, {})
        
        # Add buttons for each choice
        for idx, choice in enumerate(node.get('choices', [])):
            button = discord.ui.Button(
                label=choice['label'],
                emoji=choice.get('emoji'),
                style=discord.ButtonStyle.primary,
                custom_id=f"choice_{idx}"
            )
            button.callback = self.create_callback(choice)
            self.add_item(button)
    
    def create_callback(self, choice):
        """Create a callback function for a button."""
        async def callback(interaction: discord.Interaction):
            # Check if this is the right user
            if str(interaction.user.id) != self.user_id:
                await interaction.response.send_message(
                    "This adventure is not for you!",
                    ephemeral=True
                )
                return
            
            # Check requirements if any
            if 'requirement' in choice:
                player = storage.get_player(self.user_id)
                if not player:
                    player = storage.create_player(self.user_id, interaction.user.display_name)
                
                req = choice['requirement']
                if 'gold' in req:
                    # Convert copper to gold for comparison
                    player_gold = player['copper'] / 100
                    if player_gold < req['gold']:
                        await interaction.response.send_message(
                            f"❌ You don't have enough gold! (Need {req['gold']} gp, have {player_gold:.1f} gp)",
                            ephemeral=True
                        )
                        return
            
            # Process the choice
            next_node = choice.get('next')
            if next_node:
                await show_adventure_node(
                    interaction,
                    self.adventure_id,
                    next_node,
                    self.user_id,
                    is_followup=True
                )
            
            # Disable all buttons after choice is made
            for item in self.children:
                item.disabled = True
            
        return callback


async def show_adventure_node(
    interaction: discord.Interaction,
    adventure_id: str,
    node_id: str,
    user_id: str,
    is_followup: bool = False
):
    """Display an adventure node to the user."""
    adventure = adventures.get('adventures', {}).get(adventure_id, {})
    if not adventure:
        response_method = interaction.response if not is_followup else interaction.followup
        await response_method.send_message("Adventure not found!", ephemeral=True)
        return
    
    node = adventure.get('nodes', {}).get(node_id, {})
    if not node:
        response_method = interaction.response if not is_followup else interaction.followup
        await response_method.send_message("Invalid adventure node!", ephemeral=True)
        return
    
    # Create embed for the node
    embed = discord.Embed(
        title=f"🎭 {adventure['name']}",
        description=node['text'],
        color=discord.Color.purple()
    )
    
    # Process rewards/penalties if this is an end node
    if node.get('is_end', False):
        player = storage.get_player(user_id)
        if not player:
            player = storage.create_player(user_id, interaction.user.display_name)
        
        # Apply rewards
        rewards_text = []
        if 'rewards' in node:
            rewards = node['rewards']
            
            if 'gold' in rewards:
                copper_to_add = rewards['gold'] * 100
                new_copper = player['copper'] + copper_to_add
                storage.update_player(user_id, player, copper=new_copper)
                rewards_text.append(f"💰 +{rewards['gold']} gp")
            
            if 'xp' in rewards:
                new_xp = player['xp'] + rewards['xp']
                storage.update_player(user_id, player, xp=new_xp)
                rewards_text.append(f"⭐ +{rewards['xp']} XP")
            
            if 'items' in rewards:
                inventory = player['inventory']
                for item in rewards['items']:
                    inventory.append(item)
                    rewards_text.append(f"🎒 +{item}")
                storage.update_player(user_id, player, inventory=inventory)
        
        # Apply penalties
        if 'penalties' in node:
            penalties = node['penalties']
            
            if 'gold' in penalties:
                copper_to_remove = penalties['gold'] * 100
                new_copper = max(0, player['copper'] - copper_to_remove)
                storage.update_player(user_id, player, copper=new_copper)
                rewards_text.append(f"💸 -{penalties['gold']} gp")
            
            if 'xp' in penalties:
                new_xp = max(0, player['xp'] - penalties['xp'])
                storage.update_player(user_id, player, xp=new_xp)
                rewards_text.append(f"📉 -{penalties['xp']} XP")
            
            if 'items' in penalties:
                inventory = player['inventory']
                for item in penalties['items']:
                    if item in inventory:
                        inventory.remove(item)
                        rewards_text.append(f"🗑️ Lost {item}")
                storage.update_player(user_id, player, inventory=inventory)
        
        if rewards_text:
            embed.add_field(
                name="📊 Results",
                value="\n".join(rewards_text),
                inline=False
            )
        
        embed.set_footer(text="Adventure Complete!")
        
        # Send final message without buttons
        if is_followup:
            await interaction.edit_original_response(embed=embed, view=None)
        else:
            await interaction.response.send_message(embed=embed)
    else:
        # Not an end node, show choices
        view = AdventureView(adventure_id, node_id, user_id)
        
        if is_followup:
            await interaction.edit_original_response(embed=embed, view=view)
        else:
            await interaction.response.send_message(embed=embed, view=view)


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
    
    # Load adventures
    load_adventures()
    
    # Sync commands
    try:
        synced = await bot.tree.sync()
        print(f'Synced {len(synced)} command(s)')
    except Exception as e:
        print(f'Failed to sync commands: {e}')


@bot.tree.command(name="adventure", description="Start a quicktime adventure event")
@app_commands.describe(adventure_name="Name of the adventure to start")
async def adventure(interaction: discord.Interaction, adventure_name: str):
    """Start an adventure for a player."""
    if not storage:
        await interaction.response.send_message("Storage not configured!", ephemeral=True)
        return
    
    # Find matching adventure (case insensitive)
    adventure_id = None
    for adv_id, adv_data in adventures.get('adventures', {}).items():
        if adv_data['name'].lower() == adventure_name.lower() or adv_id == adventure_name.lower():
            adventure_id = adv_id
            break
    
    if not adventure_id:
        await interaction.response.send_message(
            f"❌ Adventure '{adventure_name}' not found! Use `/adventure_list` to see available adventures.",
            ephemeral=True
        )
        return
    
    adventure = adventures['adventures'][adventure_id]
    start_node = adventure['start_node']
    
    # Show the first node
    await show_adventure_node(
        interaction,
        adventure_id,
        start_node,
        str(interaction.user.id)
    )


@bot.tree.command(name="adventure_list", description="List all available adventures")
async def adventure_list(interaction: discord.Interaction):
    """List all available adventures."""
    embed = discord.Embed(
        title="🎭 Available Adventures",
        description="Use `/adventure <name>` to start an adventure!",
        color=discord.Color.blue()
    )
    
    adventure_list = adventures.get('adventures', {})
    if not adventure_list:
        embed.description = "No adventures available. Ask your GM to add some!"
    else:
        for adv_id, adv_data in adventure_list.items():
            embed.add_field(
                name=adv_data['name'],
                value=adv_data.get('description', 'No description'),
                inline=False
            )
    
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="start_adventure", description="[GM] Start an adventure for a player")
@app_commands.describe(
    player="The player to start the adventure for",
    adventure_name="Name of the adventure to start"
)
@is_gm()
async def start_adventure(interaction: discord.Interaction, player: discord.Member, adventure_name: str):
    """GM command to start an adventure for a specific player."""
    if not storage:
        await interaction.response.send_message("Storage not configured!", ephemeral=True)
        return
    
    # Find matching adventure
    adventure_id = None
    for adv_id, adv_data in adventures.get('adventures', {}).items():
        if adv_data['name'].lower() == adventure_name.lower() or adv_id == adventure_name.lower():
            adventure_id = adv_id
            break
    
    if not adventure_id:
        await interaction.response.send_message(
            f"❌ Adventure '{adventure_name}' not found!",
            ephemeral=True
        )
        return
    
    adventure = adventures['adventures'][adventure_id]
    start_node = adventure['start_node']
    
    # Notify the GM
    await interaction.response.send_message(
        f"✅ Starting adventure '{adventure['name']}' for {player.mention}!",
        ephemeral=True
    )
    
    # Send the adventure to the player in the channel
    # We need to create a fake interaction for the player
    # Instead, we'll send a message in the channel
    embed = discord.Embed(
        title=f"🎭 {adventure['name']}",
        description=f"{player.mention}, a new adventure begins!",
        color=discord.Color.purple()
    )
    
    node = adventure['nodes'][start_node]
    embed.add_field(name="Story", value=node['text'], inline=False)
    
    view = AdventureView(adventure_id, start_node, str(player.id))
    
    await interaction.channel.send(embed=embed, view=view)


@bot.tree.command(name="reload_adventures", description="[GM] Reload adventure scenarios from file")
@is_gm()
async def reload_adventures(interaction: discord.Interaction):
    """Reload adventures from the YAML file."""
    load_adventures()
    count = len(adventures.get('adventures', {}))
    await interaction.response.send_message(
        f"✅ Reloaded {count} adventure(s) from adventures.yaml",
        ephemeral=True
    )


@bot.tree.command(name="help", description="Show all available commands")
async def help_command(interaction: discord.Interaction):
    """Show help information."""
    embed = discord.Embed(
        title="🎭 Adventure Bot - Help",
        description="Choose-your-own-adventure quicktime events for your westmarches campaign!",
        color=discord.Color.purple()
    )
    
    embed.add_field(
        name="📖 Player Commands",
        value=(
            "`/adventure <name>` - Start an adventure\n"
            "`/adventure_list` - View all available adventures"
        ),
        inline=False
    )
    
    embed.add_field(
        name="🎲 GM Commands",
        value=(
            "`/start_adventure <player> <name>` - Start an adventure for a specific player\n"
            "`/reload_adventures` - Reload adventures from adventures.yaml file"
        ),
        inline=False
    )
    
    embed.add_field(
        name="⚙️ Configuration",
        value=(
            "Adventures are configured in `adventures.yaml`\n"
            "Edit this file to create custom adventures with:\n"
            "• Story prompts and choices\n"
            "• Multiple decision paths\n"
            "• Rewards (gold, XP, items)\n"
            "• Penalties for bad choices\n"
            "• Requirements (e.g., need gold to bribe)"
        ),
        inline=False
    )
    
    await interaction.response.send_message(embed=embed)


# Run the bot
if __name__ == '__main__':
    if not TOKEN:
        print("Error: ADVENTURE_BOT_TOKEN not found in environment variables!")
        print("Please add ADVENTURE_BOT_TOKEN to your .env file.")
        exit(1)
    
    bot.run(TOKEN)
