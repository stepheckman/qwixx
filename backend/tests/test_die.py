import pytest
from app.game.die import Die, DieColor

def test_roll_updates_value():
    # Arrange
    die = Die(DieColor.RED)

    # Act
    die.roll()

    # Assert
    assert 1 <= die.get_value() <= 6
    assert die.color == DieColor.RED

def test_init_sets_color():
    # Arrange
    color = DieColor.BLUE

    # Act
    die = Die(color)

    # Assert
    assert die.color == color
    assert die.get_value() is None
