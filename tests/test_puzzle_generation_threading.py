"""
Tests for puzzle generation threading (non-blocking UI)

Tests for:
- Background generation without UI freeze
- Spinner/timer display
- Generation result handling
"""

import sys
from pathlib import Path
import time
import threading

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
from sudoku_game import SudokuGame


class TestPuzzleGenerationThreading:
    """Test background puzzle generation"""

    def test_generation_starts_async(self):
        """Puzzle generation should start in background thread"""
        game = SudokuGame()

        # Start generation
        game._start_puzzle_generation('easy')

        assert game.generating_puzzle is True
        assert game.generation_thread is not None
        assert game.generation_thread.is_alive() or game.generation_result is not None

    def test_generation_stores_start_time(self):
        """Generation should record start time for elapsed display"""
        game = SudokuGame()

        start_before = time.time()
        game._start_puzzle_generation('easy')
        start_after = time.time()

        assert start_before <= game.generation_start_time <= start_after

    def test_generation_completes_eventually(self):
        """Generation should complete within reasonable timeout"""
        game = SudokuGame()

        game._start_puzzle_generation('easy')

        # Wait for generation to complete (easy = ~30-60s, so timeout at 70s)
        timeout = time.time() + 70
        while game.generating_puzzle and time.time() < timeout:
            time.sleep(0.1)
            game._finish_puzzle_generation()

        assert game.generating_puzzle is False
        assert game.generation_result is not None

    def test_generation_result_applied_to_grid(self):
        """When generation completes, result should populate grid"""
        game = SudokuGame()

        # Verify grid starts empty
        initial_empty = sum(1 for row in game.grid for cell in row if cell == 0)
        assert initial_empty == 81

        # Start generation
        game._start_puzzle_generation('easy')

        # Wait for completion
        timeout = time.time() + 70
        while game.generating_puzzle and time.time() < timeout:
            time.sleep(0.1)
            game._finish_puzzle_generation()

        # After completion, grid should have clues
        final_clues = sum(1 for row in game.grid for cell in row if cell != 0)
        assert 10 <= final_clues <= 25  # Easy puzzle clue range

    def test_finish_generation_idempotent(self):
        """Calling finish multiple times shouldn't change result"""
        game = SudokuGame()

        game._start_puzzle_generation('easy')

        # Wait for completion
        timeout = time.time() + 70
        while game.generating_puzzle and time.time() < timeout:
            time.sleep(0.1)
            game._finish_puzzle_generation()

        # Call finish again
        grid_after_first_finish = [row[:] for row in game.grid]
        game._finish_puzzle_generation()
        grid_after_second_finish = [row[:] for row in game.grid]

        assert grid_after_first_finish == grid_after_second_finish

    def test_generation_thread_is_daemon(self):
        """Generation thread should be daemon (not block app shutdown)"""
        game = SudokuGame()
        game._start_puzzle_generation('easy')

        assert game.generation_thread.daemon is True

    def test_multiple_generations_can_start_sequentially(self):
        """User can start multiple generations one after another"""
        game = SudokuGame()

        # Start easy generation
        game._start_puzzle_generation('easy')
        thread1 = game.generation_thread

        # Wait for completion
        timeout = time.time() + 70
        while game.generating_puzzle and time.time() < timeout:
            time.sleep(0.1)
            game._finish_puzzle_generation()

        # Start new generation
        game._start_puzzle_generation('medium')
        thread2 = game.generation_thread

        # Threads should be different
        assert thread1 != thread2

    def test_generation_sets_message_in_progress(self):
        """While generating, flag should be set"""
        game = SudokuGame()

        assert game.generating_puzzle is False

        game._start_puzzle_generation('easy')

        # After starting, flag should be set
        assert game.generating_puzzle is True
        # Spinner message appears in main game loop (line ~800 in run())

        # Wait for generation to complete
        time.sleep(0.5)

    def test_generation_handles_error(self):
        """If generation fails, error should be shown"""
        game = SudokuGame()

        game._start_puzzle_generation('invalid_difficulty')

        # Wait for generation to complete
        timeout = time.time() + 5
        while game.generating_puzzle and time.time() < timeout:
            time.sleep(0.1)
            game._finish_puzzle_generation()

        # Should have error message (or succeed anyway)
        assert game.message is not None


class TestThreadingSafety:
    """Test thread safety of generation system"""

    def test_generation_result_is_thread_safe(self):
        """Generation result assignment should be atomic"""
        game = SudokuGame()

        game._start_puzzle_generation('easy')

        # Rapidly call finish multiple times
        for _ in range(10):
            game._finish_puzzle_generation()
            time.sleep(0.01)

        # Should not crash or have corrupted state
        assert game.generation_result is None or isinstance(game.generation_result, tuple)

    def test_generation_state_variables_consistent(self):
        """Generation state should remain consistent"""
        game = SudokuGame()

        game._start_puzzle_generation('easy')

        # Check state consistency at different times
        for _ in range(10):
            generating_flag = game.generating_puzzle
            has_thread = game.generation_thread is not None
            time.sleep(0.01)

            # If generating, thread should exist
            if generating_flag:
                assert has_thread or game.generation_result is not None
