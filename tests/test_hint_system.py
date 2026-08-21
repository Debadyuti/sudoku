import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
import pygame
from unittest.mock import Mock, patch, MagicMock
from sudoku_game import SudokuGame
from constants import BLUE, RED

pygame.init()


class TestHintSystem:
    """Test the Hint System (Phase 6.1: H key shows valid candidates)"""

    def setup_method(self):
        """Initialize Pygame and create game instance"""
        if not pygame.get_init():
            pygame.init()
        self.game = SudokuGame()

    def teardown_method(self):
        """Cleanup Pygame"""
        pygame.quit()

    def test_hint_shows_candidates_for_empty_cell(self):
        """Test: Pressing H on empty cell displays valid candidates"""
        # Setup: Empty cell at (0, 0)
        self.game.selected_cell = (0, 0)
        self.game.grid[0][0] = 0

        # Trigger hint with H key
        self.game.handle_key(pygame.K_h)

        # Verify: Message shows candidates
        assert "Valid candidates:" in self.game.message
        assert self.game.message_color == BLUE
        assert len(self.game.hint_candidates) > 0

    def test_hint_fails_for_filled_cell(self):
        """Test: Pressing H on filled cell shows error message"""
        # Setup: Filled cell at (0, 0)
        self.game.selected_cell = (0, 0)
        self.game.grid[0][0] = 5

        # Trigger hint with H key
        self.game.handle_key(pygame.K_h)

        # Verify: Error message displayed
        assert self.game.message == "Cell already filled!"
        assert self.game.message_color == RED
        assert self.game.hint_candidates == []

    def test_hint_fails_with_no_valid_candidates(self):
        """Test: Pressing H on cell with no valid candidates shows error"""
        # Setup: Create impossible situation by manually filling constraints
        # Fill row 0 with 1-9, then try to get hint for (0, 0)
        self.game.grid[0] = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        # Fill column 0 with remaining (already has 1, so skip to 9)
        for i in range(1, 9):
            self.game.grid[i][0] = (i % 9) + 1 if (i % 9) != 0 else 9

        # Now (0,0) should have no valid candidates
        self.game.selected_cell = (0, 0)
        self.game.grid[0][0] = 0  # Clear it first

        # Trigger hint with H key
        self.game.handle_key(pygame.K_h)

        # Verify: If no candidates exist, error message shown
        if self.game.hint_candidates == []:
            assert self.game.message == "No valid candidates for this cell!"
            assert self.game.message_color == RED

    def test_hint_disabled_during_solving(self):
        """Test: Hint is disabled when solver is running"""
        # Setup: Start solving
        self.game.solving = True
        self.game.selected_cell = (0, 0)
        self.game.grid[0][0] = 0

        # Trigger hint with H key
        self.game.handle_key(pygame.K_h)

        # Verify: No hint provided
        assert "Valid candidates:" not in self.game.message or self.game.solving
        assert self.game.hint_candidates == []

    def test_hint_cleared_on_number_entry(self):
        """Test: Hint candidates are cleared when entering a number"""
        # Setup: Get hint first
        self.game.selected_cell = (0, 0)
        self.game.grid[0][0] = 0
        self.game.handle_key(pygame.K_h)

        initial_hint = self.game.hint_candidates
        assert len(initial_hint) > 0, "Should have hint initially"

        # Enter a number
        self.game.handle_key(pygame.K_1)

        # Verify: Hint is cleared
        assert self.game.hint_candidates == []
        assert self.game.grid[0][0] == 1

    def test_hint_cleared_on_delete(self):
        """Test: Hint candidates are cleared when deleting cell content"""
        # Setup: Get hint first
        self.game.selected_cell = (0, 0)
        self.game.grid[0][0] = 0
        self.game.handle_key(pygame.K_h)

        initial_hint = self.game.hint_candidates
        assert len(initial_hint) > 0, "Should have hint initially"

        # Delete cell
        self.game.handle_key(pygame.K_BACKSPACE)

        # Verify: Hint is cleared
        assert self.game.hint_candidates == []

    def test_hint_cleared_on_grid_clear(self):
        """Test: Hint candidates are cleared when entire grid is cleared"""
        # Setup: Get hint first
        self.game.selected_cell = (0, 0)
        self.game.grid[0][0] = 0
        self.game.handle_key(pygame.K_h)

        initial_hint = self.game.hint_candidates
        assert len(initial_hint) > 0, "Should have hint initially"

        # Clear grid
        self.game.clear_grid()

        # Verify: Hint is cleared
        assert self.game.hint_candidates == []

    def test_hint_message_format(self):
        """Test: Hint message format is correct"""
        # Setup: Get hint
        self.game.selected_cell = (0, 0)
        self.game.grid[0][0] = 0

        self.game.handle_key(pygame.K_h)

        # Verify: Message format matches
        if self.game.hint_candidates:
            expected = f"Valid candidates: {', '.join(map(str, self.game.hint_candidates))}"
            assert self.game.message == expected

    def test_hint_works_with_keypad_numbers(self):
        """Test: Hint is cleared when entering number via keypad"""
        # Setup: Get hint first
        self.game.selected_cell = (0, 0)
        self.game.grid[0][0] = 0
        self.game.handle_key(pygame.K_h)

        assert len(self.game.hint_candidates) > 0, "Should have hint initially"

        # Enter number via keypad
        self.game.handle_key(pygame.K_KP1)

        # Verify: Hint is cleared
        assert self.game.hint_candidates == []
        assert self.game.grid[0][0] == 1

    def test_hint_with_keypad_delete(self):
        """Test: Hint is cleared when using keypad delete (0)"""
        # Setup: Get hint first
        self.game.selected_cell = (0, 0)
        self.game.grid[0][0] = 0
        self.game.handle_key(pygame.K_h)

        assert len(self.game.hint_candidates) > 0, "Should have hint initially"

        # Delete with keypad 0
        self.game.handle_key(pygame.K_KP0)

        # Verify: Hint is cleared
        assert self.game.hint_candidates == []
