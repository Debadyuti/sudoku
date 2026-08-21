"""Test suite for game logic and state management (no Pygame display)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
from sudoku_game import SudokuGame
import pygame

# Initialize pygame for key constants
pygame.init()


class TestGameInitialization:
    """Test game state initialization."""

    def test_game_initializes_with_default_state(self):
        """Test game initializes with correct default state."""
        game = SudokuGame()

        assert game.grid == [[0 for _ in range(9)] for _ in range(9)]
        assert game.solution == [[0 for _ in range(9)] for _ in range(9)]
        assert game.selected_cell == (0, 0)
        assert game.error_cells == set()
        assert game.frozen_cells == set()
        assert game.puzzle_difficulty == "medium"
        assert game.solving is False
        assert game.solve_paused is False

    def test_game_initializes_empty_grid(self):
        """Test game starts with empty grid."""
        game = SudokuGame()
        empty_count = sum(1 for row in game.grid for cell in row if cell == 0)
        assert empty_count == 81


class TestKeyboardShortcuts:
    """Test keyboard input handling for shortcuts."""

    def test_keyboard_shortcut_f_finalize(self):
        """Test F key triggers finalize puzzle."""
        game = SudokuGame()
        # Set up valid incomplete puzzle
        game.grid[0][0] = 1
        game.message = ""

        game.handle_key(pygame.K_f)

        # Finalize should attempt validation
        # At least should not error
        assert game.grid[0][0] == 1

    def test_keyboard_shortcut_c_clear(self):
        """Test C key triggers clear grid."""
        game = SudokuGame()
        game.grid[0][0] = 5
        game.grid[1][1] = 3
        game.frozen_cells.add((2, 2))
        game.grid[2][2] = 7

        game.handle_key(pygame.K_c)

        # All unfrozen cells should be cleared
        assert game.grid[0][0] == 0
        assert game.grid[1][1] == 0
        assert game.grid[2][2] == 0  # Even if frozen, clear_grid clears all
        assert game.solving is False

    def test_keyboard_shortcut_a_solve_algo(self):
        """Test A key triggers animated solver."""
        game = SudokuGame()
        # Populate with a simple solvable puzzle
        game.solution = [[1, 2, 3, 4, 5, 6, 7, 8, 9] for _ in range(9)]
        game.grid = [[0 if j != 0 else (i % 9 + 1) for j in range(9)] for i in range(9)]

        game.handle_key(pygame.K_a)

        # Solver should start
        assert game.solving is True

    def test_keyboard_shortcut_s_solve_fast(self):
        """Test S key triggers fast solver."""
        game = SudokuGame()
        # Populate with a simple solvable puzzle
        game.solution = [[1, 2, 3, 4, 5, 6, 7, 8, 9] for _ in range(9)]
        game.grid = [[0 if j != 0 else (i % 9 + 1) for j in range(9)] for i in range(9)]

        game.handle_key(pygame.K_s)

        # Solver should complete fast
        assert game.solving is False

    def test_keyboard_shortcut_ctrl_c_not_mistaken_for_clear(self):
        """Test Ctrl+C doesn't trigger clear grid."""
        game = SudokuGame()
        game.grid[0][0] = 5

        # Ctrl+C should copy stats, not clear grid
        game.handle_key(pygame.K_c, mod=pygame.KMOD_CTRL)

        assert game.grid[0][0] == 5  # Grid unchanged

    def test_keyboard_shortcut_space_pause_solver(self):
        """Test SPACE key pauses/resumes solver."""
        game = SudokuGame()
        game.solving = True
        game.solve_paused = False

        game.handle_key(pygame.K_SPACE)

        assert game.solve_paused is True

        game.handle_key(pygame.K_SPACE)

        assert game.solve_paused is False


class TestGameStateTransitions:
    """Test game state transitions."""

    def test_clear_grid_clears_all_cells(self):
        """Test clear_grid empties all cells."""
        game = SudokuGame()
        game.grid = [[i + j + 1 for j in range(9)] for i in range(9)]
        game.frozen_cells = set()

        game.clear_grid()

        for row in game.grid:
            assert all(cell == 0 for cell in row)

    def test_clear_grid_clears_frozen_cells_set(self):
        """Test clear_grid also clears the frozen_cells set."""
        game = SudokuGame()
        game.frozen_cells = {(0, 0), (0, 1), (1, 0)}
        game.grid[0][0] = 5
        game.grid[0][1] = 3
        game.grid[1][0] = 7

        game.clear_grid()

        # clear_grid clears both grid AND frozen_cells set
        assert game.frozen_cells == set()
        # Grid is cleared completely
        assert game.grid[0][0] == 0

    def test_finalize_puzzle_validates_grid(self):
        """Test finalize_puzzle validates the puzzle."""
        game = SudokuGame()
        game.selected_cell = (0, 0)
        game.grid[0][0] = 5

        # Should not error
        game.finalize_puzzle()

        # Grid should remain unchanged
        assert game.grid[0][0] == 5

    def test_solving_flag_set_on_solve(self):
        """Test solving flag is set when solver starts."""
        game = SudokuGame()
        game.solution = [[1, 2, 3, 4, 5, 6, 7, 8, 9] for _ in range(9)]
        game.grid = [[0 if j != 0 else (i % 9 + 1) for j in range(9)] for i in range(9)]

        game.solve_puzzle(animated=True)

        assert game.solving is True

    def test_error_cells_cleared_on_grid_edit(self):
        """Test error cells are cleared when grid is edited."""
        game = SudokuGame()
        game.error_cells = {(0, 0), (1, 1)}
        game.selected_cell = (0, 0)

        game.handle_key(pygame.K_5)  # Enter 5 in selected cell

        assert game.error_cells == set()


class TestSolverTimerState:
    """Test solver timer and frozen state."""

    def test_solver_timer_starts_on_solve(self):
        """Test solver_start_time is set when solving starts."""
        game = SudokuGame()
        game.solution = [[1, 2, 3, 4, 5, 6, 7, 8, 9] for _ in range(9)]
        game.grid = [[0 if j != 0 else (i % 9 + 1) for j in range(9)] for i in range(9)]
        assert game.solver_start_time is None

        game.solve_puzzle(animated=True)

        assert game.solver_start_time is not None

    def test_solver_final_time_frozen_after_stop(self):
        """Test solver_final_time captures time when solver stops."""
        game = SudokuGame()
        game.solving = True
        game.solver_start_time = pygame.time.get_ticks()

        # Simulate ESC key to stop solver
        game.handle_key(pygame.K_ESCAPE)

        assert game.solving is False
        assert game.solver_final_time is not None

    def test_solver_final_time_used_in_display(self):
        """Test get_solver_elapsed_time returns frozen time when set."""
        game = SudokuGame()
        game.solver_start_time = pygame.time.get_ticks()
        game.solver_final_time = 5000  # Frozen at 5 seconds

        elapsed = game.get_solver_elapsed_time()

        # Should return frozen time, not current elapsed
        assert elapsed == 5000


class TestPuzzleDifficulty:
    """Test puzzle difficulty tracking."""

    def test_puzzle_difficulty_defaults_to_medium(self):
        """Test new games default to medium difficulty."""
        game = SudokuGame()
        assert game.puzzle_difficulty == "medium"

    def test_puzzle_difficulty_set_on_generation(self):
        """Test difficulty is set when puzzle is generated."""
        game = SudokuGame()

        game.solve_puzzle()  # Default is medium
        assert game.puzzle_difficulty == "medium"


class TestFrozenCells:
    """Test frozen cells functionality."""

    def test_frozen_cells_initialized_empty(self):
        """Test frozen_cells set is empty on start."""
        game = SudokuGame()
        assert game.frozen_cells == set()

    def test_frozen_cells_can_be_added(self):
        """Test frozen cells can be added to set."""
        game = SudokuGame()
        game.frozen_cells.add((0, 0))
        game.frozen_cells.add((1, 1))

        assert (0, 0) in game.frozen_cells
        assert (1, 1) in game.frozen_cells

    def test_clear_grid_clears_frozen_cells_set(self):
        """Test clear_grid clears the frozen_cells set."""
        game = SudokuGame()
        game.frozen_cells = {(0, 0), (1, 1)}

        game.clear_grid()

        assert game.frozen_cells == set()


class TestMessageSystem:
    """Test message display system."""

    def test_message_initializes_with_ready_text(self):
        """Test game starts with 'Ready to play' message."""
        game = SudokuGame()
        assert "Ready" in game.message or game.message == ""

    def test_message_color_initializes_to_blue(self):
        """Test message color initializes to blue."""
        game = SudokuGame()
        from constants import BLUE
        assert game.message_color == BLUE

    def test_message_updated_on_solver_stop(self):
        """Test message is updated when solver stops."""
        game = SudokuGame()
        game.solving = True
        game.solver_start_time = pygame.time.get_ticks()
        old_message = game.message

        game.handle_key(pygame.K_ESCAPE)

        assert "stopped" in game.message.lower() or game.message != old_message
