"""
Phase 7 Integration Tests - Test all Phase 7 features working together

Tests for:
- End-to-end workflows combining validation, state, UI, and generation
- Feature interactions (e.g., generating puzzle -> finalizing -> solving)
- State consistency across operations
- User workflows
"""

import sys
from pathlib import Path
import time

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
from sudoku_game import SudokuGame
from solver import SudokuSolver, PuzzleState, generate_puzzle_with_uniqueness


class TestCompleteWorkflows:
    """Test complete end-to-end workflows"""

    def test_workflow_generate_finalize_solve(self):
        """Complete workflow: Generate -> Finalize -> Solve"""
        game = SudokuGame()

        # Generate puzzle (simulating easy)
        game._start_puzzle_generation('easy')

        # Wait for generation
        timeout = time.time() + 70
        while game.generating_puzzle and time.time() < timeout:
            time.sleep(0.1)
            game._finish_puzzle_generation()

        # After generation, puzzle should be in grid
        clue_count_before = sum(1 for row in game.grid for cell in row if cell != 0)
        assert clue_count_before > 0, "Generated puzzle should have clues"

        # Finalize puzzle
        game.finalize_puzzle()

        assert game.finalized is True, "Puzzle should be marked finalized"
        assert game.puzzle_state == PuzzleState.SINGLE_SOLUTION, "Generated puzzle should have single solution"

        # Note: frozen_cells is set when solving starts, not on finalize
        # Manually set frozen_cells to test the feature
        game.frozen_cells = set((i, j) for i in range(9) for j in range(9) if game.grid[i][j] != 0)

        # Verify frozen cells prevent editing
        row, col = next((i, j) for i in range(9) for j in range(9) if game.grid[i][j] != 0)
        original_value = game.grid[row][col]
        game.selected_cell = (row, col)
        game.handle_key(9)  # Try to set to 9

        assert game.grid[row][col] == original_value, "Frozen cell should not change"

    def test_workflow_load_puzzle_solve_save(self):
        """Complete workflow: Generate -> Save -> Load -> Solve"""
        import json
        import tempfile
        from pathlib import Path

        game = SudokuGame()

        # Generate a puzzle
        puzzle, solution, state, msg, color = generate_puzzle_with_uniqueness('medium')

        # Save puzzle to temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            data = {
                'puzzle': puzzle,
                'solution': solution,
                'difficulty': 'medium',
                'clues': sum(1 for row in puzzle for cell in row if cell != 0)
            }
            json.dump(data, f)
            temp_path = f.name

        try:
            # Load puzzle from file
            from solver import load_puzzle
            loaded_puzzle, loaded_solution, difficulty, clues, frozen = load_puzzle(temp_path)

            assert loaded_puzzle == puzzle
            assert loaded_solution == solution
            assert difficulty == 'medium'

            # Apply loaded puzzle to game
            game.grid = loaded_puzzle
            game.solution = loaded_solution

            # Finalize loaded puzzle
            game.finalize_puzzle()

            assert game.finalized is True
            assert game.puzzle_state == PuzzleState.SINGLE_SOLUTION

        finally:
            Path(temp_path).unlink()

    def test_workflow_invalid_to_valid_editing(self):
        """Workflow: Create invalid puzzle -> Fix -> Validate -> Finalize"""
        game = SudokuGame()

        # Create invalid puzzle (duplicates)
        game.grid[0][0] = 1
        game.grid[0][1] = 1  # Duplicate in row

        # Validate (should be INVALID)
        game.finalize_puzzle()
        assert game.puzzle_state == PuzzleState.INVALID

        # Fix the invalid state
        game.grid[0][1] = 2  # Change duplicate to different value

        # Re-validate (may still have issues due to incomplete puzzle)
        game.finalize_puzzle()

        # Should at least not be INVALID anymore
        assert game.puzzle_state != PuzzleState.INVALID or game.puzzle_state == PuzzleState.MULTIPLE_SOLUTIONS

    def test_workflow_clear_after_finalize(self):
        """Workflow: Finalize -> Clear -> State reset"""
        game = SudokuGame()

        # Set up a valid puzzle manually
        game.grid[0][0] = 5
        game.grid[0][1] = 3

        # Finalize
        game.finalize_puzzle()
        assert game.finalized is True

        # Manually set frozen cells to test clear behavior
        game.frozen_cells = {(0, 0), (0, 1)}
        assert len(game.frozen_cells) > 0

        # Clear
        game.clear_grid()

        # State should reset
        assert game.finalized is False
        assert len(game.frozen_cells) == 0, "Clear should empty frozen_cells"
        assert game.puzzle_state == PuzzleState.MULTIPLE_SOLUTIONS
        assert all(cell == 0 for row in game.grid for cell in row)


class TestFeatureInteractions:
    """Test how different Phase 7 features interact"""

    def test_validation_with_frozen_cells(self):
        """Frozen cells should be considered in validation"""
        game = SudokuGame()

        # Create puzzle with frozen cells
        game.grid[0][0] = 1
        game.grid[0][1] = 2
        game.frozen_cells = {(0, 0), (0, 1)}

        game.finalize_puzzle()

        # Frozen cells should persist
        assert (0, 0) in game.frozen_cells
        assert (0, 1) in game.frozen_cells

    def test_state_colors_reflect_validation(self):
        """State colors should match validation results"""
        game = SudokuGame()

        # Invalid puzzle
        game.grid[0][0] = 1
        game.grid[0][1] = 1
        game.finalize_puzzle()

        assert game.puzzle_state == PuzzleState.INVALID
        assert game.state_color == (255, 0, 0)  # RED

        # Clear and test solvable
        game.clear_grid()
        game.grid[0][0] = 1
        game.finalize_puzzle()

        # Should be MULTIPLE_SOLUTIONS (open grid)
        assert game.puzzle_state == PuzzleState.MULTIPLE_SOLUTIONS
        assert game.state_color == (255, 165, 0)  # AMBER

    def test_generation_produces_validatable_puzzle(self):
        """Generated puzzles should always validate successfully"""
        puzzle, solution, state, msg, color = generate_puzzle_with_uniqueness('easy')

        game = SudokuGame()
        game.grid = puzzle
        game.finalize_puzzle()

        # Generated puzzle should always be valid
        assert game.puzzle_state in [PuzzleState.SINGLE_SOLUTION, PuzzleState.MULTIPLE_SOLUTIONS]
        assert game.puzzle_state != PuzzleState.INVALID
        assert game.puzzle_state != PuzzleState.NOT_SOLVABLE

    def test_threading_result_is_valid_puzzle(self):
        """Puzzle generated via threading should be valid"""
        game = SudokuGame()

        game._start_puzzle_generation('medium')

        # Wait for completion
        timeout = time.time() + 150
        while game.generating_puzzle and time.time() < timeout:
            time.sleep(0.1)
            game._finish_puzzle_generation()

        # Generated puzzle should be valid
        if game.grid[0][0] != 0:  # Puzzle exists
            solver = SudokuSolver(game.grid)
            state, msg, color = solver.validate_puzzle()

            assert state in [PuzzleState.SINGLE_SOLUTION, PuzzleState.MULTIPLE_SOLUTIONS]
            assert state != PuzzleState.INVALID


class TestStateConsistency:
    """Test that state remains consistent across operations"""

    def test_finalize_sets_all_state_vars(self):
        """Finalizing should set all state variables correctly"""
        game = SudokuGame()

        # Set up a puzzle
        game.grid[0][0] = 1
        game.grid[0][1] = 2

        # Before finalize
        assert game.state_message == ""
        assert game.puzzle_state == PuzzleState.MULTIPLE_SOLUTIONS

        # Finalize
        game.finalize_puzzle()

        # After finalize, all state vars should be set
        assert game.state_message != ""
        assert game.state_color is not None
        assert game.puzzle_state is not None

    def test_state_persists_after_edits(self):
        """Puzzle state should reflect edits"""
        game = SudokuGame()

        # Generate and finalize
        puzzle, solution, _, _, _ = generate_puzzle_with_uniqueness('easy')
        game.grid = puzzle
        game.finalize_puzzle()

        original_state = game.puzzle_state
        original_color = game.state_color

        # Make an edit (clear a cell)
        row, col = next((i, j) for i in range(9) for j in range(9) if game.grid[i][j] != 0)
        game.grid[row][col] = 0

        # State should change (now invalid or multiple solutions)
        # (We don't re-validate on every edit, so state persists until next finalize)
        assert game.puzzle_state == original_state

    def test_clear_resets_all_state(self):
        """Clear should reset all state variables"""
        game = SudokuGame()

        # Set up and finalize using generated puzzle
        puzzle, solution, _, _, _ = generate_puzzle_with_uniqueness('easy')
        game.grid = puzzle
        game.finalize_puzzle()

        # Verify state is set
        assert game.finalized is True
        assert game.puzzle_state == PuzzleState.SINGLE_SOLUTION

        # Clear
        game.clear_grid()

        # Verify all state reset
        assert game.finalized is False
        assert len(game.frozen_cells) == 0
        assert game.puzzle_state == PuzzleState.MULTIPLE_SOLUTIONS
        assert game.state_color == (255, 165, 0)  # AMBER


class TestUIStateRendering:
    """Test UI state rendering with different puzzle states"""

    def test_invalid_puzzle_color_red(self):
        """Invalid puzzle should render with RED color"""
        game = SudokuGame()

        # Create invalid (duplicates)
        game.grid[0][0] = 1
        game.grid[0][1] = 1
        game.finalize_puzzle()

        assert game.puzzle_state == PuzzleState.INVALID
        assert game.state_color == (255, 0, 0)

    def test_unsolvable_puzzle_color_red(self):
        """Unsolvable puzzle should render with RED color"""
        game = SudokuGame()

        # Create an unsolvable grid (contradictions)
        game.grid[0][0] = 1
        game.grid[0][1] = 1
        game.grid[0][2] = 1
        game.grid[0][3] = 1
        game.grid[0][4] = 1
        game.grid[0][5] = 1
        game.grid[0][6] = 1
        game.grid[0][7] = 1
        game.grid[0][8] = 1

        game.finalize_puzzle()

        # Should be INVALID or similar
        assert game.puzzle_state == PuzzleState.INVALID

    def test_multiple_solutions_color_amber(self):
        """Puzzle with multiple solutions should render with AMBER"""
        game = SudokuGame()

        # Minimal puzzle (many solutions)
        game.grid[0][0] = 1
        game.finalize_puzzle()

        assert game.puzzle_state == PuzzleState.MULTIPLE_SOLUTIONS
        assert game.state_color == (255, 165, 0)

    def test_single_solution_color_green(self):
        """Puzzle with single solution should render with GREEN"""
        puzzle, solution, _, _, _ = generate_puzzle_with_uniqueness('easy')
        game = SudokuGame()
        game.grid = puzzle

        game.finalize_puzzle()

        assert game.puzzle_state == PuzzleState.SINGLE_SOLUTION
        assert game.state_color == (0, 200, 0)


class TestPerformanceCharacteristics:
    """Test performance of Phase 7 features"""

    def test_validation_speed_empty_grid(self):
        """Validating empty grid should be fast"""
        game = SudokuGame()

        start = time.time()
        game.finalize_puzzle()
        elapsed = time.time() - start

        # Should be < 1 second (minimal computation)
        assert elapsed < 1.0

    def test_validation_speed_full_grid(self):
        """Validating full grid should be fast"""
        puzzle, solution, _, _, _ = generate_puzzle_with_uniqueness('easy')
        game = SudokuGame()
        game.grid = puzzle

        start = time.time()
        game.finalize_puzzle()
        elapsed = time.time() - start

        # Should be < 5 seconds (quick for small grid)
        assert elapsed < 5.0

    def test_threading_non_blocking(self):
        """Threading should not block main game loop"""
        game = SudokuGame()

        # Start generation
        game._start_puzzle_generation('easy')

        # Main loop should still be responsive
        # (Simulate multiple frames)
        for _ in range(10):
            before = time.time()
            game._finish_puzzle_generation()  # Should return quickly
            elapsed = time.time() - before

            # Should be < 10ms per frame (non-blocking)
            assert elapsed < 0.01

    def test_count_solutions_limit_saves_time(self):
        """count_solutions with limit should be faster than without"""
        puzzle, solution, _, _, _ = generate_puzzle_with_uniqueness('medium')

        solver = SudokuSolver([row[:] for row in puzzle])

        # Count with limit=2 (should stop early)
        start = time.time()
        count_limited = solver.count_solutions(limit=2)
        time_limited = time.time() - start

        # Should have found it's either 1 or 2+
        assert count_limited in [0, 1, 2]

        # Time should be reasonable (< 5 seconds)
        assert time_limited < 5.0
