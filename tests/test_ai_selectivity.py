#!/usr/bin/env python3
"""
Test script to verify AI selectivity improvements.
"""

from app.core.ai_player import AIPlayer
from app.core.die import DieColor
from app.core.game_state import GameState
from app.core.dice_roller import DiceRoller


class MockGame:
    """Mock game class for testing AI functionality."""

    def __init__(self):
        self.dice_roller = DiceRoller()
        self.dice_results = {
            "white1": 3,
            "white2": 4,
            "red": 2,
            "yellow": 5,
            "green": 1,
            "blue": 6,
        }
        self.locked_colors = set()
        self.state = GameState.STAGE_1_MOVES
        self.players = []

    def get_dice_results(self):
        return self.dice_results

    def get_locked_colors(self):
        return self.locked_colors

    def get_state(self):
        return self.state

    def get_players(self):
        return self.players

    def get_current_player(self):
        return self.players[0] if self.players else None


def test_passive_player_selectivity():
    """Test that passive AI players are more selective in Stage 1."""
    print("\nTesting passive player selectivity in Stage 1...")

    ai = AIPlayer("Passive AI", 1, "hard")
    ai.set_active(False)  # Make it a passive player

    game = MockGame()
    game.players = [ai]

    # White sum is 7 (3+4)
    # Red 7 as first move in row should have a negative score due to early positioning penalty
    # The score should be below the threshold of 2.0 for passive players

    available_moves = [(DieColor.RED, 7)]
    decision = ai.make_move_decision(game, available_moves)

    print(f"Passive AI decision for Red 7 (first move): {decision}")
    assert decision is None, "Passive AI should skip Red 7 as first move"

    # Now make it an active player
    ai.set_active(True)
    decision = ai.make_move_decision(game, available_moves)
    print(f"Active AI decision for Red 7 (first move): {decision}")
    # For active player, threshold is 0.0. Red 7 might still be negative and thus skipped.


def test_early_game_penalties():
    """Test that severe early game penalties are applied correctly."""
    print("\nTesting early game penalties...")

    ai = AIPlayer("Hard AI", 0, "hard")
    game = MockGame()

    # Test Red 10 as first move
    score_red_10 = ai._evaluate_move_advanced(game, DieColor.RED, 10)
    print(f"Red 10 (first move) score: {score_red_10:.1f}")
    assert score_red_10 < -10, "Red 10 as first move should have a very low score"

    # Test Red 2 as first move
    score_red_2 = ai._evaluate_move_advanced(game, DieColor.RED, 2)
    print(f"Red 2 (first move) score: {score_red_2:.1f}")
    assert score_red_2 > score_red_10, (
        "Red 2 should Have a better score than Red 10 as first move"
    )


def test_stage_1_participation_probability():
    """Test that participation probability is reduced for passive players."""
    print("\nTesting participation probability for passive players...")

    ai = AIPlayer("Hard AI", 1, "hard")
    game = MockGame()

    # Mocking get_available_moves to return something
    ai.get_available_moves = lambda g: [(DieColor.RED, 7)]

    # Passive
    ai.set_active(False)
    decisions_passive = [ai.should_make_move_in_stage(game, 1) for _ in range(1000)]
    rate_passive = sum(decisions_passive) / 1000

    # Active
    ai.set_active(True)
    decisions_active = [ai.should_make_move_in_stage(game, 1) for _ in range(1000)]
    rate_active = sum(decisions_active) / 1000

    print(f"Passive participation rate: {rate_passive:.2f}")
    print(f"Active participation rate: {rate_active:.2f}")

    assert rate_passive < rate_active, (
        "Passive players should participate less than active players in Stage 1"
    )


if __name__ == "__main__":
    test_passive_player_selectivity()
    test_early_game_penalties()
    test_stage_1_participation_probability()
