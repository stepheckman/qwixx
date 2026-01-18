import unittest
from app.core.die import Die, DieColor

class DieTests(unittest.TestCase):
    def test_roll_updates_value(self):
        # Arrange
        die = Die(DieColor.RED)

        # Act
        die.roll()

        # Assert
        self.assertTrue(1 <= die.get_value() <= 6)
        self.assertEqual(die.color, DieColor.RED)

    def test_init_sets_color(self):
        # Arrange
        color = DieColor.BLUE

        # Act
        die = Die(color)

        # Assert
        self.assertEqual(die.color, color)
        self.assertIsNone(die.get_value())

if __name__ == "__main__":
    unittest.main()
