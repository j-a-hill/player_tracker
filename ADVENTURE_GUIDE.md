# Adventure Bot Guide

The Adventure Bot provides choose-your-own-adventure style quicktime events for your westmarches campaign. Players who aren't actively playing can participate in solo adventures that may reward or penalize them with gold, items, or XP.

## Overview

The Adventure Bot allows you to:
- Create interactive story prompts with multiple choices
- Build branching decision trees with different outcomes
- Reward players with gold, XP, or items
- Apply penalties for bad decisions
- Set requirements (e.g., need gold to bribe, need items to help)
- Use buttons for an engaging player experience

## Player Commands

### `/adventure <name>`
Start an adventure by name. The adventure will present you with a story prompt and choices shown as buttons.

**Example:**
```
/adventure The Mysterious Stranger
```

### `/adventure_list`
View all available adventures with their descriptions.

## GM Commands

### `/start_adventure <player> <name>`
Start a specific adventure for a player. This is useful for triggering quicktime events for players who aren't online.

**Example:**
```
/start_adventure @PlayerName Goblin Ambush
```

### `/reload_adventures`
Reload all adventures from the `adventures.yaml` file. Use this after editing the YAML file to add or modify adventures.

## Creating Adventures

Adventures are defined in the `adventures.yaml` file. This allows you to easily create and modify adventures without changing code.

### Basic Structure

```yaml
adventures:
  adventure_id:  # Unique identifier (no spaces)
    name: Display Name
    description: Short description shown in the list
    start_node: intro  # Which node to start at
    nodes:
      intro:  # Node ID
        text: "Story text that describes the situation"
        choices:
          - label: "Choice 1"
            emoji: "🔮"  # Optional emoji
            next: node_id_1  # Which node to go to next
          - label: "Choice 2"
            emoji: "⚔️"
            next: node_id_2
      
      node_id_1:
        text: "Outcome of choice 1"
        is_end: true  # Marks this as an ending
```

### Rewards and Penalties

You can give or take gold, XP, and items from players:

```yaml
nodes:
  success:
    text: "You succeeded! Here's your reward."
    rewards:
      gold: 50  # Give 50 gold
      xp: 100   # Give 100 XP
      items:    # Give items
        - Magic Sword
        - Health Potion
    is_end: true
  
  failure:
    text: "You failed and lost some resources."
    penalties:
      gold: 25  # Take 25 gold
      xp: 50    # Take 50 XP
      items:    # Remove items
        - Torch
    is_end: true
```

### Requirements

You can require players to have certain resources to choose an option:

```yaml
choices:
  - label: "Bribe the guard (20 gp)"
    emoji: "💰"
    next: bribe_success
    requirement:
      gold: 20  # Player must have at least 20 gold
  
  - label: "Give them rations"
    emoji: "🍞"
    next: share_food
    requirement:
      items:
        - Rations  # Player must have rations
```

If a player doesn't meet the requirement, they'll see an error message and won't be able to choose that option.

### Complete Example

Here's a complete adventure example:

```yaml
adventures:
  cursed_amulet:
    name: The Cursed Amulet
    description: You find a mysterious amulet in ruins
    start_node: discovery
    nodes:
      discovery:
        text: "In the ancient ruins, you find a beautiful amulet glowing with an eerie light. Do you take it?"
        choices:
          - label: "Take the amulet"
            emoji: "💎"
            next: take_it
          - label: "Leave it alone"
            emoji: "🚶"
            next: leave_it
          - label: "Examine it carefully"
            emoji: "🔍"
            next: examine
      
      take_it:
        text: "As you touch the amulet, you feel dark magic surge through you. You've been cursed! You lose 50 XP, but the amulet might be valuable..."
        rewards:
          items:
            - Cursed Amulet
        penalties:
          xp: 50
        is_end: true
      
      leave_it:
        text: "You wisely decide not to mess with unknown magic. As you leave, the amulet crumbles to dust. You gain 75 XP for your caution."
        rewards:
          xp: 75
        is_end: true
      
      examine:
        text: "Your careful examination reveals the curse! You use your knowledge to safely extract the amulet's power, gaining a Pure Gem worth 100 gold and 150 XP!"
        rewards:
          gold: 100
          xp: 150
          items:
            - Pure Gem
        is_end: true
```

## Adventure Design Tips

### 1. Keep Stories Short
Quicktime events should be brief. Aim for 2-4 choices per node and 3-5 nodes total.

### 2. Make Choices Meaningful
Each choice should lead to a notably different outcome. Avoid "right/wrong" choices in favor of "interesting/also interesting".

### 3. Balance Rewards
- Small adventures: 10-50 gold, 25-100 XP, common items
- Medium adventures: 50-100 gold, 100-200 XP, uncommon items
- Large adventures: 100+ gold, 200+ XP, rare items

### 4. Use Requirements Wisely
Requirements create interesting choices but can lock out players. Consider:
- Always provide an alternative option
- Use moderate requirements (10-50 gold, common items)
- Reward players who meet requirements appropriately

### 5. Add Personality
Use emojis, vivid descriptions, and character voices to make adventures engaging.

### 6. Create Consequences
Not all choices should have rewards. Some should just be interesting story moments or minor setbacks.

## Adventure Categories

Here are some adventure types that work well for westmarches:

### Encounters
Random meetings with NPCs or creatures.
- The Mysterious Stranger
- Goblin Ambush
- Merchant Deal

### Discoveries
Finding something unusual.
- Dragon Egg
- Cursed Amulet
- Hidden Treasure

### Moral Dilemmas
Choices that test character alignment.
- The Lost Child
- Starving Thief
- Prisoner's Plea

### Skill Challenges
Tests of specific abilities or resources.
- Climbing Challenge
- Riddle Contest
- Negotiation

### Random Events
Unexpected situations.
- Weather Event
- Festival Games
- Lucky Find

## Testing Adventures

After creating a new adventure:

1. Add it to `adventures.yaml`
2. Use `/reload_adventures` to load it
3. Use `/adventure_list` to verify it appears
4. Use `/adventure <name>` to test it yourself
5. Try all paths to ensure rewards/penalties work correctly

## Troubleshooting

**Adventure not appearing:**
- Check YAML syntax (use a YAML validator)
- Ensure proper indentation (use spaces, not tabs)
- Run `/reload_adventures`

**Buttons not working:**
- Verify `next` nodes exist
- Check for typos in node IDs
- Ensure adventure has a `start_node`

**Requirements not working:**
- Check gold amounts (stored as copper internally)
- Verify item names match exactly (case-sensitive)
- Test with a player who has the required resources

**Rewards not applying:**
- Check spelling: `rewards`, `penalties`
- Verify `is_end: true` is set
- Check Google Sheets for actual values

## Integration with Other Bots

The Adventure Bot integrates seamlessly with the main Player Tracker bot:
- Reads/writes player gold from the same Google Sheet
- Reads/writes player XP (triggers level-ups via main bot)
- Reads/writes player inventory
- All changes are immediately visible across all bots

## Example Workflow

1. **GM creates adventure** in `adventures.yaml`
2. **GM reloads** with `/reload_adventures`
3. **Player starts** with `/adventure The Lost Child`
4. **Bot presents** story with button choices
5. **Player clicks** a button to choose
6. **Bot processes** the choice and shows next node
7. **Adventure ends** with rewards/penalties applied
8. **Player sees** updated gold/XP/inventory in their profile

## Advanced Features

### Multi-Path Stories

Create complex branching narratives:

```yaml
nodes:
  choice_a:
    text: "You chose path A..."
    choices:
      - label: "Option A1"
        next: a1_result
      - label: "Option A2"
        next: a2_result
  
  a1_result:
    text: "Result of A1..."
    choices:
      - label: "Continue"
        next: final_node
  
  a2_result:
    text: "Result of A2..."
    choices:
      - label: "Continue"
        next: final_node
  
  final_node:
    text: "Different paths lead to the same place."
    is_end: true
```

### Multiple Requirements

Combine different requirement types:

```yaml
choices:
  - label: "Use magic scroll and pay wizard (50gp)"
    next: ultimate_solution
    requirement:
      gold: 50
      items:
        - Magic Scroll
```

### Flavor Text Without Mechanics

Create story-only adventures for roleplay:

```yaml
nodes:
  story_moment:
    text: "You witness a beautiful sunset over the mountains. You feel at peace."
    is_end: true  # No rewards or penalties, just story
```

## Conclusion

The Adventure Bot provides a flexible, easy-to-configure system for adding solo adventures to your westmarches campaign. By editing the YAML file, you can create unlimited custom adventures tailored to your world and players.

Have fun creating adventures!
