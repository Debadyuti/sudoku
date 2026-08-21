import pygame
import sys
import json
import random
from collections import deque
from pathlib import Path

# Initialize Pygame
pygame.init()

# Constants
WIDTH = 900
HEIGHT = 800  # Increased to 800 to accommodate menu bar (30px) + existing UI
# Menu bar
MENU_HEIGHT = 30
MENU_BAR_Y = 0

GRID_SIZE = 540
CELL_SIZE = GRID_SIZE // 9
BUTTON_HEIGHT = 50
BUTTON_WIDTH = 140
MARGIN = 30
PANEL_WIDTH = 260  # Right panel for algorithm visualization
PANEL_GAP = 15    # Gap between grid and panel

# Layout — derived from constants (all shifted down 30px for menu bar)
GRID_TOP = MARGIN + MENU_HEIGHT            # 60
GRID_BOTTOM = GRID_TOP + GRID_SIZE         # 600
MESSAGE_Y   = GRID_BOTTOM + 20             # 620  — message zone top
BUTTON_Y    = GRID_BOTTOM + 70             # 670  — button row top (row 1)
BUTTON_Y2   = GRID_BOTTOM + 125            # 725  — button row 2
# Two rows x two buttons grid: [Finalize, Clear] and [Solve Algo, Solve Fast]
_BTN_GAP    = (GRID_SIZE - 2 * BUTTON_WIDTH) // 3  # Center buttons within grid area
BUTTON_X1 = MARGIN + _BTN_GAP
BUTTON_X2 = MARGIN + _BTN_GAP * 2 + BUTTON_WIDTH

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
LIGHT_BLUE = (173, 216, 230)
LIGHT_RED = (255, 182, 193)
GREEN = (34, 139, 34)
RED = (220, 20, 60)
BLUE = (30, 144, 255)
DARK_GRAY = (128, 128, 128)

# Menu colors
MENU_BG = (245, 245, 245)
MENU_TEXT = (66, 66, 66)
MENU_HOVER = (220, 240, 255)
MENU_BORDER = (180, 180, 180)

# Fonts
FONT_LARGE = pygame.font.Font(None, 40)
FONT_MEDIUM = pygame.font.Font(None, 32)
FONT_SMALL = pygame.font.Font(None, 24)
FONT_MENU = pygame.font.Font(None, 18)

# Animation utilities
def lerp(a, b, t):
    """Linear interpolation between a and b, t in [0, 1]"""
    t = max(0, min(1, t))
    return a + (b - a) * t

def ease_in_out(t):
    """Smooth ease-in-out curve"""
    t = max(0, min(1, t))
    return t * t * (3 - 2 * t)

def draw_progress_bar(surface, x, y, width, height, filled_pct, color, bg_color=(220, 220, 220)):
    """Draw a progress bar. filled_pct: 0-1 (percentage filled)"""
    filled_pct = max(0, min(1, filled_pct))
    pygame.draw.rect(surface, bg_color, (x, y, width, height))
    if filled_pct > 0:
        filled_width = int(width * filled_pct)
        pygame.draw.rect(surface, color, (x, y, filled_width, height))
    pygame.draw.rect(surface, BLACK, (x, y, width, height), 1)  # Border

def draw_rounded_rect(surface, color, rect, radius=5):
    """Draw a rectangle with rounded corners"""
    x, y, w, h = rect.x, rect.y, rect.width, rect.height
    pygame.draw.rect(surface, color, (x + radius, y, w - 2*radius, h))
    pygame.draw.rect(surface, color, (x, y + radius, w, h - 2*radius))
    pygame.draw.circle(surface, color, (x + radius, y + radius), radius)
    pygame.draw.circle(surface, color, (x + w - radius, y + radius), radius)
    pygame.draw.circle(surface, color, (x + radius, y + h - radius), radius)
    pygame.draw.circle(surface, color, (x + w - radius, y + h - radius), radius)

# ============================================================================
# Puzzle Generation & File I/O Functions
# ============================================================================

def generate_complete_grid():
    """Generate a complete, valid 9x9 Sudoku grid (all cells filled)"""
    grid = [[0 for _ in range(9)] for _ in range(9)]

    def is_valid(row, col, num):
        # Check row
        if num in grid[row]:
            return False
        # Check column
        if num in [grid[i][col] for i in range(9)]:
            return False
        # Check 3x3 box
        box_row, box_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(box_row, box_row + 3):
            for j in range(box_col, box_col + 3):
                if grid[i][j] == num:
                    return False
        return True

    def solve():
        for row in range(9):
            for col in range(9):
                if grid[row][col] == 0:
                    # Try numbers in random order
                    numbers = list(range(1, 10))
                    random.shuffle(numbers)
                    for num in numbers:
                        if is_valid(row, col, num):
                            grid[row][col] = num
                            if solve():
                                return True
                            grid[row][col] = 0
                    return False
        return True

    solve()
    return grid

def generate_puzzle(difficulty='medium'):
    """Generate a puzzle by removing clues from a complete grid

    difficulty: 'easy' (15 clues), 'medium' (27 clues), 'hard' (40 clues)
    Returns: (puzzle_grid, solution_grid)
    """
    solution = generate_complete_grid()
    puzzle = [row[:] for row in solution]  # Deep copy

    # Difficulty mapping: (clues_to_keep)
    difficulty_map = {
        'easy': 15,
        'medium': 27,
        'hard': 40
    }

    clues_to_keep = difficulty_map.get(difficulty, 27)
    clues_removed = 0
    target_removes = 81 - clues_to_keep

    # Remove clues randomly
    while clues_removed < target_removes:
        row = random.randint(0, 8)
        col = random.randint(0, 8)
        if puzzle[row][col] != 0:
            puzzle[row][col] = 0
            clues_removed += 1

    return puzzle, solution

def save_puzzle(puzzle, solution, difficulty, filepath):
    """Save puzzle to JSON file

    Args:
        puzzle: 9x9 grid with 0s for empty cells
        solution: 9x9 grid with complete solution
        difficulty: 'easy', 'medium', or 'hard'
        filepath: path to save file
    """
    import datetime
    data = {
        'puzzle': puzzle,
        'solution': solution,
        'difficulty': difficulty,
        'clues': sum(1 for row in puzzle for cell in row if cell != 0),
        'created': datetime.datetime.now().isoformat()
    }

    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

def load_puzzle(filepath):
    """Load puzzle from JSON file

    Returns: (puzzle_grid, solution_grid, difficulty, clues_count) or (None, None, None, None) on error
    """
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)

        # Validate data
        if not isinstance(data.get('puzzle'), list) or len(data['puzzle']) != 9:
            return None, None, None, None

        puzzle = data['puzzle']
        solution = data.get('solution', puzzle)  # Fallback if no solution
        difficulty = data.get('difficulty', 'unknown')
        clues = data.get('clues', sum(1 for row in puzzle for cell in row if cell != 0))

        return puzzle, solution, difficulty, clues
    except Exception as e:
        print(f"Error loading puzzle: {e}")
        return None, None, None, None

class SudokuGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Sudoku Game - Educational Solver")
        self.clock = pygame.time.Clock()

        # Game state
        self.grid = [[0 for _ in range(9)] for _ in range(9)]
        self.solution = [[0 for _ in range(9)] for _ in range(9)]  # Solution grid for generated puzzles
        self.selected_cell = (0, 0)  # Auto-select top-left cell on startup
        self.error_cells = set()
        self.message = "Ready to play - Enter numbers in selected cell"
        self.message_color = BLUE

        # Button positions — 2x2 grid layout
        self.finalize_button = pygame.Rect(BUTTON_X1, BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT)
        self.clear_button    = pygame.Rect(BUTTON_X2, BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT)
        self.solve_algo_button = pygame.Rect(BUTTON_X1, BUTTON_Y2, BUTTON_WIDTH, BUTTON_HEIGHT)
        self.solve_fast_button = pygame.Rect(BUTTON_X2, BUTTON_Y2, BUTTON_WIDTH, BUTTON_HEIGHT)

        # Solver visualization state
        self.solving = False
        self.solve_paused = False
        self.solve_fast = False
        self.solver_state = None
        self.current_cell = None
        self.candidates = []
        self.step_count = 0
        self.backtrack_count = 0
        self.step_time = 0
        self.step_delay = 300  # milliseconds between solver steps
        self.show_final_panel = False  # Keep panel visible after solving

        # Animation state
        self.mouse_pos = (0, 0)  # Current mouse position for hover detection
        self.button_hover = None  # Which button is being hovered
        self.message_fade_time = 0  # Time remaining for message fade animation
        self.hovered_button_start_time = 0  # Track hover start for smooth transitions
        self.last_frame_time = pygame.time.get_ticks()  # For delta-time calculations
        self.cell_animations = {}  # Track animations for each cell (row, col): {start_time, duration, type}
        self.last_step_count = 0  # For pulse animation on stat change
        self.last_backtrack_count = 0  # For pulse animation on stat change
        self.step_pulse_time = 0  # Time when last pulse animation started
        self.backtrack_pulse_time = 0  # Time when last pulse animation started

        # Menu state
        self.menu_open = None  # 'FILE', 'EDIT', or None
        self.menu_hover_index = -1  # Which menu item is hovered
        self.submenu_open = None  # 'NEW_PUZZLE' or None (for submenus)
        self.submenu_hover_index = -1  # Which submenu item is hovered
        
    def get_cell_color(self, row, col, base_color):
        """Get cell color with smooth animation fade-in effect"""
        cell_key = (row, col)
        now = pygame.time.get_ticks()

        # Check if cell is animating
        if cell_key in self.cell_animations:
            anim = self.cell_animations[cell_key]
            elapsed = now - anim['start_time']
            duration = anim['duration']

            if elapsed < duration:
                # Smooth fade-in using easing
                progress = ease_in_out(elapsed / duration)
                # Interpolate from white to target color
                r = int(lerp(255, base_color[0], progress))
                g = int(lerp(255, base_color[1], progress))
                b = int(lerp(255, base_color[2], progress))
                return (r, g, b)
            else:
                # Animation complete
                del self.cell_animations[cell_key]
                return base_color
        return base_color

    def draw_menu_bar(self):
        """Draw menu bar background and text only (dropdown drawn later)"""
        # Background
        pygame.draw.rect(self.screen, MENU_BG, (0, 0, WIDTH, MENU_HEIGHT))
        pygame.draw.line(self.screen, MENU_BORDER, (0, MENU_HEIGHT), (WIDTH, MENU_HEIGHT), 1)

        # Menu items
        file_text = FONT_MENU.render("FILE", True, MENU_TEXT)
        edit_text = FONT_MENU.render("EDIT", True, MENU_TEXT)

        self.screen.blit(file_text, (10, 6))
        self.screen.blit(edit_text, (65, 6))

    def update_menu_hover(self):
        """Update menu hover state based on mouse position"""
        x, y = self.mouse_pos

        # Update menu hover if menu is open
        if self.menu_open == 'FILE':
            # Check if mouse is over submenu (New Puzzle submenu is at x >= 190)
            if x >= 190 and y >= MENU_HEIGHT:
                # Mouse is over submenu area - keep "New Puzzle" (index 0) highlighted
                self.menu_hover_index = 0
                self.submenu_hover_index = (y - MENU_HEIGHT) // 30
            elif 10 < x < 190 and y >= MENU_HEIGHT:
                # Mouse is over main menu items
                self.menu_hover_index = (y - MENU_HEIGHT) // 30
                self.submenu_hover_index = -1
            else:
                # Mouse is not over menu
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

    def draw_menu_dropdowns(self):
        """Draw menu dropdown overlays (called last so they appear on top)"""
        # Update hover states based on current mouse position
        self.update_menu_hover()

        if self.menu_open == 'FILE':
            self._draw_file_menu()
        elif self.menu_open == 'EDIT':
            self._draw_edit_menu()

    def _draw_file_menu(self):
        """Draw File dropdown menu with submenus"""
        menu_items = ['New Puzzle', 'Load Puzzle...', 'Save Puzzle...', 'Exit']
        item_height = 30
        menu_width = 180
        menu_x = 10
        menu_y = MENU_HEIGHT

        # Draw menu background
        total_height = len(menu_items) * item_height
        pygame.draw.rect(self.screen, WHITE, (menu_x, menu_y, menu_width, total_height))
        pygame.draw.rect(self.screen, MENU_BORDER, (menu_x, menu_y, menu_width, total_height), 1)

        # Draw items
        for i, item in enumerate(menu_items):
            item_y = menu_y + i * item_height
            # Hover highlight
            if self.menu_hover_index == i:
                pygame.draw.rect(self.screen, MENU_HOVER, (menu_x, item_y, menu_width, item_height))
            # Text
            text = FONT_MENU.render(item, True, MENU_TEXT)
            self.screen.blit(text, (menu_x + 10, item_y + 6))

            # Draw arrow indicator for items with submenus
            if i == 0:  # New Puzzle has submenu
                arrow = FONT_MENU.render("▶", True, MENU_TEXT)
                self.screen.blit(arrow, (menu_x + menu_width - 20, item_y + 6))

        # Draw submenu if "New Puzzle" is hovered
        if self.menu_hover_index == 0:
            self._draw_new_puzzle_submenu(menu_x + menu_width, menu_y)

    def _draw_new_puzzle_submenu(self, x, y):
        """Draw New Puzzle submenu with difficulty levels"""
        submenu_items = ['Easy (E)', 'Medium (M)', 'Hard (H)']
        item_height = 30
        submenu_width = 150

        # Draw submenu background
        total_height = len(submenu_items) * item_height
        pygame.draw.rect(self.screen, WHITE, (x, y, submenu_width, total_height))
        pygame.draw.rect(self.screen, MENU_BORDER, (x, y, submenu_width, total_height), 1)

        # Draw items
        for i, item in enumerate(submenu_items):
            item_y = y + i * item_height
            # Hover highlight
            if self.submenu_hover_index == i:
                pygame.draw.rect(self.screen, MENU_HOVER, (x, item_y, submenu_width, item_height))
            # Text
            text = FONT_MENU.render(item, True, MENU_TEXT)
            self.screen.blit(text, (x + 10, item_y + 6))

    def _draw_edit_menu(self):
        """Draw Edit dropdown menu"""
        menu_items = ['Clear Grid']
        item_height = 30
        menu_width = 150
        menu_x = 65
        menu_y = MENU_HEIGHT

        # Draw menu background
        total_height = len(menu_items) * item_height
        pygame.draw.rect(self.screen, WHITE, (menu_x, menu_y, menu_width, total_height))
        pygame.draw.rect(self.screen, MENU_BORDER, (menu_x, menu_y, menu_width, total_height), 1)

        # Draw items
        for i, item in enumerate(menu_items):
            item_y = menu_y + i * item_height
            # Hover highlight
            if self.menu_hover_index == i:
                pygame.draw.rect(self.screen, MENU_HOVER, (menu_x, item_y, menu_width, item_height))
            # Text
            text = FONT_MENU.render(item, True, MENU_TEXT)
            self.screen.blit(text, (menu_x + 10, item_y + 6))

    def handle_menu_click(self, mouse_pos):
        """Handle menu bar and submenu clicks"""
        x, y = mouse_pos

        # Check if click in menu bar
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
        # Check if click on submenu item (New Puzzle submenu at x >= 190)
        elif self.menu_open == 'FILE' and x >= 190 and y >= MENU_HEIGHT and y < MENU_HEIGHT + 90:
            # Submenu has 3 items, each 30px high
            submenu_item_index = (y - MENU_HEIGHT) // 30
            if 0 <= submenu_item_index < 3:  # 3 items in NEW PUZZLE submenu
                self._handle_new_puzzle_click(submenu_item_index)
                self.menu_open = None
                self.menu_hover_index = -1
                self.submenu_open = None
                self.submenu_hover_index = -1
                return True
        # Check if click on FILE menu item
        elif self.menu_open == 'FILE' and 10 < x < 190 and y >= MENU_HEIGHT:
            item_index = (y - MENU_HEIGHT) // 30
            if 0 <= item_index < 4:  # 4 items in FILE menu
                if item_index == 0:  # "New Puzzle" - open submenu
                    self.submenu_open = 'NEW_PUZZLE'
                else:
                    self._handle_file_menu_click(item_index)
                    self.menu_open = None
                    self.submenu_open = None
                self.menu_hover_index = -1
                self.submenu_hover_index = -1
                return True
        # Check if click on EDIT menu item
        elif self.menu_open == 'EDIT' and 65 < x < 215 and y >= MENU_HEIGHT:
            item_index = (y - MENU_HEIGHT) // 30
            if 0 <= item_index < 1:  # 1 item in EDIT menu
                self._handle_edit_menu_click(item_index)
                self.menu_open = None
                self.submenu_open = None
                self.menu_hover_index = -1
                self.submenu_hover_index = -1
                return True

        # Click outside menu
        if self.menu_open:
            self.menu_open = None
            self.menu_hover_index = -1
            self.submenu_open = None
            self.submenu_hover_index = -1
            return True

        return False

    def _handle_new_puzzle_click(self, difficulty_index):
        """Handle New Puzzle submenu click (Easy=0, Medium=1, Hard=2)"""
        difficulties = ['easy', 'medium', 'hard']
        if 0 <= difficulty_index < 3:
            self._generate_new_puzzle(difficulties[difficulty_index])

    def _handle_file_menu_click(self, item_index):
        """Handle File menu item click"""
        if item_index == 1:  # Load Puzzle
            self._load_puzzle_dialog()
        elif item_index == 2:  # Save Puzzle
            self._save_puzzle_dialog()
        elif item_index == 3:  # Exit
            return False  # Will trigger quit in main loop

    def _handle_edit_menu_click(self, item_index):
        """Handle Edit menu item click"""
        if item_index == 0:  # Clear Grid
            self.clear_grid()
            self.menu_open = None

    def _load_puzzle_dialog(self):
        """Simple load puzzle dialog"""
        try:
            # Try to load from default puzzles folder
            puzzle_dir = Path('sudoku_puzzles')
            puzzle_files = list(puzzle_dir.glob('*.json'))

            if not puzzle_files:
                self.message = "No puzzle files found in sudoku_puzzles/"
                self.message_color = RED
                return

            # Load the most recent file
            latest_file = max(puzzle_files, key=lambda p: p.stat().st_mtime)
            puzzle, solution, difficulty, clues = load_puzzle(str(latest_file))

            if puzzle is None:
                self.message = "Error loading puzzle file"
                self.message_color = RED
                return

            self.grid = puzzle
            self.show_final_panel = False
            self.solving = False
            self.message = f"Puzzle loaded: {difficulty} ({clues} clues)"
            self.message_color = GREEN
        except Exception as e:
            self.message = f"Error: {str(e)}"
            self.message_color = RED

    def _save_puzzle_dialog(self):
        """Simple save puzzle dialog"""
        try:
            puzzle_dir = Path('sudoku_puzzles')
            puzzle_dir.mkdir(exist_ok=True)

            # Generate filename with timestamp
            import datetime
            filename = puzzle_dir / f"puzzle_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

            # Determine difficulty from clue count
            clues = sum(1 for row in self.grid for cell in row if cell != 0)
            if clues <= 20:
                difficulty = 'easy'
            elif clues <= 35:
                difficulty = 'medium'
            else:
                difficulty = 'hard'

            # For now, puzzle is solution (user hasn't solved yet)
            solution = [row[:] for row in self.grid]

            save_puzzle(self.grid, solution, difficulty, str(filename))
            self.message = f"Puzzle saved: {filename.name}"
            self.message_color = GREEN
        except Exception as e:
            self.message = f"Error saving: {str(e)}"
            self.message_color = RED

    def _generate_new_puzzle(self, difficulty):
        """Generate a new puzzle of given difficulty"""
        self.message = f"Generating {difficulty} puzzle..."
        self.message_color = BLUE
        pygame.display.flip()  # Show message immediately

        puzzle, solution = generate_puzzle(difficulty)
        self.grid = puzzle
        self.solution = solution
        self.error_cells = set()
        self.selected_cell = (0, 0)
        self.solving = False
        self.show_final_panel = False

        clue_count = sum(1 for row in puzzle for cell in row if cell != 0)
        self.message = f"New {difficulty} puzzle generated! ({clue_count} clues)"
        self.message_color = GREEN
        self.waiting_for_difficulty = False

    def draw_grid(self):
        """Draw the Sudoku grid with enhanced visuals and animations"""
        # Draw background
        pygame.draw.rect(self.screen, (248, 248, 248), (MARGIN, GRID_TOP, GRID_SIZE, GRID_SIZE))

        # Draw cells
        for i in range(9):
            for j in range(9):
                x = MARGIN + j * CELL_SIZE
                y = GRID_TOP + i * CELL_SIZE

                # Determine base color
                if self.solving and self.current_cell == (i, j):
                    base_color = (255, 250, 200)  # Soft yellow
                elif self.selected_cell == (i, j):
                    base_color = (150, 220, 255)  # Enhanced blue
                elif (i, j) in self.error_cells:
                    base_color = (255, 200, 200)  # Soft red
                else:
                    base_color = WHITE

                # Apply animation if active
                color = self.get_cell_color(i, j, base_color)
                pygame.draw.rect(self.screen, color, (x, y, CELL_SIZE, CELL_SIZE))

                # Draw cell border (thin)
                pygame.draw.rect(self.screen, (180, 180, 180), (x, y, CELL_SIZE, CELL_SIZE), 1)

                # Draw number if present with smooth fade-in
                if self.grid[i][j] != 0:
                    text = FONT_MEDIUM.render(str(self.grid[i][j]), True, BLACK)
                    text_rect = text.get_rect(center=(x + CELL_SIZE // 2, y + CELL_SIZE // 2))
                    self.screen.blit(text, text_rect)

        # Draw grid lines with thickness for 3x3 boxes
        box_color = (25, 55, 135)  # Dark blue for box separators
        for i in range(10):
            thickness = 3 if i % 3 == 0 else 1
            line_color = box_color if i % 3 == 0 else (64, 64, 64)
            # Horizontal lines
            pygame.draw.line(self.screen, line_color,
                           (MARGIN, GRID_TOP + i * CELL_SIZE),
                           (MARGIN + GRID_SIZE, GRID_TOP + i * CELL_SIZE),
                           thickness)
            # Vertical lines
            pygame.draw.line(self.screen, line_color,
                           (MARGIN + i * CELL_SIZE, GRID_TOP),
                           (MARGIN + i * CELL_SIZE, GRID_TOP + GRID_SIZE),
                           thickness)
    
    def draw_buttons(self):
        """Draw the control buttons in 2x2 grid with smooth hover transitions"""
        btn_configs = [
            (self.finalize_button, "Finalize", (76, 175, 80), (100, 200, 100)),      # Green
            (self.clear_button, "Clear", (229, 57, 53), (255, 100, 100)),             # Red
            (self.solve_algo_button, "Solve Algo", (66, 133, 244), (100, 160, 255)), # Blue
            (self.solve_fast_button, "Solve Fast", (0, 188, 212), (100, 220, 255)),  # Cyan
        ]

        for btn, label, btn_color, hover_color in btn_configs:
            # Check if button is hovered
            is_hovered = btn.collidepoint(self.mouse_pos)

            # Smooth color interpolation on hover (simple lerp, no complex tracking needed)
            # For smooth hover without tracking per-button, use instantaneous lerp based on state
            color = hover_color if is_hovered else btn_color

            # Draw button shadow (3D effect, animate shadow on hover)
            shadow_offset = 4 if is_hovered else 3
            shadow_color = (80, 80, 80) if is_hovered else (100, 100, 100)
            pygame.draw.rect(self.screen, shadow_color,
                           (btn.x + shadow_offset, btn.y + shadow_offset, btn.width, btn.height))

            # Draw button
            pygame.draw.rect(self.screen, color, btn)
            pygame.draw.rect(self.screen, BLACK, btn, 2)

            # Draw label (larger, clearer font on hover for emphasis)
            font_size = 22 if is_hovered else 20
            text = pygame.font.Font(None, font_size).render(label, True, WHITE)
            text_rect = text.get_rect(center=btn.center)
            self.screen.blit(text, text_rect)
    
    def draw_message(self):
        """Draw status message with toast-style background"""
        if self.message:
            text = FONT_SMALL.render(self.message, True, self.message_color)
            # Draw background box
            padding = 8
            bg_rect = text.get_rect(topleft=(MARGIN, MESSAGE_Y))
            bg_rect.inflate_ip(2 * padding, 2 * padding)
            pygame.draw.rect(self.screen, (245, 245, 245), bg_rect)
            pygame.draw.rect(self.screen, (200, 200, 200), bg_rect, 1)
            # Draw text
            self.screen.blit(text, (MARGIN + padding, MESSAGE_Y + padding))

    def draw_solver_panel(self):
        """Draw algorithm visualization panel with metrics and progress bars"""
        if not self.solving and not self.show_final_panel:
            return

        panel_x = MARGIN + GRID_SIZE + PANEL_GAP
        panel_y = GRID_TOP
        padding = 10
        bar_height = 16
        bar_width = PANEL_WIDTH - 2 * padding

        # Panel background and border
        pygame.draw.rect(self.screen, (245, 245, 245), (panel_x, panel_y, PANEL_WIDTH, GRID_SIZE))
        pygame.draw.rect(self.screen, (100, 150, 200), (panel_x, panel_y, PANEL_WIDTH, GRID_SIZE), 2)

        # Title (clearer, larger)
        title = pygame.font.Font(None, 26).render("Algorithm", True, (25, 55, 135))
        self.screen.blit(title, (panel_x + padding, panel_y + 8))
        title2 = pygame.font.Font(None, 24).render("Visualization", True, (25, 55, 135))
        self.screen.blit(title2, (panel_x + padding, panel_y + 32))

        y_offset = panel_y + 60

        # Current cell info (if solving)
        if self.current_cell and (self.solving or self.show_final_panel):
            row, col = self.current_cell
            cell_label = pygame.font.Font(None, 20).render("Current Cell:", True, (66, 66, 66))
            self.screen.blit(cell_label, (panel_x + padding, y_offset))
            y_offset += 22
            cell_text = pygame.font.Font(None, 32).render(f"({row}, {col})", True, (25, 55, 135))
            self.screen.blit(cell_text, (panel_x + padding + 10, y_offset))
            y_offset += 40

        # Steps metric with progress bar and pulse animation
        steps_label = pygame.font.Font(None, 20).render("Steps:", True, (66, 66, 66))
        self.screen.blit(steps_label, (panel_x + padding, y_offset))

        # Pulse animation on step change
        step_scale = self.get_pulse_scale(self.step_pulse_time)
        step_font_size = int(24 * step_scale)  # Larger base size
        steps_value = pygame.font.Font(None, step_font_size).render(str(self.step_count), True, (76, 175, 80))
        steps_rect = steps_value.get_rect(topleft=(panel_x + padding + 115, y_offset))
        self.screen.blit(steps_value, steps_rect)
        y_offset += 28

        # Steps progress bar (estimate: max 200 steps for visualization)
        max_steps = 200
        steps_pct = min(1.0, self.step_count / max_steps)
        draw_progress_bar(self.screen, panel_x + padding, y_offset, bar_width, bar_height,
                         steps_pct, (76, 175, 80), (220, 240, 220))
        y_offset += 32

        # Backtracks metric with progress bar and pulse animation
        back_label = pygame.font.Font(None, 20).render("Backtracks:", True, (66, 66, 66))
        self.screen.blit(back_label, (panel_x + padding, y_offset))

        # Pulse animation on backtrack change
        back_scale = self.get_pulse_scale(self.backtrack_pulse_time)
        back_font_size = int(24 * back_scale)  # Larger base size
        back_value = pygame.font.Font(None, back_font_size).render(str(self.backtrack_count), True, (255, 152, 0))
        back_rect = back_value.get_rect(topleft=(panel_x + padding + 115, y_offset))
        self.screen.blit(back_value, back_rect)
        y_offset += 28

        # Backtracks progress bar (estimate: max 50 backtracks)
        max_backtracks = 50
        backtrack_pct = min(1.0, self.backtrack_count / max_backtracks)
        draw_progress_bar(self.screen, panel_x + padding, y_offset, bar_width, bar_height,
                         backtrack_pct, (255, 152, 0), (255, 230, 200))
        y_offset += 38

        # Candidates section
        if self.candidates and self.solving:
            cand_label = pygame.font.Font(None, 20).render("Valid Candidates:", True, (66, 66, 66))
            self.screen.blit(cand_label, (panel_x + padding, y_offset))
            y_offset += 25
            candidates_str = " ".join(map(str, sorted(self.candidates)))
            cand_text = pygame.font.Font(None, 26).render(candidates_str, True, (66, 133, 244))
            self.screen.blit(cand_text, (panel_x + padding, y_offset))
            y_offset += 35

        # Status indicator
        if self.show_final_panel:
            status = "COMPLETED"
            status_color = (76, 175, 80)
        elif self.solve_fast:
            status = "SOLVED (FAST)"
            status_color = (76, 175, 80)
        else:
            status = "PAUSED" if self.solve_paused else "SOLVING..."
            status_color = (255, 152, 0) if self.solve_paused else (76, 175, 80)

        status_text = pygame.font.Font(None, 22).render(status, True, status_color)
        self.screen.blit(status_text, (panel_x + padding, y_offset))

        # Info text at bottom (clearer, larger)
        info_font = pygame.font.Font(None, 16)
        info_y = panel_y + GRID_SIZE - 85

        if self.show_final_panel:
            info_lines = ["Click any button", "to close panel"]
        elif self.solving and not self.solve_fast:
            info_lines = ["SPACE: pause/resume", "UP/DOWN: speed", "ESC: stop"]
        else:
            info_lines = []

        for i, line in enumerate(info_lines):
            text = info_font.render(line, True, (120, 120, 120))  # Slightly darker for clarity
            self.screen.blit(text, (panel_x + padding, info_y + i * 20))
    
    def handle_click(self, pos):
        """Handle mouse click events"""
        x, y = pos

        # Check menu bar first
        if self.handle_menu_click(pos):
            return

        # Check if click is on grid
        if MARGIN <= x <= MARGIN + GRID_SIZE and GRID_TOP <= y <= GRID_TOP + GRID_SIZE:
            col = (x - MARGIN) // CELL_SIZE
            row = (y - GRID_TOP) // CELL_SIZE
            self.selected_cell = (row, col)
            self.message = ""
            return

        # Check button clicks
        if self.finalize_button.collidepoint(pos):
            self.finalize_puzzle()
        elif self.clear_button.collidepoint(pos):
            self.clear_grid()
        elif self.solve_algo_button.collidepoint(pos):
            self.solve_puzzle(animated=True)
        elif self.solve_fast_button.collidepoint(pos):
            self.solve_puzzle(animated=False)
    
    def handle_key(self, key, mod=0):
        """Handle keyboard input"""
        # --- Handle difficulty selection ---
        if self.waiting_for_difficulty:
            if key == pygame.K_e:  # Easy
                self._generate_new_puzzle('easy')
            elif key == pygame.K_m:  # Medium
                self._generate_new_puzzle('medium')
            elif key == pygame.K_h:  # Hard
                self._generate_new_puzzle('hard')
            elif key == pygame.K_ESCAPE:
                self.waiting_for_difficulty = False
                self.message = ""
            return

        # --- Solver controls ---
        if key == pygame.K_SPACE and self.solving:
            self.solve_paused = not self.solve_paused
            if self.solve_paused:
                self.message = "Solver paused (SPACE to resume)"
                self.message_color = DARK_GRAY
            else:
                self.message = "Solving... (Press SPACE to pause, ESC to stop)"
                self.message_color = BLUE
            return

        if key == pygame.K_ESCAPE and self.solving:
            self.solving = False
            self.message = "Solver stopped"
            self.message_color = RED
            self.current_cell = None
            return

        # Speed controls while solving
        if self.solving:
            if key == pygame.K_UP:  # Faster
                self.step_delay = max(50, self.step_delay - 50)
                self.message = f"Speed: {100 - (self.step_delay // 5)}%"
                self.message_color = BLUE
                return
            elif key == pygame.K_DOWN:  # Slower
                self.step_delay = min(1000, self.step_delay + 50)
                self.message = f"Speed: {100 - (self.step_delay // 5)}%"
                self.message_color = BLUE
                return

        # --- Navigation: Tab / Shift+Tab ---
        if key == pygame.K_TAB:
            if self.selected_cell is None:
                self.selected_cell = (0, 0)
            else:
                row, col = self.selected_cell
                index = row * 9 + col
                if mod & pygame.KMOD_SHIFT:
                    index = (index - 1) % 81   # Shift+Tab: go backward
                else:
                    index = (index + 1) % 81   # Tab: go forward
                self.selected_cell = (index // 9, index % 9)
            self.message = ""
            return

        # --- Navigation: Arrow keys ---
        if key in (pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT):
            if self.selected_cell is None:
                self.selected_cell = (0, 0)
            else:
                row, col = self.selected_cell
                if key == pygame.K_UP:
                    self.selected_cell = ((row - 1) % 9, col)
                elif key == pygame.K_DOWN:
                    self.selected_cell = ((row + 1) % 9, col)
                elif key == pygame.K_LEFT:
                    self.selected_cell = (row, (col - 1) % 9)
                elif key == pygame.K_RIGHT:
                    self.selected_cell = (row, (col + 1) % 9)
            self.message = ""
            return

        if self.selected_cell is None:
            return

        row, col = self.selected_cell

        # Number keys (1-9)
        if pygame.K_1 <= key <= pygame.K_9:
            self.grid[row][col] = key - pygame.K_0
            self.message = ""
            self.error_cells.clear()
        # Keypad numbers
        elif pygame.K_KP1 <= key <= pygame.K_KP9:
            self.grid[row][col] = key - pygame.K_KP1 + 1
            self.message = ""
            self.error_cells.clear()
        # Delete/Backspace
        elif key in (pygame.K_BACKSPACE, pygame.K_DELETE, pygame.K_0, pygame.K_KP0):
            self.grid[row][col] = 0
            self.message = ""
            self.error_cells.clear()
    
    def is_valid_placement(self, row, col, num):
        """Check if placing num at (row, col) is valid"""
        if num == 0:
            return True
        
        # Check row
        for j in range(9):
            if j != col and self.grid[row][j] == num:
                return False
        
        # Check column
        for i in range(9):
            if i != row and self.grid[i][col] == num:
                return False
        
        # Check 3x3 box
        box_row, box_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(box_row, box_row + 3):
            for j in range(box_col, box_col + 3):
                if (i, j) != (row, col) and self.grid[i][j] == num:
                    return False
        
        return True
    
    def find_errors(self):
        """Find all cells with conflicts"""
        errors = set()
        
        for i in range(9):
            for j in range(9):
                if self.grid[i][j] != 0:
                    if not self.is_valid_placement(i, j, self.grid[i][j]):
                        errors.add((i, j))
        
        return errors
    
    def is_complete(self):
        """Check if grid is completely filled"""
        for i in range(9):
            for j in range(9):
                if self.grid[i][j] == 0:
                    return False
        return True
    
    def finalize_puzzle(self):
        """Validate the puzzle — check Sudoku rules first, then completeness"""
        errors = self.find_errors()

        if errors:
            self.error_cells = errors
            self.message = f"Found {len(errors)} conflict(s)!"
            self.message_color = RED
        elif not self.is_complete():
            self.error_cells.clear()
            self.message = "No conflicts, but puzzle is incomplete!"
            self.message_color = RED
        else:
            self.error_cells.clear()
            self.message = "Congratulations! Puzzle solved correctly!"
            self.message_color = GREEN
    
    def clear_grid(self):
        """Clear the entire grid"""
        self.grid = [[0 for _ in range(9)] for _ in range(9)]
        self.selected_cell = (0, 0)  # Auto-select top-left
        self.error_cells.clear()
        self.message = "Grid cleared!"
        self.message_color = BLUE
        self.show_final_panel = False
    
    def solve_puzzle(self, animated=True):
        """Start solving: animated step-by-step or fast"""
        self.solving = True
        self.solve_fast = not animated
        self.solve_paused = False
        self.step_count = 0
        self.backtrack_count = 0
        self.current_cell = None
        self.candidates = []
        self.step_time = pygame.time.get_ticks()
        self.show_final_panel = False

        if animated:
            self.solver_gen = self._solve_with_steps()
            self.message = "Solving... (Press SPACE to pause, ESC to stop)"
        else:
            # Fast solve: run to completion immediately
            self.solve_fast_complete()

    def solve_fast_complete(self):
        """Solve instantly without animation"""
        if self.solve_backtrack():
            self.message = "Puzzle solved instantly!"
            self.message_color = GREEN
            self.show_final_panel = True
        else:
            self.message = "No solution exists!"
            self.message_color = RED
            self.show_final_panel = True
        self.solving = False
        self.error_cells.clear()

    def solve_backtrack(self):
        """Standard backtracking solver without animation"""
        empty = self.find_empty_cell()
        if not empty:
            return True

        row, col = empty
        for num in range(1, 10):
            if self.is_valid_placement(row, col, num):
                self.grid[row][col] = num
                if self.solve_backtrack():
                    return True
                self.grid[row][col] = 0

        return False

    def get_candidates(self, row, col):
        """Get list of valid numbers for a cell"""
        candidates = []
        for num in range(1, 10):
            if self.is_valid_placement(row, col, num):
                candidates.append(num)
        return candidates

    def _solve_with_steps(self):
        """Generator that yields after each solve step for animation"""
        def backtrack():
            # Find empty cell
            empty = self.find_empty_cell()
            if not empty:
                return True

            row, col = empty
            self.current_cell = (row, col)
            self.candidates = self.get_candidates(row, col)
            self.step_count += 1
            yield  # Pause here to display this step

            # Try numbers 1-9
            for num in self.candidates:
                self.grid[row][col] = num
                self.trigger_cell_animation(row, col, duration=150)  # Smooth fill animation
                yield  # Show filled cell
                if (yield from backtrack()):
                    return True
                self.grid[row][col] = 0  # Backtrack
                self.backtrack_count += 1
                self.trigger_cell_animation(row, col, duration=100)  # Quick fade back
                yield  # Show backtrack

            return False

        result = yield from backtrack()
        return result

    def solve_step_by_step(self):
        """Perform one step of backtracking"""
        if not self.solving or self.solve_paused:
            return False

        # Check if enough time passed for next step
        now = pygame.time.get_ticks()
        if now - self.step_time < self.step_delay:
            return False

        self.step_time = now

        try:
            next(self.solver_gen)
            # Trigger pulse animations on stat changes
            if self.step_count != self.last_step_count:
                self.step_pulse_time = now
                self.last_step_count = self.step_count
            if self.backtrack_count != self.last_backtrack_count:
                self.backtrack_pulse_time = now
                self.last_backtrack_count = self.backtrack_count
        except StopIteration as e:
            result = e.value
            if result:
                self.message = f"Puzzle solved! {self.step_count} steps, {self.backtrack_count} backtracks"
                self.message_color = GREEN
                self.show_final_panel = True
            else:
                self.message = "No solution exists!"
                self.message_color = RED
                self.show_final_panel = True
            self.solving = False
            self.current_cell = None
            return True

        return False
    
    def trigger_cell_animation(self, row, col, duration=200):
        """Trigger a fill animation for a cell (smooth fade-in)"""
        cell_key = (row, col)
        self.cell_animations[cell_key] = {
            'start_time': pygame.time.get_ticks(),
            'duration': duration,
            'type': 'fill'
        }

    def get_pulse_scale(self, pulse_time, duration=150):
        """Get scale for pulse animation (1.0 = normal, peaks at ~1.1)"""
        now = pygame.time.get_ticks()
        elapsed = now - pulse_time
        if elapsed > duration:
            return 1.0
        progress = ease_in_out(elapsed / duration)
        # Peak at 0.5 of duration, then return to 1.0
        peak = 1.1
        if progress < 0.5:
            return lerp(1.0, peak, progress * 2)
        else:
            return lerp(peak, 1.0, (progress - 0.5) * 2)

    def find_empty_cell(self):
        """Find the next empty cell (0)"""
        for i in range(9):
            for j in range(9):
                if self.grid[i][j] == 0:
                    return (i, j)
        return None
    
    def run(self):
        """Main game loop"""
        running = True

        while running:
            # Track mouse position for hover effects
            self.mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(event.pos)
                elif event.type == pygame.KEYDOWN:
                    self.handle_key(event.key, event.mod)

            # Update solver animation
            if self.solving:
                self.solve_step_by_step()

            # Draw everything
            self.screen.fill((250, 250, 250))  # Light gray background
            self.draw_menu_bar()  # Draw menu bar background
            self.draw_grid()
            self.draw_buttons()
            self.draw_message()
            if self.solving or self.show_final_panel:
                self.draw_solver_panel()
            self.draw_menu_dropdowns()  # Draw menu dropdowns LAST (on top)

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = SudokuGame()
    game.run()

# Made with Bob
