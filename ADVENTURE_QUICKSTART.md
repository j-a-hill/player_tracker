# Adventure Bot Quick Start

## What is it?

The Adventure Bot provides choose-your-own-adventure style quicktime events for players in your westmarches campaign. Perfect for players who aren't actively in sessions but want to participate in solo adventures that can reward or penalize them with gold, items, or XP.

## Quick Setup

1. **Get a Discord Bot Token**
   - Go to https://discord.com/developers/applications
   - Create a new application for the Adventure Bot
   - Add a bot and copy the token
   - Enable MESSAGE CONTENT INTENT and SERVER MEMBERS INTENT

2. **Add to .env file**
   ```
   ADVENTURE_BOT_TOKEN=your_adventure_bot_token_here
   ```

3. **Invite to Discord**
   ```
   https://discord.com/api/oauth2/authorize?client_id=YOUR_CLIENT_ID&permissions=2048&scope=bot%20applications.commands
   ```

4. **Run the bot**
   ```bash
   python adventure_bot.py
   ```

## Usage

### For Players

**Start an adventure:**
```
/adventure The Mysterious Stranger
```

**See all available adventures:**
```
/adventure_list
```

Players interact using Discord buttons - no typing required!

### For GMs

**Start adventure for a player:**
```
/start_adventure @PlayerName Goblin Ambush
```

**Reload adventures after editing YAML:**
```
/reload_adventures
```

## Creating Adventures

Edit `adventures.yaml` to add your own adventures. Here's a simple example:

```yaml
adventures:
  my_adventure:
    name: My Custom Adventure
    description: A short description
    start_node: intro
    nodes:
      intro:
        text: "You find a mysterious box. What do you do?"
        choices:
          - label: "Open it"
            emoji: "📦"
            next: open_box
          - label: "Leave it"
            emoji: "🚶"
            next: leave
      
      open_box:
        text: "Inside you find 50 gold pieces!"
        rewards:
          gold: 50
        is_end: true
      
      leave:
        text: "You walk away. Was there treasure inside? You'll never know."
        is_end: true
```

## Features

- **Button-based choices** - Players click buttons, no typing
- **Branching paths** - Create complex decision trees
- **Requirements** - Lock choices behind gold/item requirements
- **Rewards** - Give gold, XP, or items
- **Penalties** - Take gold, XP, or items
- **Easy configuration** - YAML file, no coding needed!

## Example Adventures Included

1. **The Mysterious Stranger** - A cloaked figure with a letter
2. **Goblin Ambush** - Combat or negotiation on the road
3. **The Lost Child** - A moral dilemma in the woods
4. **The Suspicious Deal** - A merchant's mysterious offer
5. **The Dragon Egg** - Discover a dragon egg in a cave

See `ADVENTURE_GUIDE.md` for detailed documentation on creating complex adventures.

## Tips

- Keep adventures short (2-5 nodes)
- Make all choices interesting, not just "right vs wrong"
- Balance rewards (10-100 gold, 25-200 XP for most adventures)
- Test your adventures with `/adventure` before using with players
- Use `/reload_adventures` after editing adventures.yaml

## Troubleshooting

**Adventure not showing:**
- Check YAML syntax (use a YAML validator)
- Run `/reload_adventures`
- Check for typos in adventure names

**Buttons not working:**
- Verify all `next:` nodes exist
- Check for typos in node IDs

**Rewards not applying:**
- Check spelling: `rewards:` and `penalties:`
- Ensure `is_end: true` is set on final nodes
- Check Google Sheets to verify changes
