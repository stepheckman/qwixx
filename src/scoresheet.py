"""
Scoresheet class for the Qwixx game.
"""

from typing import Dict, List, Optional, Set
from .die import DieColor

class ColorRow:
    """Represents a single colored row on the scoresheet."""
    
    def __init__(self, color: DieColor, numbers: List[int]):
        """
        Initialize a color row.
        
        Args:
            color: The color of this row
            numbers: List of numbers in this row (e.g., [2,3,4,5,6,7,8,9,10,11,12] for red/yellow)
        """
        self.color = color
        self.numbers = numbers
        self.marked: Set[int] = set()
        self.is_locked = False
        self.rightmost_marked = -1  # Track the rightmost marked position for validation
    
    def can_mark(self, number: int) -> bool:
        """
        Check if a number can be marked in this row.
        
        Args:
            number: The number to check
            
        Returns:
            True if the number can be marked, False otherwise
        """
        if self.is_locked or number in self.marked or number not in self.numbers:
            return False
        
        # Find the position of this number
        try:
            position = self.numbers.index(number)
        except ValueError:
            return False
        
        # Can only mark if it's to the right of or at the rightmost marked position
        return position >= self.rightmost_marked
    
    def mark_number(self, number: int) -> bool:
        """
        Mark a number in this row.
        
        Args:
            number: The number to mark
            
        Returns:
            True if successfully marked, False otherwise
        """
        if not self.can_mark(number):
            return False
        
        self.marked.add(number)
        position = self.numbers.index(number)
        self.rightmost_marked = max(self.rightmost_marked, position)
        
        return True
    
    def can_lock(self) -> bool:
        """
        Check if this row can be locked.
        A row can be locked if:
        1. At least 5 numbers are marked
        2. The rightmost number (12 for red/yellow, 2 for green/blue) is marked
        
        Returns:
            True if the row can be locked, False otherwise
        """
        if len(self.marked) < 5:
            return False
        
        # Check if the rightmost number is marked
        rightmost_number = self.numbers[-1]
        return rightmost_number in self.marked
    
    def lock_row(self) -> bool:
        """
        Lock this row if possible.
        
        Returns:
            True if successfully locked, False otherwise
        """
        if not self.can_lock():
            return False
        
        self.is_locked = True
        return True
    
    def get_score(self) -> int:
        """
        Calculate the score for this row.
        Score is based on the number of marked numbers:
        1 mark = 1 point, 2 marks = 3 points, 3 marks = 6 points, etc.
        Formula: n * (n + 1) / 2
        
        Returns:
            The score for this row
        """
        n = len(self.marked)
        return n * (n + 1) // 2

class Scoresheet:
    """Represents a player's scoresheet in Qwixx."""
    
    def __init__(self):
        """Initialize a new scoresheet."""
        # Create the four colored rows
        self.rows: Dict[DieColor, ColorRow] = {
            DieColor.RED: ColorRow(DieColor.RED, list(range(2, 13))),      # 2-12
            DieColor.YELLOW: ColorRow(DieColor.YELLOW, list(range(2, 13))), # 2-12
            DieColor.GREEN: ColorRow(DieColor.GREEN, list(range(12, 1, -1))), # 12-2
            DieColor.BLUE: ColorRow(DieColor.BLUE, list(range(12, 1, -1)))   # 12-2
        }
        
        self.penalties = 0
        self.max_penalties = 4
    
    def can_mark_number(self, color: DieColor, number: int) -> bool:
        """
        Check if a number can be marked in the specified color row.
        
        Args:
            color: The color row to check
            number: The number to mark
            
        Returns:
            True if the number can be marked, False otherwise
        """
        if color not in self.rows:
            return False
        return self.rows[color].can_mark(number)
    
    def mark_number(self, color: DieColor, number: int) -> bool:
        """
        Mark a number in the specified color row.
        
        Args:
            color: The color row to mark in
            number: The number to mark
            
        Returns:
            True if successfully marked, False otherwise
        """
        if color not in self.rows:
            return False
        return self.rows[color].mark_number(number)
    
    def can_lock_row(self, color: DieColor) -> bool:
        """
        Check if a row can be locked.
        
        Args:
            color: The color row to check
            
        Returns:
            True if the row can be locked, False otherwise
        """
        if color not in self.rows:
            return False
        return self.rows[color].can_lock()
    
    def lock_row(self, color: DieColor) -> bool:
        """
        Lock a row if possible.
        
        Args:
            color: The color row to lock
            
        Returns:
            True if successfully locked, False otherwise
        """
        if color not in self.rows:
            return False
        return self.rows[color].lock_row()
    
    def add_penalty(self) -> bool:
        """
        Add a penalty mark.
        
        Returns:
            True if penalty added, False if already at maximum penalties
        """
        if self.penalties < self.max_penalties:
            self.penalties += 1
            return True
        return False
    
    def get_locked_rows_count(self) -> int:
        """
        Get the number of locked rows.
        
        Returns:
            Number of locked rows
        """
        return sum(1 for row in self.rows.values() if row.is_locked)
    
    def is_game_over(self) -> bool:
        """
        Check if the game is over for this player.
        Game is over if player has 4 penalties or 2 rows are locked.
        
        Returns:
            True if game is over, False otherwise
        """
        return self.penalties >= self.max_penalties or self.get_locked_rows_count() >= 2
    
    def calculate_total_score(self) -> int:
        """
        Calculate the total score for this scoresheet.
        
        Returns:
            Total score (sum of all row scores minus penalty points)
        """
        row_scores = sum(row.get_score() for row in self.rows.values())
        penalty_score = self.penalties * 5  # Each penalty is worth -5 points
        return row_scores - penalty_score
    
    def get_available_numbers(self, color: DieColor) -> List[int]:
        """
        Get the list of numbers that can still be marked in a color row.
        
        Args:
            color: The color row to check
            
        Returns:
            List of available numbers
        """
        if color not in self.rows or self.rows[color].is_locked:
            return []
        
        row = self.rows[color]
        available = []
        
        for i, number in enumerate(row.numbers):
            if i >= row.rightmost_marked and number not in row.marked:
                available.append(number)
        
        return available