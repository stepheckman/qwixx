"""
Player class for the Qwixx game.
"""

from app.game.scoresheet import Scoresheet
from app.game.die import DieColor
from typing import Set, Optional

class Player:
    """Represents a player in the Qwixx game."""
    
    def __init__(self, name: str, player_id: int):
        """
        Initialize a player.
        
        Args:
            name: The player's name
            player_id: Unique identifier for the player
        """
        self.name = name
        self.player_id = player_id
        self.scoresheet = Scoresheet()
        self.is_active = False
        
        # Track moves made during current turn
        self.white_sum_moves_this_turn = 0  # All players can mark white sum (max 1)
        self.colored_combination_moves_this_turn = 0  # Active player only (max 1)
        self.total_moves_this_turn = 0  # Total moves this turn
    
    def get_name(self) -> str:
        """Get the player's name."""
        return self.name
    
    def get_id(self) -> int:
        """Get the player's ID."""
        return self.player_id
    
    def get_scoresheet(self) -> Scoresheet:
        """Get the player's scoresheet."""
        return self.scoresheet
    
    def set_active(self, active: bool) -> None:
        """Set whether this player is the active player."""
        self.is_active = active
    
    def is_active_player(self) -> bool:
        """Check if this is the active player."""
        return self.is_active
    
    def get_total_score(self) -> int:
        """Get the player's total score."""
        return self.scoresheet.calculate_total_score()
    
    def is_game_over(self) -> bool:
        """Check if the game is over for this player."""
        return self.scoresheet.is_game_over()
    
    def start_new_turn(self) -> None:
        """Reset turn tracking for a new turn."""
        self.white_sum_moves_this_turn = 0
        self.colored_combination_moves_this_turn = 0
        self.total_moves_this_turn = 0
    
    def record_white_sum_move(self) -> None:
        """Record that the player used the white sum this turn."""
        self.white_sum_moves_this_turn += 1
        self.total_moves_this_turn += 1
    
    def record_colored_combination_move(self) -> None:
        """Record that the player used a colored combination this turn."""
        self.colored_combination_moves_this_turn += 1
        self.total_moves_this_turn += 1
    
    def can_use_white_sum(self) -> bool:
        """Check if player can use white sum this turn."""
        # All players can mark white sum at most once per turn
        return self.white_sum_moves_this_turn < 1
    
    def can_use_colored_combination(self) -> bool:
        """Check if active player can use a colored combination this turn."""
        if not self.is_active:
            return False  # Only active player can use colored combinations
        
        # Active player can use colored combination only once per turn
        # and can have at most 2 total moves per turn
        return (self.colored_combination_moves_this_turn < 1 and
                self.total_moves_this_turn < 2)
    
    def __str__(self) -> str:
        """String representation of the player."""
        status = " (Active)" if self.is_active else ""
        return f"{self.name}{status} - Score: {self.get_total_score()}"
    
    def __repr__(self) -> str:
        """Detailed string representation of the player."""
        return f"Player(name='{self.name}', id={self.player_id}, score={self.get_total_score()})"