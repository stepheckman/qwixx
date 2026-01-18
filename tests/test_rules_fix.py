
import unittest
from src.scoresheet import ColorRow, DieColor

class TestRuleFixes(unittest.TestCase):
    def setUp(self):
        # Create a red row (2-12)
        self.red_row = ColorRow(DieColor.RED, list(range(2, 13)))
        
    def test_cannot_mark_last_number_without_5_marks(self):
        """Test that we cannot mark the rightmost number (12) without 5 prior marks."""
        # Mark 4 numbers: 2, 3, 4, 5
        self.assertTrue(self.red_row.mark_number(2))
        self.assertTrue(self.red_row.mark_number(3))
        self.assertTrue(self.red_row.mark_number(4))
        self.assertTrue(self.red_row.mark_number(5))
        
        # Verify we have 4 marks
        self.assertEqual(len(self.red_row.marked), 4)
        
        # Try to mark 12 - should fail
        self.assertFalse(self.red_row.can_mark(12))
        self.assertFalse(self.red_row.mark_number(12))
        
    def test_can_mark_last_number_with_5_marks(self):
        """Test that we CAN mark the rightmost number (12) with 5 prior marks."""
        # Mark 5 numbers: 2, 3, 4, 5, 6
        self.assertTrue(self.red_row.mark_number(2))
        self.assertTrue(self.red_row.mark_number(3))
        self.assertTrue(self.red_row.mark_number(4))
        self.assertTrue(self.red_row.mark_number(5))
        self.assertTrue(self.red_row.mark_number(6))
        
        # Verify we have 5 marks
        self.assertEqual(len(self.red_row.marked), 5)
        
        # Try to mark 12 - should succeed
        self.assertTrue(self.red_row.can_mark(12))
        self.assertTrue(self.red_row.mark_number(12))
        
        # Verify we now have 6 marks
        self.assertEqual(len(self.red_row.marked), 6)
        
    def test_locking_and_scoring(self):
        """Test that locking works and adds 1 to the mark count for scoring."""
        # Mark 5 numbers: 2, 3, 4, 5, 6
        for i in [2, 3, 4, 5, 6]:
            self.red_row.mark_number(i)
            
        # Mark 12
        self.red_row.mark_number(12)
        
        # Should be able to lock
        self.assertTrue(self.red_row.can_lock())
        self.assertTrue(self.red_row.lock_row())
        self.assertTrue(self.red_row.is_locked)
        
        # Calculate score
        # We have 6 marked numbers: 2, 3, 4, 5, 6, 12
        # Plus 1 for the lock symbol = 7 effective marks
        # Score formula: n(n+1)/2 => 7(8)/2 = 28
        
        score = self.red_row.get_score()
        self.assertEqual(score, 28)
        
        # Without the fix, score would be based on 6 marks: 6(7)/2 = 21
        
if __name__ == '__main__':
    unittest.main()
