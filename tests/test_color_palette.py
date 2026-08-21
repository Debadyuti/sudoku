"""Test suite for Material Design color palette (Phase 4)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
from constants import (
    LIGHT_BLUE, LIGHT_RED, SOFT_YELLOW, FROZEN_BG, FROZEN_TEXT,
    GREEN, RED, BLUE, CYAN, ORANGE,
    MENU_BG, MENU_TEXT, MENU_HOVER, MENU_BORDER
)


class TestMaterialDesignPalette:
    """Test Material Design color palette implementation."""

    def test_selected_cell_color_saturated(self):
        """Test selected cell is more saturated than before."""
        # New: (150, 220, 255) vs Old: (173, 216, 230)
        assert LIGHT_BLUE == (150, 220, 255)
        # Verify blue component is high (saturation)
        assert LIGHT_BLUE[2] >= 220

    def test_error_cell_color_softer(self):
        """Test error cell is softer red."""
        # New: (255, 205, 210) vs Old: (255, 182, 193)
        assert LIGHT_RED == (255, 205, 210)
        # Verify red is max
        assert LIGHT_RED[0] == 255

    def test_solving_cell_color_warmer(self):
        """Test solving cell is warmer yellow."""
        # New: (255, 245, 157) vs Old: (255, 250, 200)
        assert SOFT_YELLOW == (255, 245, 157)
        # Verify yellow is balanced (high R and G)
        assert SOFT_YELLOW[0] >= 240
        assert SOFT_YELLOW[1] >= 240

    def test_frozen_cells_lighter(self):
        """Test frozen cell background is lighter."""
        # New: (238, 238, 238) vs Old: (230, 230, 230)
        assert FROZEN_BG == (238, 238, 238)
        # Verify light gray
        assert all(c >= 230 for c in FROZEN_BG)

    def test_button_colors_material_design(self):
        """Test button colors follow Material Design."""
        # Finalize button: Material Green 500
        assert GREEN == (76, 175, 80)
        # Clear button: Material Red 500
        assert RED == (244, 67, 54)
        # Solve Algo: Material Blue 500
        assert BLUE == (33, 150, 243)
        # Solve Fast: Material Cyan 500 (unchanged)
        assert CYAN == (0, 188, 212)

    def test_accent_colors_consistent(self):
        """Test accent colors are unified."""
        # Steps (green) matches button green
        assert GREEN == (76, 175, 80)
        # Backtracks (orange) remains
        assert ORANGE == (255, 152, 0)
        # Candidates (blue) matches button blue
        assert BLUE == (33, 150, 243)

    def test_menu_colors_updated(self):
        """Test menu colors are updated."""
        assert MENU_BG == (250, 250, 250)
        assert MENU_TEXT == (66, 66, 66)
        assert MENU_HOVER == (225, 245, 254)  # Enhanced light blue
        assert MENU_BORDER == (189, 189, 189)

    def test_frozen_text_unchanged(self):
        """Test frozen text color is unchanged."""
        assert FROZEN_TEXT == (30, 144, 255)

    def test_colors_are_rgb_tuples(self):
        """Test all colors are valid RGB tuples."""
        colors = [
            LIGHT_BLUE, LIGHT_RED, SOFT_YELLOW, FROZEN_BG, FROZEN_TEXT,
            GREEN, RED, BLUE, CYAN, ORANGE,
            MENU_BG, MENU_TEXT, MENU_HOVER, MENU_BORDER
        ]
        for color in colors:
            assert isinstance(color, tuple), f"{color} is not a tuple"
            assert len(color) == 3, f"{color} doesn't have 3 components"
            assert all(0 <= c <= 255 for c in color), f"{color} has out-of-range values"

    def test_contrast_selected_on_white(self):
        """Test selected cell has good contrast on white grid."""
        white = (255, 255, 255)
        # Calculate contrast ratio (simplified luminance distance)
        contrast = sum(abs(LIGHT_BLUE[i] - white[i]) for i in range(3))
        assert contrast > 130  # Good contrast (150,220,255 = 140 difference)

    def test_contrast_button_on_white(self):
        """Test button colors have good contrast on white background."""
        white = (255, 255, 255)
        for button_color in [GREEN, RED, BLUE]:
            contrast = sum(abs(button_color[i] - white[i]) for i in range(3))
            assert contrast > 180, f"Button color {button_color} has low contrast"

    def test_contrast_error_on_white(self):
        """Test error cell has good contrast on white."""
        white = (255, 255, 255)
        contrast = sum(abs(LIGHT_RED[i] - white[i]) for i in range(3))
        assert contrast > 90  # Acceptable contrast (255,205,210 = 95 difference)


class TestColorConsistency:
    """Test color consistency across UI."""

    def test_green_unified(self):
        """Test green is used consistently for finalize and steps."""
        assert GREEN == (76, 175, 80)
        # Both button and accent should be same
        steps_color = GREEN
        assert steps_color == GREEN

    def test_blue_unified(self):
        """Test blue is used consistently for solve and candidates."""
        assert BLUE == (33, 150, 243)

    def test_orange_consistent(self):
        """Test orange is used for backtracks."""
        assert ORANGE == (255, 152, 0)

    def test_no_palette_gaps(self):
        """Test all palette colors are defined."""
        palette = [
            LIGHT_BLUE, LIGHT_RED, SOFT_YELLOW, FROZEN_BG, FROZEN_TEXT,
            GREEN, RED, BLUE, CYAN, ORANGE,
            MENU_BG, MENU_TEXT, MENU_HOVER, MENU_BORDER
        ]
        assert len(palette) == 14
        assert all(color for color in palette)
