"""
Sudoku Game - Solver Algorithm

Pure algorithm logic (no Pygame dependency).
- Backtracking solver
- Validation logic
- Puzzle generation
- Puzzle I/O (save/load)
"""

import json
import random
from pathlib import Path


def generate_complete_grid():
    """Generate a complete, valid 9x9 Sudoku grid (all cells filled).

    Uses randomized backtracking to create a unique solution.

    Returns: 9x9 grid as list of lists
    """
    grid = [[0 for _ in range(9)] for _ in range(9)]

    def is_valid(row, col, num):
        # Check row
        if num in grid[row]:
            return False
        # Check column
        if num in [grid[i][col] for i in range(9)]:
            return False
        # Check 3x3 box
        box_row, box_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(box_row, box_row + 3):
            for j in range(box_col, box_col + 3):
                if grid[i][j] == num:
                    return False
        return True

    def solve():
        for row in range(9):
            for col in range(9):
                if grid[row][col] == 0:
                    # Try numbers in random order
                    numbers = list(range(1, 10))
                    random.shuffle(numbers)
                    for num in numbers:
                        if is_valid(row, col, num):
                            grid[row][col] = num
                            if solve():
                                return True
                            grid[row][col] = 0
                    return False
        return True

    solve()
    return grid


def generate_puzzle(difficulty='medium'):
    """Generate a puzzle by removing clues from a complete grid.

    Args:
        difficulty: 'easy' (15 clues), 'medium' (27 clues), 'hard' (40 clues)

    Returns: (puzzle_grid, solution_grid)
    """
    solution = generate_complete_grid()
    puzzle = [row[:] for row in solution]  # Deep copy

    # Difficulty mapping: (clues_to_keep)
    difficulty_map = {
        'easy': 15,
        'medium': 27,
        'hard': 40
    }

    clues_to_keep = difficulty_map.get(difficulty, 27)
    clues_removed = 0
    target_removes = 81 - clues_to_keep

    # Remove clues randomly
    while clues_removed < target_removes:
        row = random.randint(0, 8)
        col = random.randint(0, 8)
        if puzzle[row][col] != 0:
            puzzle[row][col] = 0
            clues_removed += 1

    return puzzle, solution


def save_puzzle(puzzle, solution, difficulty, filepath):
    """Save puzzle to JSON file.

    Args:
        puzzle: 9x9 grid with 0s for empty cells
        solution: 9x9 grid with complete solution
        difficulty: 'easy', 'medium', or 'hard'
        filepath: path to save file
    """
    import datetime

    data = {
        'puzzle': puzzle,
        'solution': solution,
        'difficulty': difficulty,
        'clues': sum(1 for row in puzzle for cell in row if cell != 0),
        'created': datetime.datetime.now().isoformat()
    }

    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)


def load_puzzle(filepath):
    """Load puzzle from JSON file.

    Returns: (puzzle_grid, solution_grid, difficulty, clues_count) or (None, None, None, None) on error
    """
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)

        # Validate data
        if not isinstance(data.get('puzzle'), list) or len(data['puzzle']) != 9:
            return None, None, None, None

        puzzle = data['puzzle']
        solution = data.get('solution', puzzle)  # Fallback if no solution
        difficulty = data.get('difficulty', 'unknown')
        clues = data.get('clues', sum(1 for row in puzzle for cell in row if cell != 0))

        return puzzle, solution, difficulty, clues
    except Exception as e:
        print(f"Error loading puzzle: {e}")
        return None, None, None, None


class SudokuSolver:
    """Pure Sudoku algorithm solver (no Pygame dependency)."""

    def __init__(self, grid):
        """Initialize solver with a grid.

        Args:
            grid: 9x9 grid as list of lists
        """
        self.grid = grid

    def is_valid_placement(self, row, col, num):
        """Check if placing num at (row, col) is valid.

        Validates against row, column, and 3x3 box constraints.

        Args:
            row: Row index (0-8)
            col: Column index (0-8)
            num: Number to place (1-9, or 0 for empty)

        Returns: True if valid, False otherwise
        """
        if num == 0:
            return True

        # Check row
        for j in range(9):
            if j != col and self.grid[row][j] == num:
                return False

        # Check column
        for i in range(9):
            if i != row and self.grid[i][col] == num:
                return False

        # Check 3x3 box
        box_row, box_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(box_row, box_row + 3):
            for j in range(box_col, box_col + 3):
                if (i, j) != (row, col) and self.grid[i][j] == num:
                    return False

        return True

    def get_candidates(self, row, col):
        """Get list of valid numbers for a cell.

        Args:
            row: Row index (0-8)
            col: Column index (0-8)

        Returns: List of valid numbers (1-9) for this cell
        """
        candidates = []
        for num in range(1, 10):
            if self.is_valid_placement(row, col, num):
                candidates.append(num)
        return candidates

    def find_empty_cell(self):
        """Find the next empty cell (value 0).

        Scans left-to-right, top-to-bottom.

        Returns: (row, col) tuple or None if no empty cells
        """
        for i in range(9):
            for j in range(9):
                if self.grid[i][j] == 0:
                    return (i, j)
        return None

    def find_errors(self):
        """Find all cells with conflicts.

        A cell has a conflict if its value violates Sudoku rules
        (duplicate in row, column, or box).

        Returns: Set of (row, col) tuples with conflicts
        """
        errors = set()

        for i in range(9):
            for j in range(9):
                if self.grid[i][j] != 0:
                    if not self.is_valid_placement(i, j, self.grid[i][j]):
                        errors.add((i, j))

        return errors

    def is_complete(self):
        """Check if grid is completely filled (no empty cells).

        Returns: True if all cells filled, False if any cell is 0
        """
        for i in range(9):
            for j in range(9):
                if self.grid[i][j] == 0:
                    return False
        return True

    def solve_backtrack(self):
        """Standard backtracking solver (no animation, instant solve).

        Fills the grid in-place. Returns True if solvable, False otherwise.

        Returns: True if puzzle solved, False if unsolvable
        """
        empty = self.find_empty_cell()
        if not empty:
            return True

        row, col = empty
        for num in range(1, 10):
            if self.is_valid_placement(row, col, num):
                self.grid[row][col] = num
                if self.solve_backtrack():
                    return True
                self.grid[row][col] = 0

        return False

    def solve_with_steps(self):
        """Generator-based backtracking solver for step-by-step animation.

        Yields after each step for animation/rendering.
        Yields tuples of (current_cell, candidates) for UI to display.

        Yields: None after each logical step (attempting a number, backtracking, etc.)

        Returns: True if solved, False if unsolvable
        """

        def backtrack(step_callback=None):
            # Find empty cell
            empty = self.find_empty_cell()
            if not empty:
                return True

            row, col = empty

            # Yield step info (current cell, candidates)
            candidates = self.get_candidates(row, col)
            if step_callback:
                step_callback(row, col, candidates)
            yield

            # Try numbers 1-9
            for num in candidates:
                self.grid[row][col] = num
                yield  # Show filled cell

                if (yield from backtrack(step_callback)):
                    return True

                self.grid[row][col] = 0  # Backtrack
                yield  # Show backtrack

            return False

        result = yield from backtrack()
        return result
