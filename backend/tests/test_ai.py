import pytest
from app.game.ai_player import AIPlayer
from app.game.die import DieColor
from app.game.game_state import GameState
from app.game.dice_roller import DiceRoller

class MockGame:
    """Mock game class for testing AI functionality."""
    
    def __init__(self):
        self.dice_roller = DiceRoller()
        self.dice_results = {'white1': 1, 'white2': 1, 'red': 2, 'yellow': 5, 'green': 1, 'blue': 6}
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
    # Create AI players with different difficulties
    easy_ai = AIPlayer("Easy AI", 0, "easy")
    medium_ai = AIPlayer("Medium AI", 1, "medium")
    hard_ai = AIPlayer("Hard AI", 2, "hard")
    
    # Create mock game
    game = MockGame()
    game.players = [easy_ai, medium_ai, hard_ai]
    
    # Test move evaluation for different scenarios
    test_cases = [
        (DieColor.RED, 2),    # End number (should get bonus)
        (DieColor.RED, 12),   # End number (should get bonus)
        (DieColor.GREEN, 2),  # End number for descending row
        (DieColor.GREEN, 12), # End number for descending row
        (DieColor.YELLOW, 7), # Middle number
    ]
    
    for color, number in test_cases:
        easy_score = easy_ai._evaluate_move(game, color, number) if hasattr(easy_ai, '_evaluate_move') else 0
        medium_score = medium_ai._evaluate_move(game, color, number)
        hard_score = hard_ai._evaluate_move_advanced(game, color, number)
        
        assert isinstance(easy_score, (int, float))
        assert isinstance(medium_score, (int, float))
        assert isinstance(hard_score, (int, float))

def test_red_11_penalty():
    """Test that hard mode AI avoids marking 11 in red row as first move."""
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
    
    # The penalty should make the score significantly lower when red row is empty
    assert score_red_11_empty < score_red_11_with_marks
    assert score_red_11_with_marks - score_red_11_empty >= 10

def test_stage_1_move_probability():
    """Test that AI has reasonable probability to make moves in Stage 1."""
    # Test for different difficulty levels
    for difficulty in ["easy", "medium", "hard"]:
        ai = AIPlayer(f"{difficulty.capitalize()} AI", 0, difficulty)
        game = MockGame()
        game.players = [ai]
        
        # Test Stage 1 move decisions multiple times
        stage_1_decisions = []
        for _ in range(200):
            decision = ai.should_make_move_in_stage(game, 1)
            stage_1_decisions.append(decision)
        
        move_rate = sum(stage_1_decisions) / len(stage_1_decisions)
        
        # Expected minimum move rates for Stage 1
        expected_min_rates = {
            "easy": 0.5,    # Should make moves around 60% of the time
            "medium": 0.4,  # Should make moves around 50% of the time
            "hard": 0.3     # Should make moves around 40% of the time
        }
        
        min_rate = expected_min_rates[difficulty]
        assert move_rate >= min_rate
