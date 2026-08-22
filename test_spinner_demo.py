#!/usr/bin/env python3
"""
Quick demo of puzzle generation spinner/timer functionality.

This shows the spinner and timer updating in real-time as puzzle generates.
"""

import sys
from pathlib import Path
import time

sys.path.insert(0, str(Path(__file__).parent / "src"))

from sudoku_game import SudokuGame


def demo_puzzle_generation_spinner():
    """Demo puzzle generation with spinner display"""
    print("=" * 60)
    print("Puzzle Generation Spinner Demo")
    print("=" * 60)
    print()

    game = SudokuGame()

    print("Starting EASY puzzle generation in background thread...")
    print()

    game._start_puzzle_generation('easy')

    # Simulate main game loop checking generation status
    spinner_chars = ['|', '/', '-', '\\']  # ASCII spinner for Windows console
    start = time.time()

    while game.generating_puzzle:
        elapsed = time.time() - start

        # Simulate what game loop does
        if game.generation_result:
            game._finish_puzzle_generation()
        else:
            spinner_index = int(elapsed * 4) % len(spinner_chars)
            spinner = spinner_chars[spinner_index]
            message = f"{spinner} Generating puzzle... ({elapsed:.1f}s)"
            print(f"\r{message:<50}", end='', flush=True)

        time.sleep(0.1)

    print()
    print()
    print("✓ Generation complete!")
    print()

    # Show result
    clue_count = sum(1 for row in game.grid for cell in row if cell != 0)
    print(f"Generated puzzle with {clue_count} clues")
    print(f"Message: {game.message}")
    print()

    # Show first 3 rows
    print("First 3 rows of generated puzzle:")
    for i in range(3):
        row_str = " ".join(str(cell) if cell != 0 else "." for cell in game.grid[i])
        print(f"  {row_str}")

    print()
    print("✓ Spinner demo complete!")


if __name__ == '__main__':
    demo_puzzle_generation_spinner()
