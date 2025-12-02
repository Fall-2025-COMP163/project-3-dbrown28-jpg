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
from custom_exceptions import (
    InvalidCharacterClassError,
    CharacterNotFoundError,
    SaveFileCorruptedError,
    InvalidSaveDataError,
    CharacterDeadError
)

# ============================================================================
# CHARACTER MANAGEMENT FUNCTIONS
# ============================================================================

def create_character(name, character_class):
    """
    Create a new character with stats based on class.
    
    Valid classes: Warrior, Mage, Rogue, Cleric.
    If an invalid class is given, raise InvalidCharacterClassError.

    All characters begin with:
      - level = 1
      - experience = 0
      - gold = 100
      - empty inventory and quest lists

    Returns:
        A fully-formed character dictionary with all required fields.
    """
    
    # Base stats for each valid class.
    # This allows the game to be extended later simply by expanding this dictionary.
    valid_classes = {
        "Warrior": {"health": 120, "strength": 15, "magic": 5},
        "Mage":    {"health": 80,  "strength": 8,  "magic": 20},
        "Rogue":   {"health": 90,  "strength": 12, "magic": 10},
        "Cleric":  {"health": 100, "strength": 10, "magic": 15},
    }

    # Check if the class exists; otherwise throw the required custom exception.
    if character_class not in valid_classes:
        raise InvalidCharacterClassError(f"Invalid class: {character_class}")

    # Extract base stats.
    base = valid_classes[character_class]

    # Construct the character dictionary.
    # This structure is used by the save/load system, combat, quests, etc.
    return {
        "name": name,
        "class": character_class,
        "level": 1,
        "health": base["health"],
        "max_health": base["health"],
        "strength": base["strength"],
        "magic": base["magic"],
        "experience": 0,
        "gold": 100,
        "inventory": [],
        "active_quests": [],
        "completed_quests": []
    }


def save_character(character, save_directory="data/save_games"):
    """
    Save the character to a human-readable text file.

    File format uses KEY: VALUE pairs so it is easy to read and debug.
    Lists are stored as comma-separated strings (e.g., "potion,sword").

    Raises:
        PermissionError, IOError – we do not catch these so tests can verify.
    """
    
    # Ensure the directory exists (creates it if missing).
    os.makedirs(save_directory, exist_ok=True)
    
    # Build filename: e.g., "Aragon_save.txt"
    filename = os.path.join(save_directory, f"{character['name']}_save.txt")

    # Write each field in a fixed format so loading is predictable.
    with open(filename, "w") as file:
        file.write(f"NAME: {character['name']}\n")
        file.write(f"CLASS: {character['class']}\n")
        file.write(f"LEVEL: {character['level']}\n")
        file.write(f"HEALTH: {character['health']}\n")
        file.write(f"MAX_HEALTH: {character['max_health']}\n")
        file.write(f"STRENGTH: {character['strength']}\n")
        file.write(f"MAGIC: {character['magic']}\n")
        file.write(f"EXPERIENCE: {character['experience']}\n")
        file.write(f"GOLD: {character['gold']}\n")

        # Convert lists into comma-separated strings.
        file.write(f"INVENTORY: {','.join(character['inventory'])}\n")
        file.write(f"ACTIVE_QUESTS: {','.join(character['active_quests'])}\n")
        file.write(f"COMPLETED_QUESTS: {','.join(character['completed_quests'])}\n")

    return True


def load_character(character_name, save_directory="data/save_games"):
    """
    Load a character from disk and reconstruct the dictionary.

    Raises:
        CharacterNotFoundError – no save file exists.
        SaveFileCorruptedError – file exists but cannot be read.
        InvalidSaveDataError – format does not match required structure.
    """
    
    filename = os.path.join(save_directory, f"{character_name}_save.txt")

    # Step 1: Check file existence
    if not os.path.exists(filename):
        raise CharacterNotFoundError(f"No save file for {character_name}")

    # Step 2: Attempt to read file
    try:
        with open(filename, "r") as file:
            lines = file.readlines()
    except:
        raise SaveFileCorruptedError("Unable to read save file.")

    # Step 3: Parse KEY: VALUE format
    data = {}
    try:
        for line in lines:
            if ":" not in line:
                raise InvalidSaveDataError("Malformed line in save file.")
            
            key, value = line.strip().split(":", 1)
            data[key.strip()] = value.strip()

        # Step 4: Convert strings back into appropriate Python types
        character = {
            "name": data["NAME"],
            "class": data["CLASS"],
            "level": int(data["LEVEL"]),
            "health": int(data["HEALTH"]),
            "max_health": int(data["MAX_HEALTH"]),
            "strength": int(data["STRENGTH"]),
            "magic": int(data["MAGIC"]),
            "experience": int(data["EXPERIENCE"]),
            "gold": int(data["GOLD"]),

            # Convert comma-separated strings back to lists.
            "inventory": data["INVENTORY"].split(",") if data["INVENTORY"] else [],
            "active_quests": data["ACTIVE_QUESTS"].split(",") if data["ACTIVE_QUESTS"] else [],
            "completed_quests": data["COMPLETED_QUESTS"].split(",") if data["COMPLETED_QUESTS"] else []
        }

        # Step 5: Validate structure before returning it.
        validate_character_data(character)

        return character

    except KeyError:
        raise InvalidSaveDataError("Save file missing required fields.")
    except ValueError:
        raise InvalidSaveDataError("Invalid numeric conversion in save file.")


def list_saved_characters(save_directory="data/save_games"):
    """
    Return a list of character names that have save files.

    Example:
        ["Aragon", "Luna", "Shadow"]
    """
    
    # If the directory doesn't exist, there are no saves.
    if not os.path.exists(save_directory):
        return []

    names = []
    for filename in os.listdir(save_directory):
        if filename.endswith("_save.txt"):
            names.append(filename.replace("_save.txt", ""))

    return names


def delete_character(character_name, save_directory="data/save_games"):
    """
    Delete a character save file permanently.

    Raises:
        CharacterNotFoundError if the save file does not exist.
    """
    
    filepath = os.path.join(save_directory, f"{character_name}_save.txt")

    if not os.path.exists(filepath):
        raise CharacterNotFoundError(f"No save file for {character_name}")

    os.remove(filepath)
    return True

# ============================================================================
# CHARACTER OPERATIONS (XP, GOLD, DEATH, HEALING)
# ============================================================================

def gain_experience(character, xp_amount):
    """
    Add XP to character and handle leveling up.

    Leveling rule:
        Required XP = current_level * 100

    When a character levels up:
        - level increases by 1
        - max_health increases by 10
        - strength increases by 2
        - magic increases by 2
        - health restored to max_health

    Can level up multiple times if a large XP amount is added at once.

    Raises:
        CharacterDeadError – cannot gain XP if health is 0.
    """
    
    if is_character_dead(character):
        raise CharacterDeadError("A dead character cannot gain XP.")

    character["experience"] += xp_amount

    # Continue leveling up as long as XP threshold is met.
    while character["experience"] >= character["level"] * 100:
        cost = character["level"] * 100
        character["experience"] -= cost

        # Level up and increase stats.
        character["level"] += 1
        character["max_health"] += 10
        character["strength"] += 2
        character["magic"] += 2

        # Restore HP to full when leveling up.
        character["health"] = character["max_health"]

    return character["level"]


def add_gold(character, amount):
    """
    Add or subtract gold from the character.

    amount may be negative when spending gold.

    Raises:
        ValueError – if result would be negative.
    """
    
    new_total = character["gold"] + amount

    if new_total < 0:
        raise ValueError("Cannot have negative gold.")

    character["gold"] = new_total
    return character["gold"]


def heal_character(character, amount):
    """
    Heal a character but do not exceed max_health.

    Returns:
        The ACTUAL amount healed (useful for UI or logs).
    """
    
    before = character["health"]
    character["health"] = min(character["health"] + amount, character["max_health"])
    return character["health"] - before


def is_character_dead(character):
    """
    A character is dead if health is 0 or less.
    """
    return character["health"] <= 0


def revive_character(character):
    """
    Revive a dead character with 50% max_health.

    Returns:
        True if character was revived, False if character
        was already alive.
    """
    
    if not is_character_dead(character):
        return False

    character["health"] = character["max_health"] // 2
    return True

# ============================================================================
# VALIDATION
# ============================================================================

def validate_character_data(character):
    """
    Ensures that a loaded or created character dictionary contains
    ALL required fields and that those fields have the correct types.

    Raises:
        InvalidSaveDataError if any fields are missing or incorrectly typed.
    """
    
    # Expected keys for a valid character.
    required = [
        "name", "class", "level", "health", "max_health",
        "strength", "magic", "experience", "gold",
        "inventory", "active_quests", "completed_quests"
    ]

    # Check that all required keys exist.
    for key in required:
        if key not in character:
            raise InvalidSaveDataError(f"Missing field: {key}")

    # Numeric fields must be integers.
    numeric = ["level", "health", "max_health", "strength", "magic", "experience", "gold"]
    for key in numeric:
        if not isinstance(character[key], int):
            raise InvalidSaveDataError(f"Field {key} must be an integer.")

    # List fields must be lists.
    list_fields = ["inventory", "active_quests", "completed_quests"]
    for key in list_fields:
        if not isinstance(character[key], list):
            raise InvalidSaveDataError(f"Field {key} must be a list.")

    return True

# ============================================================================
# OPTIONAL TEST DRIVER
# ============================================================================

if __name__ == "__main__":
    print("=== CHARACTER MANAGER SELF-TEST ===")
    try:
        char = create_character("TestHero", "Warrior")
        print("Created:", char)
    except Exception as e:
        print("Error:", e)
