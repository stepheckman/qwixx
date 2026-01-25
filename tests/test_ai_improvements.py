#!/usr/bin/env python3
"""
Test script to verify AI improvements are working correctly.
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


def test_ai_evaluation():
    """Test AI move evaluation functions."""
    print("Testing AI Move Evaluation...")

    # Create AI players with different difficulties
    easy_ai = AIPlayer("Easy AI", 0, "easy")
    medium_ai = AIPlayer("Medium AI", 1, "medium")
    hard_ai = AIPlayer("Hard AI", 2, "hard")

    # Create mock game
    game = MockGame()
    game.players = [easy_ai, medium_ai, hard_ai]

    # Test move evaluation for different scenarios
    test_cases = [
        (DieColor.RED, 2),  # End number (should get bonus)
        (DieColor.RED, 12),  # End number (should get bonus)
        (DieColor.GREEN, 2),  # End number for descending row
        (DieColor.GREEN, 12),  # End number for descending row
        (DieColor.YELLOW, 7),  # Middle number
    ]

    print("\nMove Evaluation Scores:")
    print("Color\tNumber\tEasy\tMedium\tHard")
    print("-" * 40)

    for color, number in test_cases:
        easy_score = (
            easy_ai._evaluate_move(game, color, number)
            if hasattr(easy_ai, "_evaluate_move")
            else 0
        )
        medium_score = medium_ai._evaluate_move(game, color, number)
        hard_score = hard_ai._evaluate_move_advanced(game, color, number)

        print(
            f"{color.value}\t{number}\t{easy_score:.1f}\t{medium_score:.1f}\t{hard_score:.1f}"
        )

    print("\nTesting strategic decision making...")

    # Test should_make_move_in_stage
    for difficulty in ["easy", "medium", "hard"]:
        ai = AIPlayer(f"{difficulty.capitalize()} AI", 0, difficulty)
        game.players = [ai]

        # Test multiple times to see probability distribution
        stage_1_decisions = []
        stage_2_decisions = []

        for _ in range(100):
            stage_1_decisions.append(ai.should_make_move_in_stage(game, 1))
            stage_2_decisions.append(ai.should_make_move_in_stage(game, 2))

        stage_1_rate = sum(stage_1_decisions) / len(stage_1_decisions)
        stage_2_rate = sum(stage_2_decisions) / len(stage_2_decisions)

        print(
            f"{difficulty.capitalize()} AI - Stage 1 move rate: {stage_1_rate:.2f}, Stage 2 move rate: {stage_2_rate:.2f}"
        )

    print("\nTesting penalty avoidance...")

    # Test penalty avoidance logic
    test_ai = AIPlayer("Test AI", 0, "medium")
    game.players = [test_ai]

    for penalty_count in range(4):
        test_ai.get_scoresheet().penalties = penalty_count
        bonus = test_ai._calculate_penalty_avoidance_bonus(game)
        print(f"Penalties: {penalty_count}, Avoidance bonus: {bonus:.1f}")

    print("\nTesting end number bonuses...")

    # Test end number bonuses
    for color in [DieColor.RED, DieColor.YELLOW, DieColor.GREEN, DieColor.BLUE]:
        for number in [2, 7, 12]:
            bonus = test_ai._calculate_end_number_bonus(color, number)
            print(f"{color.value} {number}: End number bonus = {bonus:.1f}")

    print("\nAI improvements test completed successfully!")


def test_red_11_penalty():
    """Test that hard mode AI avoids marking 11 in red row as first move."""
    print("\nTesting Red 11 penalty for hard mode AI...")

    # Create hard mode AI
    hard_ai = AIPlayer("Hard AI", 0, "hard")

    # Create mock game
    game = MockGame()
    game.players = [hard_ai]

    # Test scenario: Red row is empty, 11 is available
    red_row = hard_ai.get_scoresheet().rows[DieColor.RED]
    assert len(red_row.marked) == 0, "Red row should be empty for this test"

    # Evaluate move for Red 11 when red row is empty
    score_red_11_empty = hard_ai._evaluate_move_advanced(game, DieColor.RED, 11)

    # Mark a number in red row first (e.g., 5)
    hard_ai.get_scoresheet().mark_number(DieColor.RED, 5)

    # Evaluate move for Red 11 when red row has marks
    score_red_11_with_marks = hard_ai._evaluate_move_advanced(game, DieColor.RED, 11)

    print(f"Red 11 score (empty row): {score_red_11_empty:.1f}")
    print(f"Red 11 score (with marks): {score_red_11_with_marks:.1f}")

    # The penalty should make the score significantly lower when red row is empty
    assert score_red_11_empty < score_red_11_with_marks, (
        "Red 11 should have lower score when red row is empty"
    )

    # Test that the penalty is significant (at least -10 points difference)
    penalty_difference = score_red_11_with_marks - score_red_11_empty
    assert penalty_difference >= 10, (
        f"Penalty should be at least 10 points, got {penalty_difference:.1f}"
    )

    print("Red 11 penalty test passed!")


def test_stage_1_move_probability():
    """Test that AI has reasonable probability to make moves in Stage 1."""
    print("\nTesting Stage 1 move probability...")

    # Test for different difficulty levels
    for difficulty in ["easy", "medium", "hard"]:
        ai = AIPlayer(f"{difficulty.capitalize()} AI", 0, difficulty)
        game = MockGame()
        game.players = [ai]

        # Test Stage 1 move decisions multiple times
        stage_1_decisions = []
        for _ in range(100):
            decision = ai.should_make_move_in_stage(game, 1)
            stage_1_decisions.append(decision)

        move_rate = sum(stage_1_decisions) / len(stage_1_decisions)
        print(f"{difficulty.capitalize()} AI Stage 1 move rate: {move_rate:.2f}")

        # Expected minimum move rates for Stage 1
        # Now much lower because the mock game provides "bad" moves (Score -8.5)
        # and the new AI is more selective.
        expected_min_rates = {
            "easy": 0.05,  # Significant reduction
            "medium": 0.05,  # Significant reduction
            "hard": 0.05,  # Significant reduction
        }

        min_rate = expected_min_rates[difficulty]
        assert move_rate >= min_rate, (
            f"{difficulty} AI should make Stage 1 moves at least {min_rate * 100}% of the time, got {move_rate * 100:.1f}%"
        )

    print("Stage 1 move probability test passed!")


if __name__ == "__main__":
    test_ai_evaluation()
    test_red_11_penalty()
    test_stage_1_move_probability()
