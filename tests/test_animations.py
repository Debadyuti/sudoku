"""Test suite for animation framework (Phase 3)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
import pygame
from sudoku_game import SudokuGame
from ui import UIRenderer
from constants import interpolate_color, ease_in_out, lerp, WHITE, LIGHT_BLUE, BLACK

# Initialize pygame for testing
pygame.init()


class TestInterpolateColor:
    """Test color interpolation utility."""

    def test_interpolate_color_at_start(self):
        """Test interpolation at t=0 returns start color."""
        result = interpolate_color((255, 0, 0), (0, 255, 0), 0)
        assert result == (255, 0, 0)

    def test_interpolate_color_at_end(self):
        """Test interpolation at t=1 returns end color."""
        result = interpolate_color((255, 0, 0), (0, 255, 0), 1)
        assert result == (0, 255, 0)

    def test_interpolate_color_midpoint(self):
        """Test interpolation at t=0.5 returns midpoint color."""
        result = interpolate_color((0, 0, 0), (100, 100, 100), 0.5)
        # Should be approximately (50, 50, 50)
        assert result == (50, 50, 50)

    def test_interpolate_color_clamped(self):
        """Test interpolation clamps t to [0, 1]."""
        result = interpolate_color((255, 0, 0), (0, 255, 0), 1.5)
        assert result == (0, 255, 0)  # Clamped to t=1


class TestAnimationStateTracking:
    """Test animation state initialization and tracking."""

    def test_animation_state_initialized(self):
        """Test game initializes animation state."""
        game = SudokuGame()
        assert isinstance(game.animations, dict)
        assert len(game.animations) == 0
        assert isinstance(game.button_hover_times, dict)
        assert game.panel_stat_update_time == 0
        assert game.message_animation_start == 0
        assert game.last_frame_time is not None

    def test_delta_time_tracking(self):
        """Test delta time tracking variables exist."""
        game = SudokuGame()
        # last_frame_time should be initialized
        assert game.last_frame_time is not None
        assert isinstance(game.last_frame_time, (int, float))


class TestUIAnimations:
    """Test UI renderer animation methods."""

    def test_trigger_cell_animation(self):
        """Test triggering cell animation."""
        pygame.display.set_mode((100, 100))
        renderer = UIRenderer(pygame.display.get_surface())

        # Trigger animation
        renderer.trigger_cell_animation(0, 0, duration=200)

        # Check animation state
        assert (0, 0) in renderer.cell_animations
        anim = renderer.cell_animations[(0, 0)]
        assert anim['duration'] == 200
        assert 'start_time' in anim

    def test_get_cell_color_no_animation(self):
        """Test cell color without animation."""
        pygame.display.set_mode((100, 100))
        renderer = UIRenderer(pygame.display.get_surface())

        # Get cell color when not animating
        color = renderer._get_cell_color(0, 0, LIGHT_BLUE)
        assert color == LIGHT_BLUE

    def test_get_pulse_scale_no_pulse(self):
        """Test pulse scale when no pulse active."""
        pygame.display.set_mode((100, 100))
        renderer = UIRenderer(pygame.display.get_surface())

        # Get pulse scale at time 0 (far past)
        scale = renderer.get_pulse_scale(0, duration=150)
        assert scale == 1.0  # No pulse

    def test_get_bar_glow_no_pulse(self):
        """Test bar glow when no pulse active."""
        pygame.display.set_mode((100, 100))
        renderer = UIRenderer(pygame.display.get_surface())

        # Get glow at time 0 (far past)
        glow = renderer.get_bar_glow(0, duration=100)
        assert glow == 0.0  # No glow


class TestEasingFunctions:
    """Test easing and interpolation functions."""

    def test_lerp_start(self):
        """Test linear interpolation at start."""
        assert lerp(0, 100, 0) == 0

    def test_lerp_end(self):
        """Test linear interpolation at end."""
        assert lerp(0, 100, 1) == 100

    def test_lerp_midpoint(self):
        """Test linear interpolation at midpoint."""
        assert lerp(0, 100, 0.5) == 50

    def test_ease_in_out_start(self):
        """Test easing at start."""
        assert ease_in_out(0) == 0

    def test_ease_in_out_end(self):
        """Test easing at end."""
        assert ease_in_out(1) == 1

    def test_ease_in_out_smooth(self):
        """Test easing produces smooth curve."""
        # At 0.5, cubic easing should still be 0.5
        assert abs(ease_in_out(0.5) - 0.5) < 0.01

    def test_ease_in_out_clamped(self):
        """Test easing clamps values."""
        assert ease_in_out(-0.5) == 0
        assert ease_in_out(1.5) == 1


class TestAnimationIntegration:
    """Test animations in game context."""

    def test_cell_animation_trigger_from_game(self):
        """Test triggering cell animation from game state."""
        game = SudokuGame()
        game.ui.trigger_cell_animation(3, 4, duration=150)

        # Animation should be registered
        assert (3, 4) in game.ui.cell_animations

    def test_multiple_cell_animations(self):
        """Test multiple cells animating simultaneously."""
        game = SudokuGame()

        # Trigger animations on multiple cells
        for i in range(3):
            for j in range(3):
                game.ui.trigger_cell_animation(i, j, duration=100)

        # All should be registered
        assert len(game.ui.cell_animations) == 9
