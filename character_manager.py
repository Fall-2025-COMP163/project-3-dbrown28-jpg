"""
COMP 163 - Project 3: Quest Chronicles
Character Manager Module - Final Implementation

Name: [Dion Brown]

AI Usage:
ChatGPT assisted in generating function implementations and expanding
documentation. All code was reviewed and understood by the student.

This module handles character creation, saving, loading, updating stats,
and validating character data structures.
"""

import os
import json

from custom_exceptions import (
    InvalidCharacterClassError,
    CharacterNotFoundError,
    CharacterDeadError,
    InsufficientLevelError,
    SaveFileCorruptedError,
    InvalidSaveDataError
)

from inventory_system import (
    add_item_to_inventory,
    remove_item_from_inventory,
    use_item,
    equip_weapon,
    equip_armor,
    purchase_item,
    sell_item,
    InventoryFullError,
    ItemNotFoundError,
    InsufficientResourcesError,
    InvalidItemTypeError
)

# ====================================================================
# CONFIGURATION
# ====================================================================
CHARACTER_SAVE_DIR = "data/save_games"
os.makedirs(CHARACTER_SAVE_DIR, exist_ok=True)

VALID_CLASSES = ["Warrior", "Mage", "Rogue", "Cleric"]
LEVEL_UP_XP = 100  # XP required per level (example)
MAX_INVENTORY_SIZE = 20  # Max items a character can hold

# ====================================================================
# CHARACTER CREATION AND STORAGE
# ====================================================================

def create_character(name, char_class):
    """Create a new character with default stats"""
    if char_class not in VALID_CLASSES:
        raise InvalidCharacterClassError(f"Invalid class '{char_class}'")
    
    char = {
        "name": name,
        "class": char_class,
        "level": 1,
        "experience": 0,
        "health": 100,
        "max_health": 100,
        "gold": 0,
        "inventory": [],
        "equipped_weapon": None,
        "equipped_armor": None,
        "active_quests": [],
        "completed_quests": [],
        "strength": 10,
        "defense": 5
    }
    return char

def save_character(char):
    """Save character to JSON file"""
    filepath = os.path.join(CHARACTER_SAVE_DIR, f"{char['name']}.json")
    try:
        with open(filepath, "w") as f:
            json.dump(char, f)
        return True
    except Exception:
        raise SaveFileCorruptedError(f"Failed to save character '{char['name']}'")

def load_character(name):
    """Load a character from JSON file"""
    filepath = os.path.join(CHARACTER_SAVE_DIR, f"{name}.json")
    if not os.path.exists(filepath):
        raise CharacterNotFoundError(f"Character '{name}' not found")
    try:
        with open(filepath, "r") as f:
            char = json.load(f)
        # Basic validation
        if "name" not in char or "class" not in char:
            raise InvalidSaveDataError(f"Save data for '{name}' is invalid")
        return char
    except json.JSONDecodeError:
        raise SaveFileCorruptedError(f"Save file for '{name}' is corrupted")
    except Exception as e:
        raise InvalidSaveDataError(str(e))

def delete_character(name):
    """Delete a character's save file"""
    filepath = os.path.join(CHARACTER_SAVE_DIR, f"{name}.json")
    if os.path.exists(filepath):
        os.remove(filepath)
        return True
    return False

# ====================================================================
# EXPERIENCE AND LEVELING
# ====================================================================

def gain_experience(char, xp):
    """Add experience and level up if threshold reached"""
    if char["health"] <= 0:
        raise CharacterDeadError(f"{char['name']} is dead and cannot gain experience")
    
    char["experience"] += xp
    while char["experience"] >= LEVEL_UP_XP * char["level"]:
        char["experience"] -= LEVEL_UP_XP * char["level"]
        char["level"] += 1
        char["max_health"] += 10  # Increase max health on level up
        char["health"] = char["max_health"]  # Restore health on level up

def heal_character(char, amount):
    """Heal character, cannot exceed max_health"""
    if char["health"] <= 0:
        raise CharacterDeadError(f"{char['name']} is dead and cannot be healed")
    char["health"] = min(char["health"] + amount, char["max_health"])

# ====================================================================
# GOLD MANAGEMENT
# ====================================================================

def add_gold(char, amount):
    """Add or subtract gold; cannot go below 0"""
    if char["gold"] + amount < 0:
        raise ValueError(f"{char['name']} does not have enough gold")
    char["gold"] += amount
    return char["gold"]
