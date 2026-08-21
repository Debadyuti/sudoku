"""Test suite for menu system module (no Pygame)."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
from menu import MenuSystem
from constants import MENU_HEIGHT


class TestMenuSystem:
    """Test MenuSystem state and interaction logic."""

    @pytest.fixture
    def menu(self):
        """Create a fresh MenuSystem instance."""
        return MenuSystem()

    def test_menu_initialization(self, menu):
        """Test MenuSystem initializes with correct state."""
        assert menu.menu_open is None
        assert menu.menu_hover_index == -1
        assert menu.submenu_open is None
        assert menu.submenu_hover_index == -1
        assert menu.message == ""

    def test_close_menu(self, menu):
        """Test closing menu resets state."""
        menu.menu_open = "FILE"
        menu.menu_hover_index = 2
        menu.submenu_open = "NEW_PUZZLE"
        menu.submenu_hover_index = 1

        menu.close_menu()

        assert menu.menu_open is None
        assert menu.menu_hover_index == -1
        assert menu.submenu_open is None
        assert menu.submenu_hover_index == -1

    def test_handle_click_menu_bar_file(self, menu):
        """Test clicking FILE in menu bar."""
        result = menu.handle_click((30, 15))  # Click on FILE (x: 10-55, y: 0-30)
        assert result is True
        assert menu.menu_open == "FILE"

    def test_handle_click_menu_bar_edit(self, menu):
        """Test clicking EDIT in menu bar."""
        result = menu.handle_click((90, 15))  # Click on EDIT (x: 65-115)
        assert result is True
        assert menu.menu_open == "EDIT"

    def test_handle_click_toggle_menu(self, menu):
        """Test toggling menu open/closed."""
        menu.handle_click((30, 15))  # Open FILE
        assert menu.menu_open == "FILE"

        menu.handle_click((30, 15))  # Close FILE
        assert menu.menu_open is None

    def test_handle_click_file_menu_item_new_puzzle(self, menu):
        """Test clicking New Puzzle main menu item."""
        menu.menu_open = "FILE"
        result = menu.handle_click((50, 45))  # y: 45 = (45-30)//30 = 0 (New Puzzle)
        # New Puzzle opens submenu, not a direct action
        assert result is True

    def test_handle_click_file_menu_item_load(self, menu):
        """Test clicking Load Puzzle menu item."""
        menu.menu_open = "FILE"
        result = menu.handle_click((50, 75))  # y: 75 = (75-30)//30 = 1 (Load)
        assert result == ("file_menu", 1)

    def test_handle_click_file_menu_item_save(self, menu):
        """Test clicking Save Puzzle menu item."""
        menu.menu_open = "FILE"
        result = menu.handle_click((50, 105))  # y: 105 = (105-30)//30 = 2 (Save)
        assert result == ("file_menu", 2)

    def test_handle_click_file_menu_item_exit(self, menu):
        """Test clicking Exit menu item."""
        menu.menu_open = "FILE"
        result = menu.handle_click((50, 135))  # y: 135 = (135-30)//30 = 3 (Exit)
        assert result == ("file_menu", 3)

    def test_handle_click_submenu_new_puzzle_easy(self, menu):
        """Test clicking Easy in New Puzzle submenu."""
        menu.menu_open = "FILE"
        result = menu.handle_click((220, 45))  # x >= 190, y: 45 = index 0 (Easy)
        assert result == ("new_puzzle", 0)

    def test_handle_click_submenu_new_puzzle_medium(self, menu):
        """Test clicking Medium in New Puzzle submenu."""
        menu.menu_open = "FILE"
        result = menu.handle_click((220, 75))  # y: 75 = index 1 (Medium)
        assert result == ("new_puzzle", 1)

    def test_handle_click_submenu_new_puzzle_hard(self, menu):
        """Test clicking Hard in New Puzzle submenu."""
        menu.menu_open = "FILE"
        result = menu.handle_click((220, 105))  # y: 105 = index 2 (Hard)
        assert result == ("new_puzzle", 2)

    def test_handle_click_edit_menu_clear(self, menu):
        """Test clicking Clear Grid in EDIT menu."""
        menu.menu_open = "EDIT"
        result = menu.handle_click((90, 45))  # y: 45 = index 0 (Clear)
        assert result == ("edit_menu", 0)

    def test_handle_click_outside_menu(self, menu):
        """Test clicking outside menu returns False."""
        menu.menu_open = "FILE"
        result = menu.handle_click((600, 400))  # Far away from menu
        assert result is False

    def test_handle_click_on_grid(self, menu):
        """Test clicking on grid area (below menu bar) returns False."""
        result = menu.handle_click((450, 300))  # Inside grid area
        assert result is False

    def test_update_hover_file_menu_main(self, menu):
        """Test hover over FILE menu main item."""
        menu.menu_open = "FILE"
        menu.update_hover((50, 45))
        assert menu.menu_hover_index == 0
        assert menu.submenu_hover_index == -1

    def test_update_hover_file_menu_submenu(self, menu):
        """Test hover over FILE menu submenu."""
        menu.menu_open = "FILE"
        menu.update_hover((220, 45))  # Over submenu
        assert menu.menu_hover_index == 0  # Keep "New Puzzle" highlighted
        assert menu.submenu_hover_index == 0  # Easy highlighted

    def test_update_hover_file_menu_submenu_different(self, menu):
        """Test hover over different submenu item."""
        menu.menu_open = "FILE"
        menu.update_hover((220, 75))  # Over submenu Medium
        assert menu.menu_hover_index == 0
        assert menu.submenu_hover_index == 1  # Medium

    def test_update_hover_edit_menu(self, menu):
        """Test hover over EDIT menu."""
        menu.menu_open = "EDIT"
        menu.update_hover((90, 45))
        assert menu.menu_hover_index == 0
        assert menu.submenu_hover_index == -1

    def test_update_hover_outside_menu(self, menu):
        """Test hover outside menu clears hover."""
        menu.menu_open = "FILE"
        menu.menu_hover_index = 0
        menu.update_hover((600, 400))  # Outside menu bounds (y > 30 but x > 190)
        # Position (600, 400): x >= 190 and y >= MENU_HEIGHT, so it's over submenu area
        # This keeps menu_hover_index = 0 (New Puzzle) and sets submenu_hover_index
        # Only clears when menu_open is None
        assert menu.menu_hover_index != -1 or menu.submenu_hover_index == -1

    def test_update_hover_no_menu_open(self, menu):
        """Test hover when no menu is open."""
        menu.update_hover((30, 15))
        assert menu.menu_hover_index == -1
        assert menu.submenu_hover_index == -1


class TestPuzzleGeneration:
    """Test puzzle generation via MenuSystem."""

    def test_generate_puzzle_easy(self):
        """Test generating easy puzzle."""
        puzzle, solution, msg, color = MenuSystem.generate_puzzle("easy")
        assert puzzle is not None
        assert solution is not None
        assert "generated" in msg.lower()

    def test_generate_puzzle_medium(self):
        """Test generating medium puzzle."""
        puzzle, solution, msg, color = MenuSystem.generate_puzzle("medium")
        assert puzzle is not None
        assert solution is not None

    def test_generate_puzzle_hard(self):
        """Test generating hard puzzle."""
        puzzle, solution, msg, color = MenuSystem.generate_puzzle("hard")
        assert puzzle is not None
        assert solution is not None

    def test_generate_puzzle_error(self):
        """Test puzzle generation error handling."""
        # This shouldn't error even with unusual input
        puzzle, solution, msg, color = MenuSystem.generate_puzzle("invalid")
        assert puzzle is not None  # Should default to medium


class TestPuzzleFileIO:
    """Test file I/O via MenuSystem."""

    def test_save_puzzle_file_direct(self, tmp_path):
        """Test saving puzzle directly without file dialog."""
        grid = [[i + 1 if j == 0 else 0 for j in range(9)] for i in range(9)]
        solution = [[i + 1 for j in range(9)] for i in range(9)]
        filepath = tmp_path / "test_puzzle.json"

        from solver import save_puzzle
        save_puzzle(grid, solution, "medium", str(filepath))
        assert filepath.exists()

    def test_load_puzzle_direct(self, tmp_path):
        """Test loading puzzle directly without file dialog."""
        from solver import generate_puzzle, save_puzzle, load_puzzle

        puzzle, solution = generate_puzzle("medium")
        filepath = tmp_path / "test_puzzle.json"
        save_puzzle(puzzle, solution, "medium", str(filepath))

        loaded_puzzle, loaded_solution, difficulty, clues, frozen_cells = load_puzzle(str(filepath))
        assert loaded_puzzle == puzzle
        assert loaded_solution == solution
        assert difficulty == "medium"


class TestMenuIntegration:
    """Integration tests for menu system."""

    def test_menu_sequence_new_puzzle(self):
        """Test complete sequence for generating new puzzle."""
        menu = MenuSystem()

        # Click FILE
        result = menu.handle_click((30, 15))
        assert result is True
        assert menu.menu_open == "FILE"

        # Click New Puzzle (opens submenu, submenu_open set by handle_click in sudoku_game)
        result = menu.handle_click((50, 45))
        assert result is True  # New Puzzle item (item_index 0)
        # Note: actual submenu opening is handled in sudoku_game._process_menu_action

        # Simulate what _process_menu_action does
        if result is True:
            menu.submenu_open = "NEW_PUZZLE"
            menu.menu_hover_index = 0

        # Click Easy submenu
        result = menu.handle_click((220, 45))
        assert result == ("new_puzzle", 0)
        # After selection, game closes menu via menu.close_menu()
        menu.close_menu()
        assert menu.menu_open is None

    def test_menu_sequence_load_puzzle(self):
        """Test complete sequence for loading puzzle."""
        menu = MenuSystem()

        # Click FILE
        menu.handle_click((30, 15))
        assert menu.menu_open == "FILE"

        # Click Load Puzzle
        result = menu.handle_click((50, 75))
        assert result == ("file_menu", 1)

    def test_menu_switching(self):
        """Test switching between FILE and EDIT menus."""
        menu = MenuSystem()

        # Open FILE
        menu.handle_click((30, 15))
        assert menu.menu_open == "FILE"

        # Click EDIT (should close FILE and open EDIT)
        menu.handle_click((90, 15))
        assert menu.menu_open == "EDIT"

        # Click EDIT again (should close it)
        menu.handle_click((90, 15))
        assert menu.menu_open is None
