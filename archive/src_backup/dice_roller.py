"""
DiceRoller class for managing all dice in the Qwixx game.
"""

from typing import Dict, List, Tuple
from .die import Die, DieColor

class DiceRoller:
    """Manages all six dice used in the Qwixx game."""
    
    def __init__(self):
        """Initialize the dice roller with all six dice."""
        self.dice: Dict[DieColor, Die] = {
            DieColor.WHITE: Die(DieColor.WHITE),
            DieColor.RED: Die(DieColor.RED),
            DieColor.YELLOW: Die(DieColor.YELLOW),
            DieColor.GREEN: Die(DieColor.GREEN),
            DieColor.BLUE: Die(DieColor.BLUE)
        }
        # Add a second white die
        self.white_dice = [Die(DieColor.WHITE), Die(DieColor.WHITE)]
        self.colored_dice = [
            Die(DieColor.RED),
            Die(DieColor.YELLOW),
            Die(DieColor.GREEN),
            Die(DieColor.BLUE)
        ]
    
    def roll_all(self) -> Dict[str, int]:
        """
        Roll all six dice and return the results.
        
        Returns:
            Dictionary with dice results: 
            {'white1': value, 'white2': value, 'red': value, 'yellow': value, 'green': value, 'blue': value}
        """
        results = {}
        
        # Roll white dice
        results['white1'] = self.white_dice[0].roll()
        results['white2'] = self.white_dice[1].roll()
        
        # Roll colored dice
        for die in self.colored_dice:
            results[die.color.value] = die.roll()
        
        return results
    
    def get_white_sum(self) -> int:
        """
        Get the sum of the two white dice.
        
        Returns:
            Sum of the two white dice values
        """
        return (self.white_dice[0].get_value() or 0) + (self.white_dice[1].get_value() or 0)
    
    def get_white_plus_colored_sums(self) -> Dict[DieColor, List[int]]:
        """
        Get all possible sums of one white die plus each colored die.
        
        Returns:
            Dictionary mapping each color to list of possible sums with white dice
        """
        sums = {}
        white_values = [die.get_value() or 0 for die in self.white_dice]
        
        for colored_die in self.colored_dice:
            colored_value = colored_die.get_value() or 0
            sums[colored_die.color] = [white + colored_value for white in white_values]
        
        return sums
    
    def get_all_dice_values(self) -> Dict[str, int]:
        """
        Get current values of all dice.
        
        Returns:
            Dictionary with all dice values
        """
        return {
            'white1': self.white_dice[0].get_value() or 0,
            'white2': self.white_dice[1].get_value() or 0,
            'red': self.colored_dice[0].get_value() or 0,
            'yellow': self.colored_dice[1].get_value() or 0,
            'green': self.colored_dice[2].get_value() or 0,
            'blue': self.colored_dice[3].get_value() or 0
        }
    
    def __str__(self) -> str:
        """String representation of all dice."""
        values = self.get_all_dice_values()
        return f"White: {values['white1']}, {values['white2']} | Red: {values['red']} | Yellow: {values['yellow']} | Green: {values['green']} | Blue: {values['blue']}"