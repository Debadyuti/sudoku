"""Test suite for Sudoku solver module (pure algorithm, no Pygame)."""

import sys
import pytest
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from solver import (
    SudokuSolver,
    generate_complete_grid,
    generate_puzzle,
    save_puzzle,
    load_puzzle,
)


class TestSudokuSolver:
    """Test SudokuSolver validation and solving logic."""

    @pytest.fixture
    def empty_grid(self):
        """Empty 9x9 grid."""
        return [[0 for _ in range(9)] for _ in range(9)]

    @pytest.fixture
    def valid_grid(self):
        """A valid grid with some filled cells."""
        grid = [[0 for _ in range(9)] for _ in range(9)]
        grid[0][0] = 5
        grid[0][1] = 3
        grid[1][0] = 6
        return grid

    @pytest.fixture
    def complete_grid(self):
        """A complete valid Sudoku grid."""
        return [
            [5, 3, 4, 6, 7, 8, 9, 1, 2],
            [6, 7, 2, 1, 9, 5, 3, 4, 8],
            [1, 9, 8, 3, 4, 2, 5, 6, 7],
            [8, 5, 9, 7, 6, 1, 4, 2, 3],
            [4, 2, 6, 8, 5, 3, 7, 9, 1],
            [7, 1, 3, 9, 2, 4, 8, 5, 6],
            [9, 6, 1, 5, 3, 7, 2, 8, 4],
            [2, 8, 7, 4, 1, 9, 6, 3, 5],
            [3, 4, 5, 2, 8, 6, 1, 7, 9],
        ]

    def test_solver_initialization(self, empty_grid):
        """Test SudokuSolver initializes correctly."""
        solver = SudokuSolver(empty_grid)
        assert solver.grid == empty_grid

    def test_is_valid_placement_empty_cell(self, empty_grid):
        """Test that 0 is always valid (empty cell)."""
        solver = SudokuSolver(empty_grid)
        assert solver.is_valid_placement(0, 0, 0) is True

    def test_is_valid_placement_valid_number(self, empty_grid):
        """Test valid number placement in empty grid."""
        solver = SudokuSolver(empty_grid)
        assert solver.is_valid_placement(0, 0, 5) is True
        assert solver.is_valid_placement(0, 0, 1) is True
        assert solver.is_valid_placement(0, 0, 9) is True

    def test_is_valid_placement_duplicate_row(self, valid_grid):
        """Test that duplicate in row is rejected."""
        solver = SudokuSolver(valid_grid)
        # Row 0 has 5, 3, 6 (col 1)
        assert solver.is_valid_placement(0, 2, 5) is False  # 5 already in row
        assert solver.is_valid_placement(0, 2, 3) is False  # 3 already in row

    def test_is_valid_placement_duplicate_column(self, valid_grid):
        """Test that duplicate in column is rejected."""
        solver = SudokuSolver(valid_grid)
        # Col 0 has 5, 6
        assert solver.is_valid_placement(2, 0, 5) is False
        assert solver.is_valid_placement(2, 0, 6) is False

    def test_is_valid_placement_duplicate_box(self):
        """Test that duplicate in 3x3 box is rejected."""
        grid = [[0 for _ in range(9)] for _ in range(9)]
        grid[0][0] = 5
        solver = SudokuSolver(grid)
        # 5 is in box (0,0). (1,1) is also in that box
        assert solver.is_valid_placement(1, 1, 5) is False
        # (2,2) is also in that box
        assert solver.is_valid_placement(2, 2, 5) is False
        # (3,0) is NOT in that box, but is in same column (col 0) as (0,0)
        assert solver.is_valid_placement(3, 0, 5) is False
        # (0,3) is NOT in box (0,0) and not in same col, but IS in same row (row 0)
        assert solver.is_valid_placement(0, 3, 5) is False
        # (4,4) is in box (1,1), different row, different col, different box
        assert solver.is_valid_placement(4, 4, 5) is True
        # (3,3) is in box (1,1), also different from everything
        assert solver.is_valid_placement(3, 3, 5) is True

    def test_get_candidates_empty_grid(self, empty_grid):
        """Test candidates in completely empty grid."""
        solver = SudokuSolver(empty_grid)
        candidates = solver.get_candidates(0, 0)
        assert len(candidates) == 9
        assert sorted(candidates) == list(range(1, 10))

    def test_get_candidates_with_constraints(self, valid_grid):
        """Test candidates with some constraints."""
        solver = SudokuSolver(valid_grid)
        # Grid has 5, 3 in row 0 and 6 in column 0
        candidates = solver.get_candidates(0, 3)  # Row 0, col 3
        assert 5 not in candidates
        assert 3 not in candidates
        candidates = solver.get_candidates(3, 0)  # Row 3, col 0
        assert 5 not in candidates
        assert 6 not in candidates

    def test_find_empty_cell_exists(self, valid_grid):
        """Test finding empty cell."""
        solver = SudokuSolver(valid_grid)
        empty = solver.find_empty_cell()
        assert empty is not None
        row, col = empty
        assert valid_grid[row][col] == 0

    def test_find_empty_cell_scans_left_to_right(self, valid_grid):
        """Test that find_empty_cell scans left-to-right, top-to-bottom."""
        solver = SudokuSolver(valid_grid)
        empty = solver.find_empty_cell()
        # Should find (0, 2) first since that's leftmost-topmost empty
        assert empty == (0, 2)

    def test_find_empty_cell_none(self, complete_grid):
        """Test find_empty_cell returns None when grid is full."""
        solver = SudokuSolver(complete_grid)
        empty = solver.find_empty_cell()
        assert empty is None

    def test_find_errors_none(self, complete_grid):
        """Test find_errors returns no errors for valid grid."""
        solver = SudokuSolver(complete_grid)
        errors = solver.find_errors()
        assert len(errors) == 0

    def test_find_errors_duplicate_row(self):
        """Test find_errors detects duplicates in row."""
        grid = [[0 for _ in range(9)] for _ in range(9)]
        grid[0][0] = 5
        grid[0][1] = 5  # Duplicate
        solver = SudokuSolver(grid)
        errors = solver.find_errors()
        assert len(errors) >= 1
        assert (0, 0) in errors or (0, 1) in errors

    def test_is_complete_false(self, valid_grid):
        """Test is_complete returns False for incomplete grid."""
        solver = SudokuSolver(valid_grid)
        assert solver.is_complete() is False

    def test_is_complete_true(self, complete_grid):
        """Test is_complete returns True for full grid."""
        solver = SudokuSolver(complete_grid)
        assert solver.is_complete() is True

    def test_solve_backtrack_complete_grid(self, complete_grid):
        """Test backtrack solver on already-complete grid."""
        grid_copy = [row[:] for row in complete_grid]
        solver = SudokuSolver(grid_copy)
        result = solver.solve_backtrack()
        assert result is True
        assert solver.is_complete() is True

    def test_solve_backtrack_solvable_puzzle(self):
        """Test backtrack solver on a simple solvable puzzle."""
        grid = [[0 for _ in range(9)] for _ in range(9)]
        # Place a few clues to make it solvable
        grid[0][0] = 5
        grid[0][1] = 3
        grid[1][0] = 6
        solver = SudokuSolver(grid)
        result = solver.solve_backtrack()
        assert result is True
        assert solver.is_complete() is True

    def test_solve_with_steps_generator(self, empty_grid):
        """Test solve_with_steps generator interface."""
        solver = SudokuSolver(empty_grid)
        gen = solver.solve_with_steps()

        # Generator should exist
        assert gen is not None

        # Take a few steps
        steps_taken = 0
        for _ in range(5):
            try:
                next(gen)
                steps_taken += 1
            except StopIteration:
                break

        assert steps_taken > 0


class TestPuzzleGeneration:
    """Test puzzle generation functions."""

    def test_generate_complete_grid(self):
        """Test complete grid generation."""
        grid = generate_complete_grid()
        assert len(grid) == 9
        assert all(len(row) == 9 for row in grid)

        # Check all cells filled
        assert all(grid[i][j] != 0 for i in range(9) for j in range(9))

        # Check valid (no duplicates)
        solver = SudokuSolver(grid)
        errors = solver.find_errors()
        assert len(errors) == 0

    def test_generate_complete_grid_unique(self):
        """Test that multiple generated grids are different."""
        grid1 = generate_complete_grid()
        grid2 = generate_complete_grid()
        # Very unlikely to generate same grid twice
        assert grid1 != grid2

    def test_generate_puzzle_easy(self):
        """Test puzzle generation for easy difficulty."""
        puzzle, solution = generate_puzzle("easy")

        # Check sizes
        assert len(puzzle) == 9
        assert len(solution) == 9

        # Check clue count for easy (15 clues expected)
        clues = sum(1 for row in puzzle for cell in row if cell != 0)
        assert 10 <= clues <= 20  # Allow some variance

        # Solution should be complete
        solver = SudokuSolver(solution)
        assert solver.is_complete() is True

    def test_generate_puzzle_medium(self):
        """Test puzzle generation for medium difficulty."""
        puzzle, solution = generate_puzzle("medium")
        clues = sum(1 for row in puzzle for cell in row if cell != 0)
        assert 20 <= clues <= 35  # Medium has more clues than easy

    def test_generate_puzzle_hard(self):
        """Test puzzle generation for hard difficulty."""
        puzzle, solution = generate_puzzle("hard")
        clues = sum(1 for row in puzzle for cell in row if cell != 0)
        assert 30 <= clues <= 81  # Hard has even more clues

    def test_generate_puzzle_invalid_difficulty(self):
        """Test puzzle generation with invalid difficulty."""
        # Should default to medium
        puzzle, solution = generate_puzzle("unknown")
        clues = sum(1 for row in puzzle for cell in row if cell != 0)
        assert 20 <= clues <= 35


class TestPuzzleIO:
    """Test puzzle save/load functions."""

    @pytest.fixture
    def temp_puzzle_file(self, tmp_path):
        """Temporary file for puzzle save/load."""
        return tmp_path / "test_puzzle.json"

    def test_save_puzzle(self, temp_puzzle_file):
        """Test saving puzzle to file."""
        puzzle = [[i + 1 if j == 0 else 0 for j in range(9)] for i in range(9)]
        solution = [[i + 1 for j in range(9)] for i in range(9)]

        save_puzzle(puzzle, solution, "easy", str(temp_puzzle_file))
        assert temp_puzzle_file.exists()

    def test_load_puzzle_roundtrip(self, temp_puzzle_file):
        """Test save/load roundtrip."""
        puzzle, solution = generate_puzzle("medium")
        clues = sum(1 for row in puzzle for cell in row if cell != 0)

        save_puzzle(puzzle, solution, "medium", str(temp_puzzle_file))
        loaded_puzzle, loaded_solution, difficulty, loaded_clues, frozen_cells = load_puzzle(
            str(temp_puzzle_file)
        )

        assert loaded_puzzle == puzzle
        assert loaded_solution == solution
        assert difficulty == "medium"
        assert loaded_clues == clues

    def test_load_puzzle_nonexistent(self):
        """Test loading nonexistent puzzle."""
        puzzle, solution, difficulty, clues, frozen_cells = load_puzzle("/nonexistent/path/puzzle.json")
        assert puzzle is None
        assert solution is None
        assert difficulty is None
        assert clues is None
        assert frozen_cells is None

    def test_load_puzzle_invalid_json(self, tmp_path):
        """Test loading invalid JSON file."""
        bad_file = tmp_path / "bad.json"
        bad_file.write_text("{ invalid json }")

        puzzle, solution, difficulty, clues, frozen_cells = load_puzzle(str(bad_file))
        assert puzzle is None
