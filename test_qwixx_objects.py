import unittest
from qwixx_objects import Game, Player, Scoresheet


class GameTests(unittest.TestCase):
    def setUp(self):
        self.player1 = Player("Alice")
        self.player2 = Player("Bob")
        self.game = Game(self.player1, self.player2)

    def test_init(self):
        self.assertEqual(self.game.player1, self.player1)
        self.assertEqual(self.game.player2, self.player2)
        self.assertEqual(self.game.turn, 0)
        self.assertEqual(self.game.gameover, 0)
        self.assertEqual(self.game.finished_rows, 0)
        self.assertEqual(self.game.finished_color, "")
        self.assertIsNone(self.game.winner)

    def test_t(self):
        # TODO: Implement test for the t() method
        pass

    def test_play(self):
        # TODO: Implement test for the play() method
        pass

    def test_gameover(self):
        # TODO: Implement test for the gameover() method
        pass

    def test_finish(self):
        # TODO: Implement test for the finish() method
        pass


if __name__ == "__main__":
    unittest.main()
