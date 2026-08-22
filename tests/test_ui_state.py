"""
Tests for Phase 7.3 UI State Rendering

Tests for:
- Grid background color based on puzzle state
- Frozen cell styling
- Button state based on finalized flag
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
from solver import PuzzleState


class TestUIStateColoring:
    """Test puzzle state color rendering"""

    def test_state_color_red(self):
        """INVALID state should use RED color (255, 0, 0)"""
        from solver import SudokuSolver
        grid = [
            [1, 1, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
        ]
        solver = SudokuSolver(grid)
        state, message, color = solver.validate_puzzle()

        assert state == PuzzleState.INVALID
        assert color == (255, 0, 0)

    def test_state_color_amber(self):
        """MULTIPLE_SOLUTIONS state should use AMBER color (255, 165, 0)"""
        from solver import SudokuSolver
        grid = [
            [1, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
        ]
        solver = SudokuSolver(grid)
        state, message, color = solver.validate_puzzle()

        assert state == PuzzleState.MULTIPLE_SOLUTIONS
        assert color == (255, 165, 0)

    def test_state_color_green(self):
        """SINGLE_SOLUTION state should use GREEN color (0, 200, 0)"""
        from solver import SudokuSolver
        grid = [
            [5, 3, 4, 6, 7, 8, 9, 1, 2],
            [6, 7, 2, 1, 9, 5, 3, 4, 8],
            [1, 9, 8, 3, 4, 2, 5, 6, 7],
            [8, 5, 9, 7, 6, 1, 4, 2, 3],
            [4, 2, 6, 8, 5, 3, 7, 9, 1],
            [7, 1, 3, 9, 2, 4, 8, 5, 6],
            [9, 6, 1, 5, 3, 7, 2, 8, 4],
            [2, 8, 7, 4, 1, 9, 6, 3, 5],
            [3, 4, 5, 0, 0, 0, 0, 0, 0],
        ]
        solver = SudokuSolver(grid)
        state, message, color = solver.validate_puzzle()

        assert state == PuzzleState.SINGLE_SOLUTION
        assert color == (0, 200, 0)


class TestFrozenCellStyling:
    """Test frozen cell visual styling"""

    def test_frozen_cells_in_game(self):
        """Frozen cells should prevent entry"""
        from sudoku_game import SudokuGame

        game = SudokuGame()
        game.grid[0][0] = 5
        game.frozen_cells.add((0, 0))
        game.selected_cell = (0, 0)

        # Try to overwrite frozen cell
        game.handle_key(3)  # Press '3'

        # Cell should remain unchanged
        assert game.grid[0][0] == 5
        assert "locked" in game.message.lower()

    def test_frozen_cells_clear_grid(self):
        """Frozen cells should be cleared when grid is cleared"""
        from sudoku_game import SudokuGame

        game = SudokuGame()
        game.frozen_cells.add((0, 0))
        game.frozen_cells.add((1, 1))

        game.clear_grid()

        assert len(game.frozen_cells) == 0

    def test_finalized_button_disabled(self):
        """Finalize button should be grayed out when puzzle finalized"""
        from sudoku_game import SudokuGame
        from solver import PuzzleState

        game = SudokuGame()
        # Puzzle starts not finalized
        assert game.finalized is False

        # After finalize with valid puzzle, should be finalized
        game.grid[0][0] = 5
        game.finalize_puzzle()

        assert game.finalized is True
        assert game.puzzle_state != PuzzleState.INVALID


class TestUIStateTransitions:
    """Test state transitions and UI updates"""

    def test_clear_resets_finalized(self):
        """Clear button should reset finalized state"""
        from sudoku_game import SudokuGame

        game = SudokuGame()
        game.grid[0][0] = 5
        game.finalize_puzzle()
        assert game.finalized is True

        game.clear_grid()
        assert game.finalized is False

    def test_state_colors_persist(self):
        """State colors should persist until changed"""
        from sudoku_game import SudokuGame
        from solver import PuzzleState

        game = SudokuGame()
        # Initial state
        assert game.puzzle_state == PuzzleState.MULTIPLE_SOLUTIONS
        assert game.state_color == (255, 165, 0)  # AMBER

        # After creating invalid puzzle
        game.grid[0][0] = 1
        game.grid[0][1] = 1
        game.finalize_puzzle()

        assert game.puzzle_state == PuzzleState.INVALID
        assert game.state_color == (255, 0, 0)  # RED

        # After clear, reset to default
        game.clear_grid()
        assert game.puzzle_state == PuzzleState.MULTIPLE_SOLUTIONS
        assert game.state_color == (255, 165, 0)  # AMBER
