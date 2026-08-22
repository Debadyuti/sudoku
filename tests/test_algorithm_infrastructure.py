"""
Phase 8.1: Algorithm Infrastructure Tests

Tests for algorithm selection framework:
- SolveAlgorithm enum
- Algorithm state in SudokuGame
- Algorithm selection via menu
- Algorithm stats tracking
- UI display of algorithm
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
from solver import SolveAlgorithm, generate_puzzle_with_uniqueness
from sudoku_game import SudokuGame


class TestSolveAlgorithmEnum:
    """Test SolveAlgorithm enum exists and has required values"""

    def test_enum_exists(self):
        """SolveAlgorithm enum can be imported"""
        assert SolveAlgorithm is not None

    def test_enum_values(self):
        """SolveAlgorithm has BACKTRACK, CONSTRAINT_PROPAGATION, HYBRID"""
        assert hasattr(SolveAlgorithm, 'BACKTRACK')
        assert hasattr(SolveAlgorithm, 'CONSTRAINT_PROPAGATION')
        assert hasattr(SolveAlgorithm, 'HYBRID')

    def test_enum_values_accessible(self):
        """Can access all algorithm values"""
        assert SolveAlgorithm.BACKTRACK.value == "backtrack"
        assert SolveAlgorithm.CONSTRAINT_PROPAGATION.value == "constraint_prop"
        assert SolveAlgorithm.HYBRID.value == "hybrid"


class TestAlgorithmState:
    """Test algorithm state in SudokuGame"""

    def test_default_algorithm_is_hybrid(self):
        """Default algorithm selection is HYBRID"""
        game = SudokuGame()
        assert game.algorithm_selected == SolveAlgorithm.HYBRID

    def test_algorithm_stats_initialized(self):
        """Algorithm stats dict has required keys"""
        game = SudokuGame()
        assert isinstance(game.algorithm_stats, dict)
        assert 'name' in game.algorithm_stats
        assert 'iterations' in game.algorithm_stats
        assert 'backtracks' in game.algorithm_stats
        assert 'constraints_applied' in game.algorithm_stats
        assert 'time_ms' in game.algorithm_stats

    def test_algorithm_stats_initial_values(self):
        """Algorithm stats have correct initial values"""
        game = SudokuGame()
        assert game.algorithm_stats['name'] == 'Hybrid'
        assert game.algorithm_stats['iterations'] == 0
        assert game.algorithm_stats['backtracks'] == 0
        assert game.algorithm_stats['constraints_applied'] == 0
        assert game.algorithm_stats['time_ms'] == 0

    def test_can_change_algorithm_selected(self):
        """Can change algorithm_selected value"""
        game = SudokuGame()
        game.algorithm_selected = SolveAlgorithm.BACKTRACK
        assert game.algorithm_selected == SolveAlgorithm.BACKTRACK

        game.algorithm_selected = SolveAlgorithm.CONSTRAINT_PROPAGATION
        assert game.algorithm_selected == SolveAlgorithm.CONSTRAINT_PROPAGATION


class TestAlgorithmMenuActions:
    """Test algorithm selection via menu"""

    def test_menu_action_backtrack(self):
        """Menu action switches to BACKTRACK algorithm"""
        game = SudokuGame()
        game._process_menu_action(('edit_menu', 1))
        assert game.algorithm_selected == SolveAlgorithm.BACKTRACK
        assert "Backtracking" in game.message

    def test_menu_action_constraint(self):
        """Menu action switches to CONSTRAINT_PROPAGATION algorithm"""
        game = SudokuGame()
        game._process_menu_action(('edit_menu', 2))
        assert game.algorithm_selected == SolveAlgorithm.CONSTRAINT_PROPAGATION
        assert "Constraint Propagation" in game.message

    def test_menu_action_hybrid(self):
        """Menu action switches to HYBRID algorithm"""
        game = SudokuGame()
        game.algorithm_selected = SolveAlgorithm.BACKTRACK  # Change from default
        game._process_menu_action(('edit_menu', 3))
        assert game.algorithm_selected == SolveAlgorithm.HYBRID
        assert "Hybrid" in game.message

    def test_menu_action_backtrack_clears_error_state(self):
        """Switching algorithm doesn't affect error cells"""
        game = SudokuGame()
        game.error_cells.add((0, 0))
        initial_errors = game.error_cells.copy()

        game._process_menu_action(('edit_menu', 1))

        # Error state should remain (menu action doesn't clear errors)
        assert game.error_cells == initial_errors


class TestAlgorithmStats:
    """Test algorithm statistics tracking"""

    def test_update_algorithm_stats_backtrack(self):
        """Stats updated correctly for backtrack algorithm"""
        game = SudokuGame()
        game.algorithm_selected = SolveAlgorithm.BACKTRACK
        game.step_count = 42
        game.backtrack_count = 5
        game.solver_final_time = 1234

        game.update_algorithm_stats()

        assert game.algorithm_stats['name'] == 'Backtrack'
        assert game.algorithm_stats['iterations'] == 42
        assert game.algorithm_stats['backtracks'] == 5
        assert game.algorithm_stats['time_ms'] == 1234

    def test_update_algorithm_stats_constraint(self):
        """Stats updated correctly for constraint propagation algorithm"""
        game = SudokuGame()
        game.algorithm_selected = SolveAlgorithm.CONSTRAINT_PROPAGATION
        game.step_count = 30
        game.backtrack_count = 2
        game.solver_final_time = 800

        game.update_algorithm_stats()

        assert 'Constraint' in game.algorithm_stats['name']
        assert game.algorithm_stats['iterations'] == 30
        assert game.algorithm_stats['backtracks'] == 2
        assert game.algorithm_stats['time_ms'] == 800

    def test_update_algorithm_stats_hybrid(self):
        """Stats updated correctly for hybrid algorithm"""
        game = SudokuGame()
        game.algorithm_selected = SolveAlgorithm.HYBRID
        game.step_count = 50
        game.backtrack_count = 8
        game.solver_final_time = 2000

        game.update_algorithm_stats()

        assert game.algorithm_stats['name'] == 'Hybrid'
        assert game.algorithm_stats['iterations'] == 50
        assert game.algorithm_stats['backtracks'] == 8
        assert game.algorithm_stats['time_ms'] == 2000

    def test_update_algorithm_stats_with_none_time(self):
        """Stats handle None solver_final_time gracefully"""
        game = SudokuGame()
        game.solver_final_time = None
        game.step_count = 10

        game.update_algorithm_stats()

        assert game.algorithm_stats['time_ms'] == 0


class TestAlgorithmRouting:
    """Test algorithm routing in solve_puzzle"""

    def test_solve_with_backtrack_algorithm(self):
        """solve_puzzle with BACKTRACK algorithm executes"""
        game = SudokuGame()
        game.algorithm_selected = SolveAlgorithm.BACKTRACK

        # Set up simple puzzle
        puzzle, solution, state, msg, color = generate_puzzle_with_uniqueness('easy')
        game.grid = puzzle

        # Call solve (should use backtrack path)
        game.solve_puzzle(animated=False)

        # Should complete without error
        assert game.solver_final_time is not None

    def test_solve_with_constraint_algorithm(self):
        """solve_puzzle with CONSTRAINT_PROPAGATION algorithm executes"""
        game = SudokuGame()
        game.algorithm_selected = SolveAlgorithm.CONSTRAINT_PROPAGATION

        # Set up simple puzzle
        puzzle, solution, state, msg, color = generate_puzzle_with_uniqueness('easy')
        game.grid = puzzle

        # Call solve (should fall back to backtrack for now)
        game.solve_puzzle(animated=False)

        # Should complete without error
        assert game.solver_final_time is not None

    def test_solve_with_hybrid_algorithm(self):
        """solve_puzzle with HYBRID algorithm executes"""
        game = SudokuGame()
        game.algorithm_selected = SolveAlgorithm.HYBRID

        # Set up simple puzzle
        puzzle, solution, state, msg, color = generate_puzzle_with_uniqueness('easy')
        game.grid = puzzle

        # Call solve (should fall back to backtrack for now)
        game.solve_puzzle(animated=False)

        # Should complete without error
        assert game.solver_final_time is not None

    def test_stats_updated_after_solving(self):
        """Algorithm stats updated when solving completes"""
        game = SudokuGame()
        game.algorithm_selected = SolveAlgorithm.BACKTRACK

        # Set up simple puzzle
        puzzle, solution, state, msg, color = generate_puzzle_with_uniqueness('easy')
        game.grid = puzzle

        # Solve puzzle
        game.solve_puzzle(animated=False)

        # Stats should be updated
        assert game.algorithm_stats['name'] == 'Backtrack'
        assert game.algorithm_stats['iterations'] > 0
        assert game.algorithm_stats['time_ms'] > 0


class TestAlgorithmSwitching:
    """Test switching between algorithms"""

    def test_switch_algorithms_between_puzzles(self):
        """Can switch algorithms between different puzzle solves"""
        game = SudokuGame()

        # Solve with backtrack
        puzzle1, solution1, _, _, _ = generate_puzzle_with_uniqueness('easy')
        game.grid = puzzle1
        game.algorithm_selected = SolveAlgorithm.BACKTRACK
        game.solve_puzzle(animated=False)
        first_algo = game.algorithm_stats['name']

        # Clear and solve with hybrid
        game.clear_grid()
        puzzle2, solution2, _, _, _ = generate_puzzle_with_uniqueness('easy')
        game.grid = puzzle2
        game.algorithm_selected = SolveAlgorithm.HYBRID
        game.solve_puzzle(animated=False)
        second_algo = game.algorithm_stats['name']

        # Should have used different algorithms
        assert first_algo == 'Backtrack'
        assert second_algo == 'Hybrid'

    def test_algorithm_changes_dont_affect_grid(self):
        """Changing algorithm doesn't modify puzzle grid"""
        game = SudokuGame()
        puzzle, _, _, _, _ = generate_puzzle_with_uniqueness('easy')
        game.grid = puzzle
        original_grid = [row[:] for row in game.grid]

        # Change algorithm
        game.algorithm_selected = SolveAlgorithm.BACKTRACK
        game._process_menu_action(('edit_menu', 1))

        # Grid should be unchanged
        assert game.grid == original_grid


class TestAlgorithmIntegration:
    """Integration tests for algorithm infrastructure"""

    def test_complete_workflow_with_algorithm_selection(self):
        """Complete workflow: Select algorithm → Generate puzzle → Solve → Check stats"""
        game = SudokuGame()

        # Select algorithm
        game.algorithm_selected = SolveAlgorithm.HYBRID

        # Generate puzzle
        puzzle, solution, _, _, _ = generate_puzzle_with_uniqueness('medium')
        game.grid = puzzle

        # Solve
        game.solve_puzzle(animated=False)

        # Verify everything
        assert game.algorithm_selected == SolveAlgorithm.HYBRID
        assert game.algorithm_stats['name'] == 'Hybrid'
        assert game.algorithm_stats['iterations'] > 0
        assert game.solver_final_time is not None

    def test_algorithm_persistence_across_operations(self):
        """Selected algorithm persists across multiple operations"""
        game = SudokuGame()

        # Select algorithm
        game._process_menu_action(('edit_menu', 1))
        assert game.algorithm_selected == SolveAlgorithm.BACKTRACK

        # Clear grid (shouldn't change algorithm)
        game.grid[0][0] = 5
        game.clear_grid()
        assert game.algorithm_selected == SolveAlgorithm.BACKTRACK

        # Generate new puzzle (shouldn't change algorithm)
        puzzle, _, _, _, _ = generate_puzzle_with_uniqueness('easy')
        game.grid = puzzle
        assert game.algorithm_selected == SolveAlgorithm.BACKTRACK
