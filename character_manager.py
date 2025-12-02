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

"""
COMP 163 - Project 3: Quest Chronicles
Inventory System Module

Handles inventory management, item usage, equipment, purchasing, and selling.
"""

from custom_exceptions import (
    InventoryFullError,
    ItemNotFoundError,
    InsufficientResourcesError,
    InvalidItemTypeError
)

# Maximum number of items a character can hold
MAX_INVENTORY_SIZE = 20

# ============================================================================ 
# BASIC INVENTORY OPERATIONS
# ============================================================================

def add_item_to_inventory(char, item_name):
    """Add an item to the character's inventory"""
    if 'inventory' not in char:
        char['inventory'] = []

    if len(char['inventory']) >= MAX_INVENTORY_SIZE:
        raise InventoryFullError("Inventory is full")
    
    char['inventory'].append(item_name)
    return True

def remove_item_from_inventory(char, item_name):
    """Remove an item from inventory"""
    if 'inventory' not in char or item_name not in char['inventory']:
        raise ItemNotFoundError(f"Item '{item_name}' not found in inventory")
    
    char['inventory'].remove(item_name)
    return True

# ============================================================================ 
# ITEM USAGE
# ============================================================================

def use_item(char, item_name, item_data):
    """
    Use a consumable item from inventory.
    Raises InvalidItemTypeError if item type is not consumable.
    """
    if 'inventory' not in char or item_name not in char['inventory']:
        raise ItemNotFoundError(f"Item '{item_name}' not in inventory")
    
    if item_data['type'] != 'consumable':
        raise InvalidItemTypeError(f"Cannot use item type '{item_data['type']}'")

    # Apply item effect
    effect = item_data.get('effect', '')
    if effect.startswith('health:'):
        heal_amount = int(effect.split(':')[1])
        char['health'] = min(char['health'] + heal_amount, char.get('max_health', 100))
    
    # Remove used item
    char['inventory'].remove(item_name)
    return True

# ============================================================================ 
# EQUIPMENT
# ============================================================================

def equip_weapon(char, item_name, item_data):
    """Equip a weapon and apply its effect"""
    if 'inventory' not in char or item_name not in char['inventory']:
        raise ItemNotFoundError(f"Weapon '{item_name}' not in inventory")
    
    if item_data['type'] != 'weapon':
        raise InvalidItemTypeError(f"Cannot equip item type '{item_data['type']}'")
    
    char['equipped_weapon'] = item_name
    # Apply weapon effect (e.g., strength:5)
    effect = item_data.get('effect', '')
    if effect.startswith('strength:'):
        char['strength'] = char.get('strength', 10) + int(effect.split(':')[1])

def equip_armor(char, item_name, item_data):
    """Equip armor and apply its effect"""
    if 'inventory' not in char or item_name not in char['inventory']:
        raise ItemNotFoundError(f"Armor '{item_name}' not in inventory")
    
    if item_data['type'] != 'armor':
        raise InvalidItemTypeError(f"Cannot equip item type '{item_data['type']}'")
    
    char['equipped_armor'] = item_name
    # Apply armor effect (e.g., defense:5)
    effect = item_data.get('effect', '')
    if effect.startswith('defense:'):
        char['defense'] = char.get('defense', 5) + int(effect.split(':')[1])

# ============================================================================ 
# SHOP OPERATIONS
# ============================================================================

def purchase_item(char, item_name, item_data):
    """Purchase an item from shop"""
    if char.get('gold', 0) < item_data.get('cost', 0):
        raise InsufficientResourcesError("Not enough gold to purchase item")
    
    add_item_to_inventory(char, item_name)
    char['gold'] -= item_data.get('cost', 0)
    return True

def sell_item(char, item_name, item_data):
    """Sell an item, returns gold gained (50% of cost)"""
    if 'inventory' not in char or item_name not in char['inventory']:
        raise ItemNotFoundError(f"Cannot sell '{item_name}', not in inventory")
    
    remove_item_from_inventory(char, item_name)
    gold_received = item_data.get('cost', 0) // 2
    char['gold'] = char.get('gold', 0) + gold_received
    return gold_received
