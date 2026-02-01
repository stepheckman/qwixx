import pytest
from app.core.ai_player import AIPlayer
from app.core.die import DieColor
from app.core.game_state import GameState
from app.core.dice_roller import DiceRoller


class MockGame:
    def __init__(self, ai_strategy="hard"):
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
        self.ai_strategy = ai_strategy

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


def test_hard_ai_skips_extremely_bad_moves():
    """Test that Hard AI prefers a penalty over a move that skips too many numbers."""
    ai = AIPlayer("Hard AI", 0, "hard")
    ai.set_active(True)  # Active player role
    game = MockGame()
    game.players = [ai]

    # White sum is 7. Marking 7 in Red row as first move blocks 2,3,4,5,6 (5 numbers).
    # With the new logic, Red 7 should have a score around -30.
    # The active player threshold for Hard AI is -15.0.
    # So it should decide to SKIP (returning None) and take a penalty instead.

    available_moves = [(DieColor.RED, 7)]
    decision = ai.make_move_decision(game, available_moves)

    assert decision is None, "Hard AI should skip Red 7 as first move even if active"


def test_hard_ai_maintains_lock_potential():
    """Test that Hard AI avoids moves that make locking impossible."""
    ai = AIPlayer("Hard AI", 0, "hard")
    game = MockGame()

    # Blue row: numbers are 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2
    # Suppose we have 1 mark already (12).
    ai.get_scoresheet().mark_number(DieColor.BLUE, 12)

    # Now we consider marking 3.
    # If we mark 3, only 2 is left.
    # Total marks would be: 12, 3, 2 = 3 marks.
    # 3 marks is < 5, so locking is impossible.
    # The logic should apply a severe penalty.

    score = ai._evaluate_move_advanced(game, DieColor.BLUE, 3)
    assert score < -40.0, (
        f"Marking 3 in Blue with only 12 marked should be severely penalized, got {score}"
    )


def test_hard_ai_allows_good_moves():
    """Test that Hard AI still allows good moves (skipping few numbers)."""
    ai = AIPlayer("Hard AI", 0, "hard")
    game = MockGame()

    # Marking 3 in Red row as first move blocks only 2 (1 number).
    # This should have a positive or slightly negative but > -15 score.
    score = ai._evaluate_move_advanced(game, DieColor.RED, 3)
    assert score > -15.0, f"Red 3 as first move should be acceptable, got {score}"

    ai.set_active(True)
    available_moves = [(DieColor.RED, 3)]
    decision = ai.make_move_decision(game, available_moves)
    assert decision == (DieColor.RED, 3), "Hard AI should accept a good move like Red 3"


if __name__ == "__main__":
    pytest.main([__file__])
