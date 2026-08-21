import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
import pygame
import copy
from sudoku_game import SudokuGame
from constants import BLUE

pygame.init()


class TestUndoRedoSystem:
    """Test Undo/Redo System (Phase 6.3: Move history with Ctrl+Z/Y)"""

    def setup_method(self):
        """Initialize Pygame and create game instance"""
        if not pygame.get_init():
            pygame.init()
        self.game = SudokuGame()

    def teardown_method(self):
        """Cleanup Pygame"""
        pygame.quit()

    def test_move_history_initialized_empty(self):
        """Test: Move history starts empty"""
        assert self.game.move_history == []
        assert self.game.move_index == -1

    def test_save_move_state_adds_to_history(self):
        """Test: Saving move adds grid state to history"""
        self.game.grid[0][0] = 1
        self.game._save_move_state()

        assert len(self.game.move_history) == 1
        assert self.game.move_index == 0

    def test_multiple_moves_build_history(self):
        """Test: Multiple moves create sequential history"""
        # Move 1
        self.game.grid[0][0] = 1
        self.game._save_move_state()

        # Move 2
        self.game.grid[0][1] = 2
        self.game._save_move_state()

        # Move 3
        self.game.grid[0][2] = 3
        self.game._save_move_state()

        assert len(self.game.move_history) == 3
        assert self.game.move_index == 2

    def test_undo_single_move(self):
        """Test: Undo reverts to previous grid state"""
        # Save initial state
        self.game.grid[0][0] = 1
        self.game._save_move_state()
        initial_grid = copy.deepcopy(self.game.move_history[0])

        # Make new move
        self.game.grid[0][0] = 2
        self.game._save_move_state()

        # Undo
        self.game.undo_move()

        # Verify: Grid reverted to initial state
        assert self.game.grid[0][0] == 1
        assert self.game.message == "Move undone"

    def test_undo_multiple_moves(self):
        """Test: Multiple undos work sequentially"""
        # Build history
        self.game.grid[0][0] = 1
        self.game._save_move_state()
        self.game.grid[0][1] = 2
        self.game._save_move_state()
        self.game.grid[0][2] = 3
        self.game._save_move_state()

        # Undo 2 times
        self.game.undo_move()
        assert self.game.move_index == 1
        self.game.undo_move()
        assert self.game.move_index == 0

        # Grid should match first move
        assert self.game.grid[0][0] == 1
        assert self.game.grid[0][1] == 0
        assert self.game.grid[0][2] == 0

    def test_redo_single_move(self):
        """Test: Redo restores undone move"""
        # Build history and undo
        self.game.grid[0][0] = 1
        self.game._save_move_state()
        self.game.grid[0][1] = 2
        self.game._save_move_state()

        self.game.undo_move()
        assert self.game.grid[0][1] == 0

        # Redo
        self.game.redo_move()

        # Verify: Move restored
        assert self.game.grid[0][0] == 1
        assert self.game.grid[0][1] == 2
        assert self.game.message == "Move redone"

    def test_redo_multiple_moves(self):
        """Test: Multiple redos work sequentially"""
        # Build history
        for i in range(3):
            self.game.grid[0][i] = i + 1
            self.game._save_move_state()

        # Undo twice
        self.game.undo_move()
        self.game.undo_move()
        assert self.game.move_index == 0

        # Redo twice
        self.game.redo_move()
        self.game.redo_move()
        assert self.game.move_index == 2

        # Grid should be fully restored
        assert self.game.grid[0][0] == 1
        assert self.game.grid[0][1] == 2
        assert self.game.grid[0][2] == 3

    def test_undo_at_beginning(self):
        """Test: Undo at start of history does nothing"""
        # No history yet
        self.game.undo_move()

        assert self.game.move_index == -1
        assert self.game.message == "Nothing to undo"

    def test_redo_at_end(self):
        """Test: Redo at end of history does nothing"""
        # Build and navigate to end
        self.game.grid[0][0] = 1
        self.game._save_move_state()

        # Already at end
        self.game.redo_move()

        assert self.game.message == "Nothing to redo"

    def test_new_move_clears_redo_stack(self):
        """Test: Making new move after undo clears redo stack"""
        # Build history
        self.game.grid[0][0] = 1
        self.game._save_move_state()
        self.game.grid[0][1] = 2
        self.game._save_move_state()

        # Undo
        self.game.undo_move()
        assert self.game.move_index == 0
        assert len(self.game.move_history) == 2

        # Make new move
        self.game.grid[0][2] = 3
        self.game._save_move_state()

        # Verify: Redo stack cleared
        assert len(self.game.move_history) == 2
        assert self.game.move_index == 1

    def test_history_max_size_100(self):
        """Test: Move history respects 100-move limit"""
        # Save 110 moves (each one modifies same cell, cycling through value 1)
        for i in range(110):
            self.game.grid[0][0] = 1  # Always set to same value
            self.game._save_move_state()

        # Verify: Only 100 moves kept
        assert len(self.game.move_history) == 100
        assert self.game.move_index == 99

    def test_error_cells_cleared_on_undo(self):
        """Test: Error cells cleared after undo"""
        # Setup: Create history
        self.game.grid[0][0] = 1
        self.game._save_move_state()
        self.game.grid[0][1] = 2
        self.game._save_move_state()

        # Add error and undo
        self.game.error_cells.add((0, 0))
        self.game.undo_move()

        # Verify: Errors cleared by undo_move()
        assert len(self.game.error_cells) == 0

    def test_error_cells_cleared_on_redo(self):
        """Test: Error cells cleared after redo"""
        # Setup: Create history
        self.game.grid[0][0] = 1
        self.game._save_move_state()
        self.game.grid[0][1] = 2
        self.game._save_move_state()
        self.game.undo_move()

        # Add error and redo
        self.game.error_cells.add((0, 0))
        self.game.redo_move()

        # Verify: Errors cleared by redo_move()
        assert len(self.game.error_cells) == 0

    def test_hint_cleared_on_undo(self):
        """Test: Hints cleared after undo"""
        # Setup: Create history
        self.game.grid[0][0] = 1
        self.game._save_move_state()
        self.game.grid[0][1] = 2
        self.game._save_move_state()

        # Add hint and undo
        self.game.hint_candidates = [2, 3, 4]
        self.game.undo_move()

        # undo_move clears hints
        assert self.game.hint_candidates == []

    def test_hint_cleared_on_redo(self):
        """Test: Hints cleared after redo"""
        # Setup: Create history
        self.game.grid[0][0] = 1
        self.game._save_move_state()
        self.game.grid[0][1] = 2
        self.game._save_move_state()
        self.game.undo_move()

        # Add hint and redo
        self.game.hint_candidates = [2, 3, 4]
        self.game.redo_move()

        # redo_move clears hints
        assert self.game.hint_candidates == []

    def test_keyboard_undo_shortcut(self):
        """Test: Ctrl+Z keyboard shortcut triggers undo"""
        self.game.grid[0][0] = 1
        self.game._save_move_state()
        self.game.grid[0][1] = 2
        self.game._save_move_state()
        self.game.selected_cell = (0, 0)

        # Trigger Ctrl+Z
        self.game.handle_key(pygame.K_z, mod=pygame.KMOD_CTRL)

        assert self.game.move_index == 0  # After one undo
        assert self.game.message == "Move undone"

    def test_keyboard_redo_shortcut(self):
        """Test: Ctrl+Y keyboard shortcut triggers redo"""
        self.game.grid[0][0] = 1
        self.game._save_move_state()
        self.game.grid[0][1] = 2
        self.game._save_move_state()
        self.game.undo_move()

        # Trigger Ctrl+Y
        self.game.handle_key(pygame.K_y, mod=pygame.KMOD_CTRL)

        assert self.game.move_index == 1
        assert self.game.message == "Move redone"

    def test_undo_disabled_during_solving(self):
        """Test: Undo disabled when solver running"""
        self.game.grid[0][0] = 1
        self.game._save_move_state()
        self.game.solving = True

        # Try undo via keyboard
        self.game.handle_key(pygame.K_z, mod=pygame.KMOD_CTRL)

        # Should still be in solving state
        assert self.game.solving
        # Move index unchanged (undo not called)
        assert self.game.move_index == 0

    def test_redo_disabled_during_solving(self):
        """Test: Redo disabled when solver running"""
        self.game.grid[0][0] = 1
        self.game._save_move_state()
        self.game.grid[0][1] = 2
        self.game._save_move_state()
        self.game.undo_move()
        self.game.solving = True

        # Try redo via keyboard
        self.game.handle_key(pygame.K_y, mod=pygame.KMOD_CTRL)

        # Move index unchanged (redo not called because solving=True)
        assert self.game.move_index == 0

    def test_clear_grid_resets_history(self):
        """Test: Clear grid clears move history"""
        # Build history
        self.game.grid[0][0] = 1
        self.game._save_move_state()
        self.game.grid[0][1] = 2
        self.game._save_move_state()

        # Clear
        self.game.clear_grid()

        # Verify: History cleared
        assert self.game.move_history == []
        assert self.game.move_index == -1

    def test_move_state_deep_copy(self):
        """Test: Move history stores independent copies"""
        # Create nested structure in grid
        self.game.grid[0][0] = 1
        self.game._save_move_state()

        # Modify grid
        self.game.grid[0][0] = 2

        # Verify: History copy unchanged
        assert self.game.move_history[0][0][0] == 1

    def test_undo_redo_roundtrip(self):
        """Test: Full undo/redo cycle preserves state"""
        # Make changes
        self.game.grid[0][0] = 1
        self.game._save_move_state()
        state1 = [row[:] for row in self.game.grid]

        self.game.grid[0][1] = 2
        self.game._save_move_state()
        state2 = [row[:] for row in self.game.grid]

        self.game.grid[0][2] = 3
        self.game._save_move_state()
        state3 = [row[:] for row in self.game.grid]

        # Undo twice to get back to state1
        self.game.undo_move()
        self.game.undo_move()

        # Should match state1
        for i in range(9):
            for j in range(9):
                assert self.game.grid[i][j] == state1[i][j]

        # Redo twice to get back to state3
        self.game.redo_move()
        self.game.redo_move()

        # Should match state3
        for i in range(9):
            for j in range(9):
                assert self.game.grid[i][j] == state3[i][j]
