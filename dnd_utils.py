"""
Utility functions for D&D 5e game mechanics.
Includes XP thresholds, level calculations, and currency conversions.
"""

# D&D 5e XP thresholds for character levels 1-20
XP_THRESHOLDS = {
    1: 0,
    2: 300,
    3: 900,
    4: 2700,
    5: 6500,
    6: 14000,
    7: 23000,
    8: 34000,
    9: 48000,
    10: 64000,
    11: 85000,
    12: 100000,
    13: 120000,
    14: 140000,
    15: 165000,
    16: 195000,
    17: 225000,
    18: 265000,
    19: 305000,
    20: 355000
}

# Currency conversion rates (in copper pieces)
# Removed pp (platinum) and ep (electrum) per requirements
CURRENCY_VALUES = {
    'cp': 1,      # Copper
    'sp': 10,     # Silver
    'gp': 100,    # Gold
}


def get_level_from_xp(xp: int) -> int:
    """
    Calculate character level from session count.
    Level n requires sum(1..n-1) sessions.
    
    Args:
        xp: Current session count
        
    Returns:
        Character level (1-20)
    """
    # L * (L - 1) / 2 <= xp
    # 0 = 1, 1 = 2, 3 = 3, 6 = 4, 10 = 5...
    level = 1
    for lvl in range(20, 0, -1):
        if xp >= (lvl * (lvl - 1)) // 2:
            level = lvl
            break
    return level


def get_xp_for_level(level: int) -> int:
    """
    Get session threshold for a specific level.
    
    Args:
        level: Character level (1-20)
        
    Returns:
        Sessions required for that level
    """
    level = min(max(level, 1), 20)
    return (level * (level - 1)) // 2


def get_xp_progress(xp: int) -> tuple:
    """
    Get XP progress information for current level.
    
    Args:
        xp: Current experience points
        
    Returns:
        Tuple of (current_level, current_xp, next_level_xp, progress_percentage)
    """
    current_level = get_level_from_xp(xp)
    current_level_xp = get_xp_for_level(current_level)
    
    if current_level >= 20:
        # Max level reached
        return (20, xp, xp, 100.0, 0)
    
    next_level_xp = get_xp_for_level(current_level + 1)
    xp_into_level = xp - current_level_xp
    xp_needed_for_next = next_level_xp - current_level_xp
    progress = (xp_into_level / xp_needed_for_next) * 100 if xp_needed_for_next > 0 else 0
    
    return (current_level, current_level_xp, next_level_xp, progress, xp_needed_for_next - xp_into_level)


def format_currency(total_copper: int = 0) -> str:
    """
    Format currency from total copper into a readable string.
    Converts to highest denominations first (gold, silver, copper).
    
    Args:
        total_copper: Total value in copper pieces
        
    Returns:
        Formatted currency string (e.g., "5 gp, 3 sp, 7 cp")
    """
    if total_copper <= 0:
        return "0 cp"
    
    parts = []
    remaining = total_copper
    
    # Convert to gold pieces (100 cp = 1 gp)
    if remaining >= 100:
        gp = remaining // 100
        parts.append(f"{gp} gp")
        remaining = remaining % 100
    
    # Convert to silver pieces (10 cp = 1 sp)
    if remaining >= 10:
        sp = remaining // 10
        parts.append(f"{sp} sp")
        remaining = remaining % 10
    
    # Remaining copper pieces
    if remaining > 0:
        parts.append(f"{remaining} cp")
    
    return ", ".join(parts)


def convert_to_copper(cp=0, sp=0, gp=0) -> int:
    """
    Convert currency to copper pieces.
    
    Args:
        cp: Copper pieces
        sp: Silver pieces
        gp: Gold pieces
        
    Returns:
        Total value in copper pieces
    """
    total = 0
    total += cp * CURRENCY_VALUES['cp']
    total += sp * CURRENCY_VALUES['sp']
    total += gp * CURRENCY_VALUES['gp']
    return total


def parse_currency_input(amount: int, currency_type: str) -> int:
    """
    Convert a currency amount and type to copper pieces.
    
    Args:
        amount: Amount of currency
        currency_type: Type of currency (cp, sp, or gp)
        
    Returns:
        Total value in copper pieces
    """
    if currency_type not in CURRENCY_VALUES:
        valid_types = ', '.join(CURRENCY_VALUES.keys())
        raise ValueError(f"Invalid currency type '{currency_type}'. Valid types are: {valid_types}")
    
    return amount * CURRENCY_VALUES[currency_type]


def create_progress_bar(percentage: float, length: int = 10) -> str:
    """
    Create a visual progress bar.
    
    Args:
        percentage: Progress as percentage (0-100)
        length: Length of the progress bar in characters
        
    Returns:
        Progress bar string
    """
    filled = int((percentage / 100) * length)
    bar = "█" * filled + "░" * (length - filled)
    return f"[{bar}] {percentage:.1f}%"
