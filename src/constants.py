"""
Sudoku Game - Constants and Configuration

All constants, colors, fonts, and animation utilities in one place.
"""

import pygame

# Initialize Pygame
pygame.init()

# ============================================================================
# Window Dimensions & Layout
# ============================================================================

WIDTH = 900
HEIGHT = 800  # Accommodates menu bar (30px) + grid + buttons + panel

# Menu bar
MENU_HEIGHT = 30
MENU_BAR_Y = 0

# Grid layout
GRID_SIZE = 540
CELL_SIZE = GRID_SIZE // 9
MARGIN = 30
PANEL_WIDTH = 260  # Right panel for algorithm visualization
PANEL_GAP = 15    # Gap between grid and panel

# Derived layout constants (all shifted down 30px for menu bar)
GRID_TOP = MARGIN + MENU_HEIGHT            # 60
GRID_BOTTOM = GRID_TOP + GRID_SIZE         # 600
MESSAGE_Y = GRID_BOTTOM + 20               # 620 — message zone top
BUTTON_Y = GRID_BOTTOM + 70                # 670 — button row 1
BUTTON_Y2 = GRID_BOTTOM + 125              # 725 — button row 2

# Button layout
BUTTON_HEIGHT = 50
BUTTON_WIDTH = 140
_BTN_GAP = (GRID_SIZE - 2 * BUTTON_WIDTH) // 3  # Center buttons within grid
BUTTON_X1 = MARGIN + _BTN_GAP
BUTTON_X2 = MARGIN + _BTN_GAP * 2 + BUTTON_WIDTH

# Panel layout
PANEL_X = MARGIN + GRID_SIZE + PANEL_GAP
PANEL_Y = GRID_TOP
PANEL_HEIGHT = GRID_SIZE

# ============================================================================
# Color Palette
# ============================================================================

# Basic colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
LIGHT_GRAY = (220, 220, 220)
DARK_GRAY = (128, 128, 128)

# Grid colors
LIGHT_BLUE = (173, 216, 230)     # Selected cell
LIGHT_RED = (255, 182, 193)      # Error cell
SOFT_YELLOW = (255, 250, 200)    # Solving cell
FROZEN_BG = (230, 230, 230)      # Frozen cell background (greyed out)
FROZEN_TEXT = (30, 144, 255)     # Frozen cell text (blue)

# Button colors
GREEN = (34, 139, 34)             # Finalize (hover: #64C864)
RED = (220, 20, 60)               # Clear
BLUE = (30, 144, 255)             # Solve Algo
CYAN = (0, 188, 212)              # Solve Fast

# Menu colors
MENU_BG = (245, 245, 245)
MENU_TEXT = (66, 66, 66)
MENU_HOVER = (220, 240, 255)
MENU_BORDER = (180, 180, 180)

# Accent colors (for stats and indicators)
ORANGE = (255, 152, 0)            # Backtracks indicator

# ============================================================================
# Fonts
# ============================================================================

FONT_LARGE = pygame.font.Font(None, 40)   # Grid numbers
FONT_MEDIUM = pygame.font.Font(None, 32)  # Button text
FONT_SMALL = pygame.font.Font(None, 24)   # Panel text
FONT_MENU = pygame.font.Font(None, 18)    # Menu text

# ============================================================================
# Animation & Easing
# ============================================================================

def lerp(a, b, t):
    """Linear interpolation between a and b.

    Args:
        a: Start value
        b: End value
        t: Time in [0, 1]

    Returns: Interpolated value
    """
    t = max(0, min(1, t))
    return a + (b - a) * t


def ease_in_out(t):
    """Smooth ease-in-out curve (cubic smoothstep).

    Args:
        t: Time in [0, 1]

    Returns: Eased value
    """
    t = max(0, min(1, t))
    return t * t * (3 - 2 * t)


# ============================================================================
# Drawing Utilities
# ============================================================================

def draw_progress_bar(surface, x, y, width, height, filled_pct, color, bg_color=(220, 220, 220)):
    """Draw a progress bar.

    Args:
        surface: Pygame surface to draw on
        x, y: Top-left position
        width, height: Dimensions
        filled_pct: Percentage filled (0.0 - 1.0)
        color: Fill color (RGB tuple)
        bg_color: Background color (RGB tuple)
    """
    filled_pct = max(0, min(1, filled_pct))
    pygame.draw.rect(surface, bg_color, (x, y, width, height))
    if filled_pct > 0:
        filled_width = int(width * filled_pct)
        pygame.draw.rect(surface, color, (x, y, filled_width, height))
    pygame.draw.rect(surface, BLACK, (x, y, width, height), 1)  # Border


def draw_rounded_rect(surface, color, rect, radius=5):
    """Draw a rectangle with rounded corners.

    Args:
        surface: Pygame surface to draw on
        color: Fill color (RGB tuple)
        rect: Pygame Rect object
        radius: Corner radius in pixels
    """
    x, y, w, h = rect.x, rect.y, rect.width, rect.height
    pygame.draw.rect(surface, color, (x + radius, y, w - 2*radius, h))
    pygame.draw.rect(surface, color, (x, y + radius, w, h - 2*radius))
    pygame.draw.circle(surface, color, (x + radius, y + radius), radius)
    pygame.draw.circle(surface, color, (x + w - radius, y + radius), radius)
    pygame.draw.circle(surface, color, (x + radius, y + h - radius), radius)
    pygame.draw.circle(surface, color, (x + w - radius, y + h - radius), radius)
