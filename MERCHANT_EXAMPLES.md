# Merchant Bot Usage Examples

This file demonstrates how to use the merchant bot to create custom item lists for different scenarios.

## Multi-Currency Support

The merchant bot now supports all D&D 5e currency types:
- **cp** - Copper pieces
- **sp** - Silver pieces
- **ep** - Electrum pieces
- **gp** - Gold pieces (default)
- **pp** - Platinum pieces

## Basic Shop Setup

### 1. Starting Fresh
```
/clear_shop
```
This removes all items from the shop, allowing you to create a custom list from scratch.

### 2. Adding Items

**Unlimited Stock Items:**
```
/add_item name:"Health Potion" price:50 currency:gp description:"Restores 50 HP" stock:-1
/add_item name:"Mana Potion" price:40 currency:gp description:"Restores 30 MP" stock:-1
```

**Limited Stock Items:**
```
/add_item name:"Legendary Sword" price:1000 currency:gp description:"A rare and powerful weapon" stock:1
/add_item name:"Magic Scroll" price:200 currency:gp description:"Teaches a new spell" stock:3
```

**Items with Different Currency Types:**
```
/add_item name:"Torch" price:5 currency:cp description:"Basic light source" stock:20
/add_item name:"Rope" price:1 currency:sp description:"50 feet of rope" stock:10
/add_item name:"Healing Salve" price:5 currency:ep description:"Minor healing" stock:5
/add_item name:"Magic Wand" price:50 currency:pp description:"Rare magical item" stock:1
```

### 3. Viewing the Shop
```
/shop
```
Players can use this command to see all available items and their stock levels.

### 4. Buying Items

**Single Item:**
```
/buy Health Potion
```

**Multiple Items:**
```
/buy Health Potion quantity:5
```

## Example Scenarios

### Scenario 1: Starting Town General Store (Copper/Silver Items)
```
/clear_shop
/add_item name:"Torch" price:5 currency:cp description:"Provides light in dark places" stock:-1
/add_item name:"Rope (50ft)" price:10 currency:sp description:"Sturdy climbing rope" stock:-1
/add_item name:"Rations" price:5 currency:cp description:"Food for one day" stock:-1
/add_item name:"Bedroll" price:1 currency:sp description:"For a good night's rest" stock:-1
/add_item name:"Waterskin" price:5 currency:cp description:"Carries water" stock:-1
```

### Scenario 2: Magic Shop with Rare Items (Gold/Platinum)
```
/clear_shop
/add_item name:"Minor Healing Potion" price:25 currency:gp description:"Restores 25 HP" stock:10
/add_item name:"Scroll of Fireball" price:150 currency:gp description:"One-time use spell" stock:3
/add_item name:"Scroll of Teleport" price:300 currency:gp description:"One-time use spell" stock:1
/add_item name:"Wand of Magic Missiles" price:50 currency:pp description:"10 charges remaining" stock:2
/add_item name:"Ring of Protection" price:100 currency:pp description:"+1 AC bonus" stock:1
```

### Scenario 3: Blacksmith for Weapons and Armor (Gold)
```
/clear_shop
/add_item name:"Short Sword" price:100 currency:gp description:"1d6 damage" stock:5
/add_item name:"Longsword" price:150 currency:gp description:"1d8 damage" stock:3
/add_item name:"Greataxe" price:200 currency:gp description:"1d12 damage" stock:2
/add_item name:"Leather Armor" price:50 currency:gp description:"AC 11" stock:5
/add_item name:"Chain Mail" price:200 currency:gp description:"AC 16" stock:2
/add_item name:"Plate Armor" price:500 currency:gp description:"AC 18" stock:1
```

### Scenario 4: One-Time Event Shop (Mixed Currency)
```
/clear_shop
/add_item name:"Festival Mask" price:20 currency:cp description:"A colorful decorative mask" stock:10
/add_item name:"Sweet Treats" price:5 currency:cp description:"Delicious pastries" stock:20
/add_item name:"Lucky Charm" price:5 currency:sp description:"Supposedly brings good fortune" stock:5
/add_item name:"Fireworks" price:3 currency:gp description:"For celebration" stock:15
```

## Managing Stock

### Restocking Items
When items run low, use the restock command:
```
/restock Health Potion quantity:20
```

### Making Items Unlimited
```
/restock Torch quantity:-1
```

### Making Items Out of Stock
```
/restock "Legendary Sword" quantity:0
```

## Tips for GMs

1. **Plan Ahead**: Create themed shops for different locations (town, dungeon merchant, traveling vendor)
2. **Use Currency Types Strategically**:
   - Copper (cp): Very cheap items (torches, rations)
   - Silver (sp): Common items (rope, basic tools)
   - Electrum (ep): Uncommon items (minor potions)
   - Gold (gp): Standard magical items and equipment
   - Platinum (pp): Rare and legendary items
3. **Use Stock Wisely**: 
   - Common items: -1 (unlimited)
   - Uncommon items: 10-20
   - Rare items: 1-5
   - Unique items: 1
4. **Price Balance**: Consider your players' currency amounts (check with `/profile`)
5. **Clear Between Sessions**: Use `/clear_shop` to create location-specific shops
6. **Track Purchases**: Items automatically deduct from stock when purchased
7. **Update in Google Sheets**: You can also edit items directly in the Shop worksheet (columns: Item Name, Price, Currency, Description, Stock)

## Player Commands

Players have access to these commands:

### View Shop
```
/shop
```
Shows all items with prices and stock levels.

### Buy Items
```
/buy <item name>
/buy <item name> quantity:<number>
```
Examples:
- `/buy Health Potion` - Buy 1
- `/buy Health Potion quantity:5` - Buy 5

The bot will:
- Check if the player has enough gold
- Check if enough stock is available
- Deduct gold from player
- Add items to player inventory
- Reduce stock automatically
