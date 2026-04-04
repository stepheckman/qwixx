import pytest
from app.game.scoresheet import ColorRow, DieColor

def test_cannot_mark_last_number_without_5_marks():
    """Test that we cannot mark the rightmost number (12) without 5 prior marks."""
    # Create a red row (2-12)
    red_row = ColorRow(DieColor.RED, list(range(2, 13)))
    
    # Mark 4 numbers: 2, 3, 4, 5
    red_row.mark_number(2)
    red_row.mark_number(3)
    red_row.mark_number(4)
    red_row.mark_number(5)
    
    # Verify we have 4 marks
    assert len(red_row.marked) == 4
    
    # Try to mark 12 - should fail
    assert not red_row.can_mark(12)
    assert not red_row.mark_number(12)

def test_can_mark_last_number_with_5_marks():
    """Test that we CAN mark the rightmost number (12) with 5 prior marks."""
    # Create a red row (2-12)
    red_row = ColorRow(DieColor.RED, list(range(2, 13)))
    
    # Mark 5 numbers: 2, 3, 4, 5, 6
    red_row.mark_number(2)
    red_row.mark_number(3)
    red_row.mark_number(4)
    red_row.mark_number(5)
    red_row.mark_number(6)
    
    # Verify we have 5 marks
    assert len(red_row.marked) == 5
    
    # Try to mark 12 - should succeed
    assert red_row.can_mark(12)
    assert red_row.mark_number(12)
    
    # Verify we now have 6 marks
    assert len(red_row.marked) == 6

def test_locking_and_scoring():
    """Test that locking works and adds 1 to the mark count for scoring."""
    # Create a red row (2-12)
    red_row = ColorRow(DieColor.RED, list(range(2, 13)))
    
    # Mark 5 numbers: 2, 3, 4, 5, 6
    for i in [2, 3, 4, 5, 6]:
        red_row.mark_number(i)
        
    # Mark 12
    red_row.mark_number(12)
    
    # Should be able to lock
    assert red_row.can_lock()
    assert red_row.lock_row()
    assert red_row.is_locked
    
    # Calculate score
    # We have 6 marked numbers: 2, 3, 4, 5, 6, 12
    # Plus 1 for the lock symbol = 7 effective marks
    # Score formula: n(n+1)/2 => 7(8)/2 = 28
    
    score = red_row.get_score()
    assert score == 28
