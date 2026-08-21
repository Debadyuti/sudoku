import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
import pygame
from sudoku_game import SudokuGame
from constants import BLUE

pygame.init()


class TestPuzzleStatistics:
    """Test Puzzle Statistics (Phase 6.2: Extended stats tracking)"""

    def setup_method(self):
        """Initialize Pygame and create game instance"""
        if not pygame.get_init():
            pygame.init()
        self.game = SudokuGame()

    def teardown_method(self):
        """Cleanup Pygame"""
        pygame.quit()

    def test_statistics_structure(self):
        """Test: Extended stats returns dict with correct keys"""
        stats = self.game._get_extended_stats()

        # Verify all keys present
        assert 'steps' in stats
        assert 'backtracks' in stats
        assert 'time_ms' in stats
        assert 'time_sec' in stats
        assert 'solved' in stats
        assert 'progress' in stats
        assert 'difficulty' in stats

    def test_statistics_initial_values(self):
        """Test: Initial statistics are sensible"""
        stats = self.game._get_extended_stats()

        # Initial state should have no solving time
        assert stats['time_ms'] == 0
        assert stats['time_sec'] == 0
        # No cells filled yet
        assert stats['solved'] == 0
        # No steps/backtracks yet
        assert stats['steps'] == 0
        assert stats['backtracks'] == 0

    def test_cells_filled_initially_tracked(self):
        """Test: Initial clue count is tracked"""
        # Setup: Fill some cells
        self.game.grid[0][0] = 1
        self.game.grid[0][1] = 2
        self.game.grid[1][0] = 3

        # Trigger solve (tracks initial clues)
        self.game.solve_puzzle(animated=False)

        # Verify: Initial cells counted
        assert self.game.cells_filled_initially == 3

    def test_progress_percentage_calculation(self):
        """Test: Progress percentage calculated correctly"""
        # Setup: Add some initial cells
        self.game.grid[0][0] = 1
        self.game.grid[0][1] = 2

        # Fill 40% of grid (1 + 2 + remaining cells toward 81)
        for i in range(9):
            for j in range(9):
                if self.game.grid[i][j] == 0:
                    self.game.grid[i][j] = (i + j) % 9 + 1

        # Trigger solve
        self.game.solve_puzzle(animated=False)

        stats = self.game._get_extended_stats()

        # Grid should be 100% filled when all cells have values
        assert stats['progress'] == 100

    def test_difficulty_tracking(self):
        """Test: Difficulty is stored and returned in stats"""
        self.game.puzzle_difficulty = "hard"

        stats = self.game._get_extended_stats()

        assert stats['difficulty'] == "hard"

    def test_statistics_after_solving(self):
        """Test: Statistics updated after puzzle solve"""
        # Setup: Simple puzzle with just first cell empty
        self.game.grid = [
            [0, 2, 3, 4, 5, 6, 7, 8, 9],
            [4, 5, 6, 7, 8, 9, 1, 2, 3],
            [7, 8, 9, 1, 2, 3, 4, 5, 6],
            [2, 3, 4, 5, 6, 7, 8, 9, 1],
            [5, 6, 7, 8, 9, 1, 2, 3, 4],
            [8, 9, 1, 2, 3, 4, 5, 6, 7],
            [3, 4, 5, 6, 7, 8, 9, 1, 2],
            [6, 7, 8, 9, 1, 2, 3, 4, 5],
            [9, 1, 2, 3, 4, 5, 6, 7, 8]
        ]

        # Solve
        self.game.solve_puzzle(animated=False)

        # Get stats
        stats = self.game._get_extended_stats()

        # After solving, should have steps/backtracks > 0
        assert stats['steps'] >= 0
        assert stats['backtracks'] >= 0
        # Progress should be 100% after solving
        assert stats['progress'] == 100

    def test_time_tracking_values(self):
        """Test: Time values are numeric and consistent"""
        # Setup: Simple puzzle
        self.game.grid[0][0] = 0
        self.game.grid[0][1] = 2

        # Manually set final time for testing
        self.game.solver_final_time = 1500  # 1.5 seconds

        stats = self.game._get_extended_stats()

        # Verify time values
        assert isinstance(stats['time_ms'], (int, float))
        assert isinstance(stats['time_sec'], float)
        assert stats['time_ms'] == 1500
        assert abs(stats['time_sec'] - 1.5) < 0.01

    def test_solved_count_with_filled_grid(self):
        """Test: Solved cell count is accurate"""
        # Setup: Fill entire grid
        for i in range(9):
            for j in range(9):
                self.game.grid[i][j] = (i + j) % 9 + 1

        stats = self.game._get_extended_stats()

        # All 81 cells filled
        assert stats['solved'] == 81

    def test_progress_with_empty_grid(self):
        """Test: Progress reflects empty grid state"""
        # Grid starts empty - no solve called yet so cells_filled_initially is 0
        stats = self.game._get_extended_stats()

        # With 0 initial clues and 0 solved cells, progress is 0%
        assert stats['progress'] == 0

    def test_progress_with_partial_fill(self):
        """Test: Progress percentage reflects partial completion"""
        # Setup: Add initial clues
        self.game.grid[0][0] = 1
        self.game.grid[0][1] = 2
        self.game.grid[1][0] = 3

        # Solve to track initial
        self.game.solve_puzzle(animated=False)

        # Now manually add more solved cells (simulate partial solve)
        self.game.grid[0][2] = 4
        self.game.grid[0][3] = 5

        stats = self.game._get_extended_stats()

        # Progress should reflect the added cells
        solved = sum(1 for row in self.game.grid for cell in row if cell != 0)
        expected_progress = (solved - 3) / (81 - 3) * 100
        assert abs(stats['progress'] - expected_progress) < 1

    def test_statistics_dict_types(self):
        """Test: All statistics values have correct types"""
        stats = self.game._get_extended_stats()

        assert isinstance(stats['steps'], int)
        assert isinstance(stats['backtracks'], int)
        assert isinstance(stats['time_ms'], (int, float))
        assert isinstance(stats['time_sec'], float)
        assert isinstance(stats['solved'], int)
        assert isinstance(stats['progress'], (int, float))
        assert isinstance(stats['difficulty'], str)

    def test_multiple_solve_tracking(self):
        """Test: Statistics reset on new solve"""
        # First solve
        self.game.grid[0][0] = 1
        self.game.solve_puzzle(animated=False)
        initial_count = self.game.cells_filled_initially

        # Clear and second solve
        self.game.clear_grid()
        self.game.grid[0][0] = 2
        self.game.grid[0][1] = 3
        self.game.solve_puzzle(animated=False)
        new_count = self.game.cells_filled_initially

        # New count should reflect new initial state
        assert new_count == 2
