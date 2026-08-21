#!/usr/bin/env python3
"""
Sudoku Game - Launcher Script

This script runs the Sudoku game from the src/ folder.
Usage: python run.py
       uv run python run.py
"""

import sys
from pathlib import Path

# Add src/ to path so we can import sudoku_game
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

from sudoku_game import SudokuGame

if __name__ == "__main__":
    game = SudokuGame()
    game.run()
