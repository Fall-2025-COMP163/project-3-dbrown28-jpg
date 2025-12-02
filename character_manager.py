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
    InvalidSaveDataError,
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
MAX_INVENTORY_SIZE = 20
LEVEL_UP_XP = 100  # XP required for level 1 -> 2 (example)

# ====================================================================
# CHARACTER CREATION AND STORAGE
# ====================================================================

def create_character(name, char_class):
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
    filepath = os.path.join(CHARACTER_SAVE_DIR, f"{char['name']}.json")
    try:
        with open(filepath, "w") as f:
            json.dump(char, f)
        return True
    except Exception:
        raise SaveFileCorruptedError(f"Failed to save character '{char['name']}'")

def load_character(name):
    filepath = os.path.join(CHARACTER_SAVE_DIR, f"{name}.json")
    if not os.path.exists(filepath):
        raise CharacterNotFoundError(f"Character '{name}' not found")
    try:
        with open(filepath, "r") as f:
            char = json.load(f)
        if "name" not in char or "class" not in char:
            raise InvalidSaveDataError(f"Save data for '{name}' is invalid")
        return char
    except json.JSONDecodeError:
        raise SaveFileCorruptedError(f"Save file for '{name}' is corrupted")
    except Exception as e:
        raise InvalidSaveDataError(str(e))

def delete_character(name):
    filepath = os.path.join(CHARACTER_SAVE_DIR, f"{name}.json")
    if os.path.exists(filepath):
        os.remove(filepath)
        return True
    return False

# ====================================================================
# EXPERIENCE AND LEVELING
# ====================================================================

def gain_experience(char, xp):
    if char["health"] <= 0:
        raise CharacterDeadError(f"{char['name']} is dead and cannot gain experience")
    char["experience"] += xp
    while char["experience"] >= LEVEL_UP_XP * char["level"]:
        char["experience"] -= LEVEL_UP_XP * char["level"]
        char["level"] += 1
        char["max_health"] += 10
        char["health"] = char["max_health"]

def heal_character(char, amount):
    if char["health"] <= 0:
        raise CharacterDeadError(f"{char['name']} is dead and cannot be healed")
    char["health"] = min(char["health"] + amount, char["max_health"])

# ====================================================================
# INVENTORY MANAGEMENT
# ====================================================================

def add_item_to_inventory(char, item_name):
    if 'inventory' not in char:
        char['inventory'] = []
    if len(char['inventory']) >= MAX_INVENTORY_SIZE:
        raise InventoryFullError("Inventory is full")
    char['inventory'].append(item_name)
    return True

def remove_item_from_inventory(char, item_name):
    if 'inventory' not in char or item_name not in char['inventory']:
        raise ItemNotFoundError(f"Item '{item_name}' not found in inventory")
    char['inventory'].remove(item_name)
    return True

# ====================================================================
# ITEM USAGE
# ====================================================================

def use_item(char, item_name, item_data):
    if 'inventory' not in char or item_name not in char['inventory']:
        raise ItemNotFoundError(f"Item '{item_name}' not in inventory")
    if item_data['type'] != 'consumable':
        raise InvalidItemTypeError(f"Cannot use item type '{item_data['type']}'")

    effect = item_data.get('effect', '')
    if effect.startswith('health:'):
        heal_amount = int(effect.split(':')[1])
        char['health'] = min(char['health'] + heal_amount, char.get('max_health', 100))

    char['inventory'].remove(item_name)
    return True

# ====================================================================
# EQUIPMENT
# ====================================================================

def equip_weapon(char, item_name, item_data):
    if 'inventory' not in char or item_name not in char['inventory']:
        raise ItemNotFoundError(f"Weapon '{item_name}' not in inventory")
    if item_data['type'] != 'weapon':
        raise InvalidItemTypeError(f"Cannot equip item type '{item_data['type']}'")

    char['equipped_weapon'] = item_name
    effect = item_data.get('effect', '')
    if effect.startswith('strength:'):
        char['strength'] = char.get('strength', 10) + int(effect.split(':')[1])

def equip_armor(char, item_name, item_data):
    if 'inventory' not in char or item_name not in char['inventory']:
        raise ItemNotFoundError(f"Armor '{item_name}' not in inventory")
    if item_data['type'] != 'armor':
        raise InvalidItemTypeError(f"Cannot equip item type '{item_data['type']}'")

    char['equipped_armor'] = item_name
    effect = item_data.get('effect', '')
    if effect.startswith('defense:'):
        char['defense'] = char.get('defense', 5) + int(effect.split(':')[1])

# ====================================================================
# SHOP OPERATIONS
# ====================================================================

def purchase_item(char, item_name, item_data):
    if char.get('gold', 0) < item_data.get('cost', 0):
        raise InsufficientResourcesError("Not enough gold to purchase item")
    add_item_to_inventory(char, item_name)
    char['gold'] -= item_data.get('cost', 0)
    return True

def sell_item(char, item_name, item_data):
    if 'inventory' not in char or item_name not in char['inventory']:
        raise ItemNotFoundError(f"Cannot sell '{item_name}', not in inventory")
    remove_item_from_inventory(char, item_name)
    gold_received = item_data.get('cost', 0) // 2
    char['gold'] = char.get('gold', 0) + gold_received
    return gold_received

# ====================================================================
# GOLD MANAGEMENT
# ====================================================================

def add_gold(char, amount):
    if char.get("gold", 0) + amount < 0:
        raise InsufficientResourcesError(f"{char['name']} does not have enough gold")
    char["gold"] += amount

