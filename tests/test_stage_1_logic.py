import unittest
from app.core.game import Game
from app.core.game_state import GameState
from app.core.die import DieColor


class TestStage1Logic(unittest.TestCase):
    def setUp(self):
        self.game = Game(num_players=2)

        # Manually set up dice for predictable testing
        def mock_roll_all(locked_colors=None):
            results = {
                "white1": 3,
                "white2": 4,
                "red": 1,
                "yellow": 1,
                "green": 1,
                "blue": 1,
            }
            # Also update internal dice values so get_white_plus_colored_sums works correctly
            self.game.dice_roller.white_dice[0].value = 3
            self.game.dice_roller.white_dice[1].value = 4
            self.game.dice_roller.colored_dice[0].value = 1
            self.game.dice_roller.colored_dice[1].value = 1
            self.game.dice_roller.colored_dice[2].value = 1
            self.game.dice_roller.colored_dice[3].value = 1
            return results

        self.game.dice_roller.roll_all = mock_roll_all

    def test_stage_1_waits_for_both_players(self):
        """Test that Stage 1 doesn't end until both players are done."""
        # Start game and roll
        self.game.roll_dice()
        self.assertEqual(self.game.state, GameState.STAGE_1_MOVES)

        player1 = self.game.players[0]
        player2 = self.game.players[1]

        # Player 2 (inactive) marks white sum
        success = self.game.try_mark_number(player2, DieColor.RED, 7)
        self.assertTrue(success)
        self.assertIn(7, player2.get_scoresheet().rows[DieColor.RED].marked)

        # Player 2 is done
        self.game.player_done_making_moves(player2)
        self.assertEqual(self.game.state, GameState.STAGE_1_MOVES)
        self.assertIn(player2.get_id(), self.game.stage_1_players_finished)

        # Player 1 is done
        self.game.player_done_making_moves(player1)

        # Since Player 1 (rolling) has stage 2 moves available (3+1=4, 4+1=5), it should go to Stage 2
        self.assertEqual(self.game.state, GameState.STAGE_2_MOVES)

    def test_stage_1_moves_allowed_for_all_players(self):
        """Test that any player can mark the white sum in Stage 1."""
        self.game.roll_dice()

        player1 = self.game.players[0]
        player2 = self.game.players[1]

        # Player 1 (rolling) marks white sum
        self.assertTrue(self.game.try_mark_number(player1, DieColor.YELLOW, 7))

        # Player 2 (inactive) marks white sum
        self.assertTrue(self.game.try_mark_number(player2, DieColor.GREEN, 7))

        self.assertIn(7, player1.get_scoresheet().rows[DieColor.YELLOW].marked)
        self.assertIn(7, player2.get_scoresheet().rows[DieColor.GREEN].marked)


if __name__ == "__main__":
    unittest.main()
