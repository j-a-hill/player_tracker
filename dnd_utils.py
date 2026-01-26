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
CURRENCY_VALUES = {
    'cp': 1,      # Copper
    'sp': 10,     # Silver
    'ep': 50,     # Electrum
    'gp': 100,    # Gold
    'pp': 1000    # Platinum
}


def get_level_from_xp(xp: int) -> int:
    """
    Calculate character level from XP.
    
    Args:
        xp: Current experience points
        
    Returns:
        Character level (1-20)
    """
    level = 1
    for lvl in range(20, 0, -1):
        if xp >= XP_THRESHOLDS[lvl]:
            level = lvl
            break
    return level


def get_xp_for_level(level: int) -> int:
    """
    Get XP threshold for a specific level.
    
    Args:
        level: Character level (1-20)
        
    Returns:
        XP required for that level
    """
    return XP_THRESHOLDS.get(min(max(level, 1), 20), 0)


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
        return (20, xp, xp, 100.0)
    
    next_level_xp = get_xp_for_level(current_level + 1)
    xp_into_level = xp - current_level_xp
    xp_needed_for_next = next_level_xp - current_level_xp
    progress = (xp_into_level / xp_needed_for_next) * 100 if xp_needed_for_next > 0 else 0
    
    return (current_level, current_level_xp, next_level_xp, progress)


def format_currency(cp=0, sp=0, ep=0, gp=0, pp=0) -> str:
    """
    Format currency into a readable string.
    
    Args:
        cp: Copper pieces
        sp: Silver pieces
        ep: Electrum pieces
        gp: Gold pieces
        pp: Platinum pieces
        
    Returns:
        Formatted currency string
    """
    parts = []
    if pp > 0:
        parts.append(f"{pp} pp")
    if gp > 0:
        parts.append(f"{gp} gp")
    if ep > 0:
        parts.append(f"{ep} ep")
    if sp > 0:
        parts.append(f"{sp} sp")
    if cp > 0:
        parts.append(f"{cp} cp")
    
    return ", ".join(parts) if parts else "0 gp"


def convert_to_copper(cp=0, sp=0, ep=0, gp=0, pp=0) -> int:
    """
    Convert all currency to copper pieces.
    
    Args:
        cp: Copper pieces
        sp: Silver pieces
        ep: Electrum pieces
        gp: Gold pieces
        pp: Platinum pieces
        
    Returns:
        Total value in copper pieces
    """
    total = 0
    total += cp * CURRENCY_VALUES['cp']
    total += sp * CURRENCY_VALUES['sp']
    total += ep * CURRENCY_VALUES['ep']
    total += gp * CURRENCY_VALUES['gp']
    total += pp * CURRENCY_VALUES['pp']
    return total


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
