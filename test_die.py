import unittest
from qwixx_objects import Die


class DieTests(unittest.TestCase):
    def test_roll_updates_value(self):
        # Arrange
        die = Die("red")

        # Act
        die.roll()

        # Assert
        self.assertTrue(1 <= die.value <= die.sides)

    def test_init_sets_color_and_sides(self):
        # Arrange
        color = "blue"
        sides = 8

        # Act
        die = Die(color, sides)

        # Assert
        self.assertEqual(die.color, color)
        self.assertEqual(die.sides, sides)

    def test_init_calls_roll(self):
        # Arrange
        color = "green"

        # Act
        die = Die(color)

        # Assert
        self.assertNotEqual(die.value, 0)


if __name__ == "__main__":
    unittest.main()
