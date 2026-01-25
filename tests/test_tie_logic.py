#!/usr/bin/env python3
"""
Test script to verify tie handling logic.
"""

from app.core.game import Game
from app.core.game_state import GameState
from unittest.mock import patch


def test_tie_handling():
    """Test that ties are correctly reported in the game message."""
    print("\nTesting tie handling logic...")

    # Initialize game with mocked logging
    with patch("app.core.game.setup_logging"):
        game = Game(num_players=2)

    p1 = game.players[0]
    p2 = game.players[1]

    # Mock scores to be equal
    p1.get_scoresheet().calculate_total_score = lambda: 33
    p2.get_scoresheet().calculate_total_score = lambda: 33

    # Force game over by locking 2 colors
    game.locked_colors = {"red", "yellow"}
    game.state = GameState.GAME_OVER

    # Call check_game_over to update message
    game.check_game_over()

    print(f"Game message: {game.message}")
    assert "It's a tie between Player 1 and Player 2" in game.message
    assert "33 points" in game.message

    print("Tie handling test passed!")


def test_single_winner_handling():
    """Test that a single winner is still correctly reported."""
    print("\nTesting single winner handling logic...")

    # Initialize game with mocked logging
    with patch("app.core.game.setup_logging"):
        game = Game(num_players=2)

    p1 = game.players[0]
    p2 = game.players[1]

    # Mock scores to be different
    p1.get_scoresheet().calculate_total_score = lambda: 40
    p2.get_scoresheet().calculate_total_score = lambda: 33

    # Force game over by locking 2 colors
    game.locked_colors = {"red", "yellow"}
    game.state = GameState.GAME_OVER

    # Call check_game_over to update message
    game.check_game_over()

    print(f"Game message: {game.message}")
    assert "Player 1 wins with 40 points" in game.message

    print("Single winner handling test passed!")


if __name__ == "__main__":
    test_tie_handling()
    test_single_winner_handling()


if __name__ == "__main__":
    test_tie_handling()
    test_single_winner_handling()
