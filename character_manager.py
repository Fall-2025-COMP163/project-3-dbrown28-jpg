"""
character_manager.py
---------------------

Handles:

- Creating characters
- Saving/loading characters from disk
- Managing XP/level-ups
- Managing gold
- Healing

This module is intentionally simple and dictionary-based
to match the integration tests exactly.
"""

import os
import json

from custom_exceptions import (
    InvalidCharacterClassError,
    CharacterNotFoundError,
    CharacterDeadError,
)

# Directory where characters are saved
SAVE_DIR = "data/save_games"

# Allowed character classes
ALLOWED_CLASSES = ["Warrior", "Mage", "Rogue", "Cleric"]


# ============================================================
# Utility: Ensure directory exists
# ============================================================

def _ensure_save_dir():
    """Creates the save directory if it doesn't already exist."""
    os.makedirs(SAVE_DIR, exist_ok=True)


# ============================================================
# CHARACTER CREATION
# ============================================================

def create_character(name: str, char_class: str) -> dict:
    """
    Creates a new character dictionary matching what the tests expect.

    Raises:
        InvalidCharacterClassError: If char_class isn't one of the allowed ones.
    """
    if char_class not in ALLOWED_CLASSES:
        raise InvalidCharacterClassError(f"Invalid class: {char_class}")

    character = {
        "name": name,
        "class": char_class,
        "level": 1,
        "experience": 0,
        "gold": 100,
        "inventory": [],
        "health": 100,
        "max_health": 100,
        "strength": 10,
        "active_quests": [],
        "completed_quests": [],
    }

    return character


# ============================================================
# CHARACTER SAVING / LOADING
# ============================================================

def save_character(character: dict) -> bool:
    """
    Saves a character as JSON.

    Returns:
        True if successful.
    """
    _ensure_save_dir()
    filepath = os.path.join(SAVE_DIR, f"{character['name']}.json")

    with open(filepath, "w") as f:
        json.dump(character, f, indent=4)

    return True


def load_character(name: str) -> dict:
    """
    Loads a character from disk.

    Raises:
        CharacterNotFoundError: if save file does not exist.
    """
    filepath = os.path.join(SAVE_DIR, f"{name}.json")

    if not os.path.exists(filepath):
        raise CharacterNotFoundError(f"Character '{name}' not found")

    with open(filepath, "r") as f:
        data = json.load(f)

    return data


def delete_character(name: str):
    """Deletes a character file. Used by tests for cleanup."""
    filepath = os.path.join(SAVE_DIR, f"{name}.json")
    if os.path.exists(filepath):
        os.remove(filepath)


# ============================================================
# XP / LEVELING
# ============================================================

def gain_experience(character: dict, amount: int):
    """
    Adds XP and auto-levels up if threshold is reached.

    Raises:
        CharacterDeadError – if character.health <= 0
    """
    if character["health"] <= 0:
        raise CharacterDeadError("Cannot gain XP while dead")

    character["experience"] += amount

    # Level-up threshold: 100 XP per level
    while character["experience"] >= 100:
        character["experience"] -= 100
        character["level"] += 1

        # Increase max health on level-up
        character["max_health"] += 20
        character["health"] = character["max_health"]  # Restore health fully


# ============================================================
# GOLD MANAGEMENT
# ============================================================

def add_gold(character: dict, amount: int):
    """
    Adds or subtracts gold.

    Tests expect:
        - Negative values allowed EXCEPT when resulting gold < 0
        - Raise ValueError if insufficient gold
    """
    if character["gold"] + amount < 0:
        raise ValueError("Not enough gold")

    character["gold"] += amount


# ============================================================
# HEALING
# ============================================================

def heal_character(character: dict, amount: int):
    """Restores health without exceeding max_health."""
    character["health"] = min(character["health"] + amount, character["max_health"])
