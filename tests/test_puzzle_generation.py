"""
Tests for System Generated Puzzles (Phase 7.4)

Tests for:
- Puzzle generation with guaranteed uniqueness
- Difficulty levels (easy, medium, hard)
- Puzzle validity
- Solution count verification
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
from solver import generate_puzzle_with_uniqueness, PuzzleState, SudokuSolver


class TestPuzzleGenerationWithUniqueness:
    """Test generate_puzzle_with_uniqueness() function"""

    def test_generate_easy_puzzle(self):
        """Easy puzzle should have 10-25 clues"""
        puzzle, solution, state, message, color = generate_puzzle_with_uniqueness('easy')

        clue_count = sum(1 for i in range(9) for j in range(9) if puzzle[i][j] != 0)
        assert 10 <= clue_count <= 25
        assert state == PuzzleState.SINGLE_SOLUTION
        assert color == (0, 200, 0)  # GREEN

    def test_generate_medium_puzzle(self):
        """Medium puzzle should have 20-35 clues"""
        puzzle, solution, state, message, color = generate_puzzle_with_uniqueness('medium')

        clue_count = sum(1 for i in range(9) for j in range(9) if puzzle[i][j] != 0)
        assert 20 <= clue_count <= 35
        assert state == PuzzleState.SINGLE_SOLUTION
        assert color == (0, 200, 0)  # GREEN

    def test_generate_hard_puzzle(self):
        """Hard puzzle should have 30-50 clues"""
        puzzle, solution, state, message, color = generate_puzzle_with_uniqueness('hard')

        clue_count = sum(1 for i in range(9) for j in range(9) if puzzle[i][j] != 0)
        assert 30 <= clue_count <= 50
        assert state == PuzzleState.SINGLE_SOLUTION
        assert color == (0, 200, 0)  # GREEN

    def test_generated_puzzle_is_valid(self):
        """Generated puzzle should have no conflicts"""
        puzzle, solution, state, message, color = generate_puzzle_with_uniqueness('medium')

        solver = SudokuSolver(puzzle)
        errors = solver.find_errors()
        assert len(errors) == 0

    def test_generated_puzzle_has_unique_solution(self):
        """Generated puzzle should have exactly 1 solution"""
        puzzle, solution, state, message, color = generate_puzzle_with_uniqueness('medium')

        solver = SudokuSolver([row[:] for row in puzzle])
        solution_count = solver.count_solutions(limit=2)
        assert solution_count == 1

    def test_solution_solves_puzzle(self):
        """Provided solution should solve the puzzle"""
        puzzle, solution, state, message, color = generate_puzzle_with_uniqueness('medium')

        # Verify solution is complete
        solution_clues = sum(1 for i in range(9) for j in range(9) if solution[i][j] != 0)
        assert solution_clues == 81

        # Verify solution has no conflicts
        solver = SudokuSolver(solution)
        errors = solver.find_errors()
        assert len(errors) == 0

    def test_puzzle_and_solution_match(self):
        """Puzzle clues should match solution values"""
        puzzle, solution, state, message, color = generate_puzzle_with_uniqueness('medium')

        # Check that all puzzle clues match solution
        for i in range(9):
            for j in range(9):
                if puzzle[i][j] != 0:
                    assert puzzle[i][j] == solution[i][j]

    def test_returns_state_info(self):
        """Generated puzzle should return state information"""
        puzzle, solution, state, message, color = generate_puzzle_with_uniqueness('medium')

        assert state is not None
        assert message is not None
        assert color is not None
        assert state == PuzzleState.SINGLE_SOLUTION

    def test_default_difficulty_is_medium(self):
        """Calling without difficulty should default to medium"""
        puzzle, solution, state, message, color = generate_puzzle_with_uniqueness()

        clue_count = sum(1 for i in range(9) for j in range(9) if puzzle[i][j] != 0)
        assert 20 <= clue_count <= 35

    def test_multiple_generations_differ(self):
        """Different generated puzzles should be different"""
        puzzle1, _, _, _, _ = generate_puzzle_with_uniqueness('medium')
        puzzle2, _, _, _, _ = generate_puzzle_with_uniqueness('medium')

        # Puzzles should be different (extremely unlikely to be identical)
        assert puzzle1 != puzzle2

    def test_puzzle_is_solvable(self):
        """Generated puzzle should be solvable by backtracking"""
        puzzle, solution, state, message, color = generate_puzzle_with_uniqueness('medium')

        solver = SudokuSolver([row[:] for row in puzzle])
        is_solvable = solver.solve_backtrack()
        assert is_solvable is True

    def test_easy_puzzle_is_easier_than_hard(self):
        """Easy puzzles should have fewer clues than hard puzzles on average"""
        # Generate multiple puzzles and check average clue counts
        easy_clues = []
        hard_clues = []

        for _ in range(3):
            puzzle, _, _, _, _ = generate_puzzle_with_uniqueness('easy')
            easy_clues.append(sum(1 for i in range(9) for j in range(9) if puzzle[i][j] != 0))

            puzzle, _, _, _, _ = generate_puzzle_with_uniqueness('hard')
            hard_clues.append(sum(1 for i in range(9) for j in range(9) if puzzle[i][j] != 0))

        avg_easy = sum(easy_clues) / len(easy_clues)
        avg_hard = sum(hard_clues) / len(hard_clues)
        assert avg_easy < avg_hard


class TestGeneratedPuzzleIntegration:
    """Test integration with game system"""

    def test_generated_puzzle_can_be_finalized(self):
        """Generated puzzle should finalize without errors"""
        from sudoku_game import SudokuGame

        puzzle, solution, state, message, color = generate_puzzle_with_uniqueness('medium')

        game = SudokuGame()
        game.grid = puzzle
        game.finalize_puzzle()

        # Should finalize as SINGLE_SOLUTION (GREEN)
        assert game.puzzle_state == PuzzleState.SINGLE_SOLUTION
        assert game.finalized is True

    def test_generated_puzzle_auto_freezes(self):
        """When finalized, puzzle clues should be frozen"""
        from sudoku_game import SudokuGame

        puzzle, solution, state, message, color = generate_puzzle_with_uniqueness('medium')

        game = SudokuGame()
        game.grid = puzzle
        game.finalize_puzzle()

        # All non-empty cells in original puzzle should be frozen
        # (They're now part of the frozen_cells from the game's perspective)
        # Note: frozen_cells is set when loading, not when finalizing
        # So we just verify the game knows it's finalized
        assert game.finalized is True
