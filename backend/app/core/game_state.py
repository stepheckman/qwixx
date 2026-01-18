"""
Game state enumeration for the Qwixx game.
"""

from enum import Enum

class GameState(Enum):
    """Enumeration for different game states."""
    SETUP = "setup"
    WAITING_FOR_ROLL = "waiting_for_roll"
    DICE_ROLLED = "dice_rolled"
    STAGE_1_MOVES = "stage_1_moves"  # All players can mark white dice sum
    STAGE_2_MOVES = "stage_2_moves"  # Only rolling player can mark white + colored
    WAITING_FOR_MOVES = "waiting_for_moves"  # Legacy state, keeping for compatibility
    GAME_OVER = "game_over"