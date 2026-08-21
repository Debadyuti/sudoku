"""
Sudoku Game - Menu System

Menu state management, interaction handling, and puzzle file operations.
"""

import pygame
from pathlib import Path

try:
    from .constants import MENU_HEIGHT, RED, GREEN, BLUE
    from .solver import generate_puzzle, save_puzzle, load_puzzle
except ImportError:
    from constants import MENU_HEIGHT, RED, GREEN, BLUE
    from solver import generate_puzzle, save_puzzle, load_puzzle


class MenuSystem:
    """Handles menu state, interactions, and puzzle operations."""

    def __init__(self):
        """Initialize menu state."""
        self.menu_open = None          # 'FILE', 'EDIT', or None
        self.menu_hover_index = -1     # Track which menu item is hovered
        self.submenu_open = None       # 'NEW_PUZZLE' or None
        self.submenu_hover_index = -1  # Track which submenu item is hovered
        self.message = ""
        self.message_color = BLUE

    def update_hover(self, mouse_pos):
        """Update menu hover state based on mouse position."""
        x, y = mouse_pos

        if self.menu_open == 'FILE':
            if x >= 190 and y >= MENU_HEIGHT:
                self.menu_hover_index = 0
                self.submenu_hover_index = (y - MENU_HEIGHT) // 30
            elif 10 < x < 190 and y >= MENU_HEIGHT:
                self.menu_hover_index = (y - MENU_HEIGHT) // 30
                self.submenu_hover_index = -1
            else:
                self.menu_hover_index = -1
                self.submenu_hover_index = -1
        elif self.menu_open == 'EDIT':
            if 65 < x < 215 and y >= MENU_HEIGHT:
                self.menu_hover_index = (y - MENU_HEIGHT) // 30
            else:
                self.menu_hover_index = -1
        else:
            self.menu_hover_index = -1
            self.submenu_hover_index = -1

    def handle_click(self, mouse_pos):
        """Handle menu bar and submenu clicks. Returns True if menu handled click."""
        x, y = mouse_pos

        # Check if click in menu bar (FILE or EDIT)
        if y < MENU_HEIGHT:
            if 10 < x < 55:  # FILE menu
                self.menu_open = 'FILE' if self.menu_open != 'FILE' else None
                self.menu_hover_index = -1
                self.submenu_open = None
                self.submenu_hover_index = -1
                return True
            elif 65 < x < 115:  # EDIT menu
                self.menu_open = 'EDIT' if self.menu_open != 'EDIT' else None
                self.menu_hover_index = -1
                self.submenu_open = None
                self.submenu_hover_index = -1
                return True
            return False

        # Check if click on submenu item (New Puzzle submenu at x >= 190)
        if self.menu_open == 'FILE' and x >= 190 and y >= MENU_HEIGHT and y < MENU_HEIGHT + 90:
            submenu_item_index = (y - MENU_HEIGHT) // 30
            if 0 <= submenu_item_index < 3:
                return ('new_puzzle', submenu_item_index)

        # Check if click on FILE menu item
        if self.menu_open == 'FILE' and 10 < x < 190 and y >= MENU_HEIGHT:
            item_index = (y - MENU_HEIGHT) // 30
            if 0 <= item_index < 4:
                if item_index == 0:  # "New Puzzle"
                    self.submenu_open = 'NEW_PUZZLE'
                    return True
                else:
                    return ('file_menu', item_index)

        # Check if click on EDIT menu item
        if self.menu_open == 'EDIT' and 65 < x < 215 and y >= MENU_HEIGHT:
            item_index = (y - MENU_HEIGHT) // 30
            if 0 <= item_index < 1:
                return ('edit_menu', item_index)

        return False

    def close_menu(self):
        """Close open menus."""
        self.menu_open = None
        self.submenu_open = None
        self.menu_hover_index = -1
        self.submenu_hover_index = -1

    @staticmethod
    def generate_puzzle(difficulty):
        """Generate a new puzzle of given difficulty.

        Args:
            difficulty: 'easy', 'medium', or 'hard'

        Returns: (puzzle_grid, solution_grid, message, message_color)
        """
        try:
            puzzle, solution = generate_puzzle(difficulty)
            clue_count = sum(1 for row in puzzle for cell in row if cell != 0)
            message = f"New {difficulty} puzzle generated! ({clue_count} clues)"
            return puzzle, solution, message, GREEN
        except Exception as e:
            return None, None, f"Error generating puzzle: {str(e)}", RED

    @staticmethod
    def load_puzzle_file():
        """Load puzzle from file.

        Returns: (puzzle_grid, solution_grid, difficulty, clues, message, message_color)
        """
        try:
            puzzle_dir = Path('sudoku_puzzles')
            puzzle_files = list(puzzle_dir.glob('*.json'))

            if not puzzle_files:
                return None, None, None, None, "No puzzle files found in sudoku_puzzles/", RED

            latest_file = max(puzzle_files, key=lambda p: p.stat().st_mtime)
            puzzle, solution, difficulty, clues = load_puzzle(str(latest_file))

            if puzzle is None:
                return None, None, None, None, "Error loading puzzle file", RED

            message = f"Puzzle loaded: {difficulty} ({clues} clues)"
            return puzzle, solution, difficulty, clues, message, GREEN
        except Exception as e:
            return None, None, None, None, f"Error: {str(e)}", RED

    @staticmethod
    def save_puzzle_file(grid, puzzle_solution=None):
        """Save puzzle to file.

        Args:
            grid: Current grid (puzzle state)
            puzzle_solution: Optional solution grid (defaults to current grid as solution)

        Returns: (message, message_color)
        """
        try:
            puzzle_dir = Path('sudoku_puzzles')
            puzzle_dir.mkdir(exist_ok=True)

            import datetime
            filename = puzzle_dir / f"puzzle_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

            # Determine difficulty from clue count
            clues = sum(1 for row in grid for cell in row if cell != 0)
            if clues <= 20:
                difficulty = 'easy'
            elif clues <= 35:
                difficulty = 'medium'
            else:
                difficulty = 'hard'

            solution = puzzle_solution if puzzle_solution else [row[:] for row in grid]
            save_puzzle(grid, solution, difficulty, str(filename))

            return f"Puzzle saved: {filename.name}", GREEN
        except Exception as e:
            return f"Error saving: {str(e)}", RED
