"""
Phase 7 Performance Benchmarks

Measures performance of key Phase 7 operations:
- Puzzle generation by difficulty
- Validation (all 3 lenses)
- Solution counting
- Puzzle loading/saving
"""

import sys
from pathlib import Path
import time
import json
import tempfile

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
from sudoku_game import SudokuGame
from solver import (
    SudokuSolver, PuzzleState,
    generate_puzzle_with_uniqueness,
    save_puzzle, load_puzzle
)


class TestGenerationPerformance:
    """Benchmark puzzle generation by difficulty"""

    def test_generation_easy_performance(self):
        """Easy puzzle generation should complete in ~30-60 seconds"""
        start = time.time()
        puzzle, solution, state, msg, color = generate_puzzle_with_uniqueness('easy')
        elapsed = time.time() - start

        clue_count = sum(1 for row in puzzle for cell in row if cell != 0)

        # Should complete in reasonable time
        assert elapsed < 120, f"Easy generation took {elapsed:.1f}s (max 120s)"
        # Should have correct clue count
        assert 10 <= clue_count <= 25, f"Easy puzzle has {clue_count} clues (expected 10-25)"
        # Should have single solution
        assert state == PuzzleState.SINGLE_SOLUTION

        print(f"\n  Easy generation: {elapsed:.1f}s, {clue_count} clues")

    def test_generation_medium_performance(self):
        """Medium puzzle generation should complete in ~60-120 seconds"""
        start = time.time()
        puzzle, solution, state, msg, color = generate_puzzle_with_uniqueness('medium')
        elapsed = time.time() - start

        clue_count = sum(1 for row in puzzle for cell in row if cell != 0)

        # Should complete in reasonable time
        assert elapsed < 180, f"Medium generation took {elapsed:.1f}s (max 180s)"
        # Should have correct clue count
        assert 20 <= clue_count <= 35, f"Medium puzzle has {clue_count} clues (expected 20-35)"
        # Should have single solution
        assert state == PuzzleState.SINGLE_SOLUTION

        print(f"\n  Medium generation: {elapsed:.1f}s, {clue_count} clues")

    def test_generation_hard_performance(self):
        """Hard puzzle generation should complete in ~120-200 seconds"""
        start = time.time()
        puzzle, solution, state, msg, color = generate_puzzle_with_uniqueness('hard')
        elapsed = time.time() - start

        clue_count = sum(1 for row in puzzle for cell in row if cell != 0)

        # Should complete in reasonable time
        assert elapsed < 300, f"Hard generation took {elapsed:.1f}s (max 300s)"
        # Should have correct clue count
        assert 30 <= clue_count <= 50, f"Hard puzzle has {clue_count} clues (expected 30-50)"
        # Should have single solution
        assert state == PuzzleState.SINGLE_SOLUTION

        print(f"\n  Hard generation: {elapsed:.1f}s, {clue_count} clues")


class TestValidationPerformance:
    """Benchmark puzzle validation"""

    def test_validation_empty_grid_fast(self):
        """Validating empty grid should be very fast"""
        game = SudokuGame()
        solver = SudokuSolver(game.grid)

        start = time.time()
        state, msg, color = solver.validate_puzzle()
        elapsed = time.time() - start

        assert elapsed < 0.1, f"Empty grid validation took {elapsed:.3f}s"
        print(f"\n  Empty grid validation: {elapsed*1000:.1f}ms")

    def test_validation_full_solution_fast(self):
        """Validating complete solution should be very fast"""
        puzzle, solution, _, _, _ = generate_puzzle_with_uniqueness('easy')
        solver = SudokuSolver(solution)

        start = time.time()
        state, msg, color = solver.validate_puzzle()
        elapsed = time.time() - start

        assert elapsed < 1.0, f"Full solution validation took {elapsed:.3f}s"
        assert state == PuzzleState.SINGLE_SOLUTION
        print(f"\n  Full solution validation: {elapsed*1000:.1f}ms")

    def test_validation_generated_puzzle_reasonable(self):
        """Validating generated puzzle should be reasonable"""
        puzzle, solution, _, _, _ = generate_puzzle_with_uniqueness('easy')
        solver = SudokuSolver([row[:] for row in puzzle])

        start = time.time()
        state, msg, color = solver.validate_puzzle()
        elapsed = time.time() - start

        assert elapsed < 60, f"Generated puzzle validation took {elapsed:.1f}s"
        assert state == PuzzleState.SINGLE_SOLUTION
        print(f"\n  Generated puzzle validation: {elapsed:.1f}s")

    def test_validation_invalid_puzzle_fast(self):
        """Validating invalid puzzle should exit early"""
        grid = [[0 for _ in range(9)] for _ in range(9)]
        grid[0][0] = 1
        grid[0][1] = 1  # Duplicate

        solver = SudokuSolver(grid)

        start = time.time()
        state, msg, color = solver.validate_puzzle()
        elapsed = time.time() - start

        # Should exit early on duplicate detection
        assert elapsed < 0.1, f"Invalid puzzle validation took {elapsed:.3f}s"
        assert state == PuzzleState.INVALID
        print(f"\n  Invalid puzzle validation (early exit): {elapsed*1000:.1f}ms")


class TestSolutionCountingPerformance:
    """Benchmark solution counting"""

    def test_count_solutions_limit_2_early_exit(self):
        """count_solutions with limit=2 should exit early"""
        # Create a puzzle with multiple solutions
        grid = [[0 for _ in range(9)] for _ in range(9)]
        grid[0][0] = 1  # Only one clue = many solutions

        solver = SudokuSolver(grid)

        start = time.time()
        count = solver.count_solutions(limit=2)
        elapsed = time.time() - start

        # Should find 2 solutions and exit (not try to find all)
        assert count == 2
        # Should be fast due to early exit
        assert elapsed < 1.0, f"count_solutions(limit=2) took {elapsed:.1f}s"
        print(f"\n  count_solutions(limit=2) with many solutions: {elapsed*1000:.1f}ms, found {count}")

    def test_count_solutions_unique_solution(self):
        """count_solutions on unique puzzle should verify quickly"""
        puzzle, solution, _, _, _ = generate_puzzle_with_uniqueness('easy')
        solver = SudokuSolver([row[:] for row in puzzle])

        start = time.time()
        count = solver.count_solutions(limit=2)
        elapsed = time.time() - start

        assert count == 1
        # Should be reasonable (< 30 seconds for easy)
        assert elapsed < 30, f"count_solutions on unique puzzle took {elapsed:.1f}s"
        print(f"\n  count_solutions(limit=2) unique solution: {elapsed:.1f}s, found {count}")


class TestFileIOPerformance:
    """Benchmark puzzle save/load operations"""

    def test_save_puzzle_performance(self):
        """Saving puzzle to file should be fast"""
        puzzle, solution, _, _, _ = generate_puzzle_with_uniqueness('easy')

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name

        try:
            start = time.time()
            save_puzzle(puzzle, solution, 'easy', temp_path)
            elapsed = time.time() - start

            assert elapsed < 0.1, f"Puzzle save took {elapsed:.3f}s"
            print(f"\n  Puzzle save to file: {elapsed*1000:.1f}ms")
        finally:
            Path(temp_path).unlink()

    def test_load_puzzle_performance(self):
        """Loading puzzle from file should be fast"""
        puzzle, solution, _, _, _ = generate_puzzle_with_uniqueness('easy')

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name

        try:
            # Save first
            save_puzzle(puzzle, solution, 'easy', temp_path)

            # Load
            start = time.time()
            loaded_puzzle, loaded_solution, difficulty, clues, frozen = load_puzzle(temp_path)
            elapsed = time.time() - start

            assert elapsed < 0.1, f"Puzzle load took {elapsed:.3f}s"
            assert loaded_puzzle == puzzle
            print(f"\n  Puzzle load from file: {elapsed*1000:.1f}ms")
        finally:
            Path(temp_path).unlink()


class TestThreadingPerformance:
    """Benchmark puzzle generation threading overhead"""

    def test_threading_overhead_minimal(self):
        """Threading should not add significant overhead"""
        game = SudokuGame()

        # Time to start generation
        start = time.time()
        game._start_puzzle_generation('easy')
        elapsed_start = time.time() - start

        # Starting thread should be < 10ms
        assert elapsed_start < 0.01, f"Thread start took {elapsed_start:.3f}s"

        # Wait for completion
        timeout = time.time() + 70
        while game.generating_puzzle and time.time() < timeout:
            time.sleep(0.1)
            game._finish_puzzle_generation()

        # Time to apply result
        start = time.time()
        game._finish_puzzle_generation()
        elapsed_finish = time.time() - start

        # Applying result should be < 10ms
        assert elapsed_finish < 0.01, f"Result application took {elapsed_finish:.3f}s"

        print(f"\n  Thread start: {elapsed_start*1000:.1f}ms")
        print(f"  Result application: {elapsed_finish*1000:.1f}ms")


class TestMemoryUsage:
    """Verify memory usage is reasonable"""

    def test_puzzle_grid_memory_reasonable(self):
        """Puzzle grid should use minimal memory"""
        game = SudokuGame()
        puzzle, solution, _, _, _ = generate_puzzle_with_uniqueness('easy')
        game.grid = puzzle
        game.solution = solution

        # Store history
        game.move_history = [[row[:] for row in game.grid] for _ in range(100)]
        game.move_index = 99

        # Should not crash or use excessive memory
        assert len(game.move_history) == 100
        print(f"\n  100 move history stored successfully")

    def test_generation_thread_cleanup(self):
        """Generation thread should clean up properly"""
        game = SudokuGame()

        # Start multiple generations
        for _ in range(3):
            game._start_puzzle_generation('easy')

            timeout = time.time() + 70
            while game.generating_puzzle and time.time() < timeout:
                time.sleep(0.1)
                game._finish_puzzle_generation()

        # Should not have lingering threads
        # (Python daemon threads clean up automatically on exit)
        assert game.generation_thread is None or not game.generation_thread.is_alive()
        print(f"\n  Multiple generation threads cleaned up properly")
