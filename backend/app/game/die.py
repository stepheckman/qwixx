"""
Die class for the Qwixx game.
"""

import random
from enum import Enum
from typing import Optional

class DieColor(Enum):
    """Enumeration for die colors."""
    WHITE = "white"
    RED = "red"
    YELLOW = "yellow"
    GREEN = "green"
    BLUE = "blue"

class Die:
    """Represents a single die in the Qwixx game."""
    
    def __init__(self, color: DieColor):
        """
        Initialize a die with a specific color.
        
        Args:
            color: The color of the die
        """
        self.color = color
        self.value: Optional[int] = None
    
    def roll(self) -> int:
        """
        Roll the die and return the result.
        
        Returns:
            The rolled value (1-6)
        """
        self.value = random.randint(1, 6)
        return self.value
    
    def get_value(self) -> Optional[int]:
        """
        Get the current value of the die.
        
        Returns:
            The current die value, or None if not rolled yet
        """
        return self.value
    
    def __str__(self) -> str:
        """String representation of the die."""
        return f"{self.color.value.capitalize()} die: {self.value if self.value else 'Not rolled'}"
    
    def __repr__(self) -> str:
        """Detailed string representation of the die."""
        return f"Die(color={self.color}, value={self.value})"