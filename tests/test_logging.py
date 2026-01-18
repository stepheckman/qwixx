#!/usr/bin/env python3
"""
Test script to verify logging functionality.
"""

import pytest

pygame = pytest.importorskip("pygame")

from app.core.game import Game
from app.core.logger import setup_logging

def test_logging():
    """Test the logging functionality."""
    # Initialize logging
    setup_logging()
    
    # Initialize Pygame (headless)
    pygame.init()
    screen = pygame.display.set_mode((1200, 800))
    
    try:
        # Create a game
        print("Creating game...")
        game = Game(screen, 1, 'medium')
        
        # Roll dice
        print("Rolling dice...")
        game.roll_dice()
        
        print("Test completed! Check the log files in the logs/ directory.")
        
    except Exception as e:
        print(f"Error during test: {e}")
    finally:
        pygame.quit()

if __name__ == "__main__":
    test_logging()
