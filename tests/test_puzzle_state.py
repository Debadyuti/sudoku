"""
Tests for Puzzle State System (Phase 7.2)

Tests for:
- Puzzle state tracking and updates
- Finalized flag behavior
- Frozen cells enforcement
- State validation integration
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pygame
from sudoku_game import SudokuGame
from solver import PuzzleState


class TestPuzzleStateTracking:
    """Test puzzle state initialization and updates"""

    def test_initial_puzzle_state(self):
        """Puzzle should start in MULTIPLE_SOLUTIONS state"""
        game = SudokuGame()
        assert game.puzzle_state == PuzzleState.MULTIPLE_SOLUTIONS
        assert game.finalized is False
        assert game.state_solution_grid is None

    def test_finalize_invalid_puzzle(self):
        """Finalize with duplicate should set INVALID state"""
        game = SudokuGame()
        # Set duplicate in row
        game.grid[0][0] = 1
        game.grid[0][1] = 1
        game.finalize_puzzle()

        assert game.puzzle_state == PuzzleState.INVALID
        assert game.state_color == (255, 0, 0)  # RED
        assert game.finalized is False

    def test_finalize_multiple_solutions(self):
        """Finalize sparse puzzle should set MULTIPLE_SOLUTIONS state"""
        game = SudokuGame()
        game.grid[0][0] = 1
        game.finalize_puzzle()

        assert game.puzzle_state == PuzzleState.MULTIPLE_SOLUTIONS
        assert game.state_color == (255, 165, 0)  # AMBER
        assert game.finalized is True

    def test_finalize_single_solution(self):
        """Finalize valid puzzle should set SINGLE_SOLUTION state"""
        game = SudokuGame()
        # Use a heavily constrained puzzle to avoid timeout
        game.grid = [
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
        game.finalize_puzzle()

        assert game.puzzle_state == PuzzleState.SINGLE_SOLUTION
        assert game.state_color == (0, 200, 0)  # GREEN
        assert game.finalized is True
        assert game.state_solution_grid is not None


class TestFrozenCells:
    """Test frozen cell enforcement"""

    def test_frozen_cells_prevent_entry(self):
        """Cannot modify frozen cells via keyboard"""
        game = SudokuGame()
        # Set and freeze cell
        game.grid[0][0] = 5
        game.frozen_cells.add((0, 0))
        game.selected_cell = (0, 0)

        # Try to change frozen cell
        game.handle_key(pygame.K_3)  # Press '3'

        assert game.grid[0][0] == 5  # Should remain unchanged
        assert "locked" in game.message.lower()

    def test_unfrozen_cells_allow_entry(self):
        """Can modify unfrozen cells"""
        game = SudokuGame()
        game.selected_cell = (0, 0)

        # Enter number
        game.handle_key(pygame.K_7)

        assert game.grid[0][0] == 7

    def test_frozen_cells_cleared_on_clear_grid(self):
        """Frozen cells reset when grid cleared"""
        game = SudokuGame()
        game.frozen_cells.add((0, 0))
        game.finalized = True

        game.clear_grid()

        assert len(game.frozen_cells) == 0
        assert game.finalized is False


class TestStateTransitions:
    """Test state changes during gameplay"""

    def test_state_resets_on_clear(self):
        """State resets to default when grid cleared"""
        game = SudokuGame()
        # Set custom state
        game.puzzle_state = PuzzleState.SINGLE_SOLUTION
        game.finalized = True
        game.state_color = (0, 200, 0)

        game.clear_grid()

        assert game.puzzle_state == PuzzleState.MULTIPLE_SOLUTIONS
        assert game.finalized is False
        assert game.state_color == (255, 165, 0)

    def test_state_message_updated(self):
        """State message reflects validation result"""
        game = SudokuGame()
        game.grid[0][0] = 1
        game.grid[0][1] = 1

        game.finalize_puzzle()

        assert game.state_message == game.message
        assert len(game.state_message) > 0
