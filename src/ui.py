"""
Sudoku Game - UI Rendering

All visual rendering logic in one place.
- Grid, buttons, messages
- Solver panel with metrics
- Menu system
- Animations and visual effects
"""

import pygame

try:
    from .constants import (
        WIDTH, HEIGHT, MENU_HEIGHT, MENU_BAR_Y,
        GRID_SIZE, CELL_SIZE, MARGIN, PANEL_WIDTH, PANEL_GAP,
        GRID_TOP, GRID_BOTTOM, MESSAGE_Y, BUTTON_Y, BUTTON_Y2,
        BUTTON_HEIGHT, BUTTON_WIDTH, BUTTON_X1, BUTTON_X2,
        PANEL_X, PANEL_Y, PANEL_HEIGHT,
        WHITE, BLACK, GRAY, LIGHT_GRAY, DARK_GRAY,
        LIGHT_BLUE, LIGHT_RED, SOFT_YELLOW,
        GREEN, RED, BLUE, CYAN, ORANGE,
        MENU_BG, MENU_TEXT, MENU_HOVER, MENU_BORDER,
        FONT_LARGE, FONT_MEDIUM, FONT_SMALL, FONT_MENU,
        lerp, ease_in_out, draw_progress_bar, draw_rounded_rect
    )
except ImportError:
    # Fallback for when imported via sys.path (from run.py)
    from constants import (
        WIDTH, HEIGHT, MENU_HEIGHT, MENU_BAR_Y,
        GRID_SIZE, CELL_SIZE, MARGIN, PANEL_WIDTH, PANEL_GAP,
        GRID_TOP, GRID_BOTTOM, MESSAGE_Y, BUTTON_Y, BUTTON_Y2,
        BUTTON_HEIGHT, BUTTON_WIDTH, BUTTON_X1, BUTTON_X2,
        PANEL_X, PANEL_Y, PANEL_HEIGHT,
        WHITE, BLACK, GRAY, LIGHT_GRAY, DARK_GRAY,
        LIGHT_BLUE, LIGHT_RED, SOFT_YELLOW,
        GREEN, RED, BLUE, CYAN, ORANGE,
        MENU_BG, MENU_TEXT, MENU_HOVER, MENU_BORDER,
        FONT_LARGE, FONT_MEDIUM, FONT_SMALL, FONT_MENU,
        lerp, ease_in_out, draw_progress_bar, draw_rounded_rect
    )


class UIRenderer:
    """Handles all visual rendering for the Sudoku game."""

    def __init__(self, screen):
        """Initialize renderer.

        Args:
            screen: Pygame surface to render to
        """
        self.screen = screen
        self.cell_animations = {}  # Track animations for each cell
        self.button_rects = {}  # Cache button rectangles

    def draw_grid(self, grid, selected_cell, solving_cell, error_cells, solving_mode=False):
        """Draw the Sudoku grid with enhanced visuals and animations.

        Args:
            grid: 9x9 grid data
            selected_cell: (row, col) of selected cell or None
            solving_cell: (row, col) of current solver cell or None
            error_cells: Set of (row, col) with conflicts
            solving_mode: True if solver is actively running
        """
        # Draw background
        pygame.draw.rect(self.screen, (248, 248, 248), (MARGIN, GRID_TOP, GRID_SIZE, GRID_SIZE))

        # Draw cells
        for i in range(9):
            for j in range(9):
                x = MARGIN + j * CELL_SIZE
                y = GRID_TOP + i * CELL_SIZE

                # Determine base color
                if solving_mode and solving_cell == (i, j):
                    base_color = SOFT_YELLOW
                elif selected_cell == (i, j):
                    base_color = LIGHT_BLUE
                elif (i, j) in error_cells:
                    base_color = LIGHT_RED
                else:
                    base_color = WHITE

                # Apply animation if active
                color = self._get_cell_color(i, j, base_color)
                pygame.draw.rect(self.screen, color, (x, y, CELL_SIZE, CELL_SIZE))

                # Draw cell border (thin)
                pygame.draw.rect(self.screen, (180, 180, 180), (x, y, CELL_SIZE, CELL_SIZE), 1)

                # Draw number if present
                if grid[i][j] != 0:
                    text = FONT_MEDIUM.render(str(grid[i][j]), True, BLACK)
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

    def draw_buttons(self, mouse_pos):
        """Draw control buttons in 2x2 grid with hover transitions.

        Args:
            mouse_pos: (x, y) current mouse position
        """
        btn_configs = [
            (pygame.Rect(BUTTON_X1, BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT), "Finalize", GREEN, (100, 200, 100)),
            (pygame.Rect(BUTTON_X2, BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT), "Clear", RED, (255, 100, 100)),
            (pygame.Rect(BUTTON_X1, BUTTON_Y2, BUTTON_WIDTH, BUTTON_HEIGHT), "Solve Algo", BLUE, (100, 160, 255)),
            (pygame.Rect(BUTTON_X2, BUTTON_Y2, BUTTON_WIDTH, BUTTON_HEIGHT), "Solve Fast", CYAN, (100, 220, 255)),
        ]

        for btn, label, btn_color, hover_color in btn_configs:
            # Check if button is hovered
            is_hovered = btn.collidepoint(mouse_pos)

            # Smooth color interpolation on hover
            color = hover_color if is_hovered else btn_color

            # Draw button shadow (3D effect, animate on hover)
            shadow_offset = 4 if is_hovered else 3
            shadow_color = (80, 80, 80) if is_hovered else (100, 100, 100)
            pygame.draw.rect(self.screen, shadow_color,
                           (btn.x + shadow_offset, btn.y + shadow_offset, btn.width, btn.height))

            # Draw button
            pygame.draw.rect(self.screen, color, btn)
            pygame.draw.rect(self.screen, BLACK, btn, 2)

            # Draw label (larger on hover)
            font_size = 22 if is_hovered else 20
            text = pygame.font.Font(None, font_size).render(label, True, WHITE)
            text_rect = text.get_rect(center=btn.center)
            self.screen.blit(text, text_rect)

    def draw_message(self, message, message_color):
        """Draw status message with toast-style background.

        Args:
            message: Text message to display
            message_color: RGB tuple for text color
        """
        if message:
            text = FONT_SMALL.render(message, True, message_color)
            # Draw background box
            padding = 8
            bg_rect = text.get_rect(topleft=(MARGIN, MESSAGE_Y))
            bg_rect.inflate_ip(2 * padding, 2 * padding)
            pygame.draw.rect(self.screen, (245, 245, 245), bg_rect)
            pygame.draw.rect(self.screen, (200, 200, 200), bg_rect, 1)
            # Draw text
            self.screen.blit(text, (MARGIN + padding, MESSAGE_Y + padding))

    def draw_solver_panel(self, step_count, backtrack_count, current_cell, candidates,
                         solving, solve_paused, show_final_panel, solve_fast):
        """Draw algorithm visualization panel with metrics.

        Args:
            step_count: Number of steps taken
            backtrack_count: Number of backtracks
            current_cell: (row, col) or None
            candidates: List of valid candidates
            solving: True if solver is active
            solve_paused: True if solver is paused
            show_final_panel: True if showing final results
            solve_fast: True if fast solve mode used
        """
        if not solving and not show_final_panel:
            return

        panel_x = MARGIN + GRID_SIZE + PANEL_GAP
        panel_y = GRID_TOP
        padding = 10
        bar_height = 16
        bar_width = PANEL_WIDTH - 2 * padding

        # Panel background and border
        pygame.draw.rect(self.screen, (245, 245, 245), (panel_x, panel_y, PANEL_WIDTH, GRID_SIZE))
        pygame.draw.rect(self.screen, (100, 150, 200), (panel_x, panel_y, PANEL_WIDTH, GRID_SIZE), 2)

        # Title
        title = pygame.font.Font(None, 26).render("Algorithm", True, (25, 55, 135))
        self.screen.blit(title, (panel_x + padding, panel_y + 8))
        title2 = pygame.font.Font(None, 24).render("Visualization", True, (25, 55, 135))
        self.screen.blit(title2, (panel_x + padding, panel_y + 32))

        y_offset = panel_y + 60

        # Current cell info
        if current_cell and (solving or show_final_panel):
            row, col = current_cell
            cell_label = pygame.font.Font(None, 20).render("Current Cell:", True, (66, 66, 66))
            self.screen.blit(cell_label, (panel_x + padding, y_offset))
            y_offset += 22
            cell_text = pygame.font.Font(None, 32).render(f"({row}, {col})", True, (25, 55, 135))
            self.screen.blit(cell_text, (panel_x + padding + 10, y_offset))
            y_offset += 40

        # Steps metric
        steps_label = pygame.font.Font(None, 20).render("Steps:", True, (66, 66, 66))
        self.screen.blit(steps_label, (panel_x + padding, y_offset))
        steps_value = pygame.font.Font(None, 24).render(str(step_count), True, GREEN)
        steps_rect = steps_value.get_rect(topleft=(panel_x + padding + 115, y_offset))
        self.screen.blit(steps_value, steps_rect)
        y_offset += 28

        # Steps progress bar
        max_steps = 200
        steps_pct = min(1.0, step_count / max_steps)
        draw_progress_bar(self.screen, panel_x + padding, y_offset, bar_width, bar_height,
                         steps_pct, GREEN, (220, 240, 220))
        y_offset += 32

        # Backtracks metric
        back_label = pygame.font.Font(None, 20).render("Backtracks:", True, (66, 66, 66))
        self.screen.blit(back_label, (panel_x + padding, y_offset))
        back_value = pygame.font.Font(None, 24).render(str(backtrack_count), True, ORANGE)
        back_rect = back_value.get_rect(topleft=(panel_x + padding + 115, y_offset))
        self.screen.blit(back_value, back_rect)
        y_offset += 28

        # Backtracks progress bar
        max_backtracks = 50
        backtrack_pct = min(1.0, backtrack_count / max_backtracks)
        draw_progress_bar(self.screen, panel_x + padding, y_offset, bar_width, bar_height,
                         backtrack_pct, ORANGE, (255, 230, 200))
        y_offset += 38

        # Candidates section
        if candidates and solving:
            cand_label = pygame.font.Font(None, 20).render("Valid Candidates:", True, (66, 66, 66))
            self.screen.blit(cand_label, (panel_x + padding, y_offset))
            y_offset += 25
            candidates_str = " ".join(map(str, sorted(candidates)))
            cand_text = pygame.font.Font(None, 26).render(candidates_str, True, BLUE)
            self.screen.blit(cand_text, (panel_x + padding, y_offset))
            y_offset += 35

        # Status indicator
        if show_final_panel:
            status = "COMPLETED"
            status_color = GREEN
        elif solve_fast:
            status = "SOLVED (FAST)"
            status_color = GREEN
        else:
            status = "PAUSED" if solve_paused else "SOLVING..."
            status_color = ORANGE if solve_paused else GREEN

        status_text = pygame.font.Font(None, 22).render(status, True, status_color)
        self.screen.blit(status_text, (panel_x + padding, y_offset))

        # Info text at bottom
        info_font = pygame.font.Font(None, 16)
        info_y = panel_y + GRID_SIZE - 85

        if show_final_panel:
            info_lines = ["Click any button", "to close panel"]
        else:
            info_lines = ["SPACE: pause/resume", "UP/DOWN: adjust speed", "ESC: stop"]

        for line in info_lines:
            info_text = info_font.render(line, True, (100, 100, 100))
            self.screen.blit(info_text, (panel_x + padding, info_y))
            info_y += 18

    def draw_menu_bar(self):
        """Draw menu bar background and text."""
        # Background
        pygame.draw.rect(self.screen, MENU_BG, (0, 0, WIDTH, MENU_HEIGHT))
        pygame.draw.line(self.screen, MENU_BORDER, (0, MENU_HEIGHT), (WIDTH, MENU_HEIGHT), 1)

        # Menu items
        file_text = FONT_MENU.render("FILE", True, MENU_TEXT)
        edit_text = FONT_MENU.render("EDIT", True, MENU_TEXT)

        self.screen.blit(file_text, (10, 6))
        self.screen.blit(edit_text, (65, 6))

    def draw_menu_dropdowns(self, menu_open, menu_hover_index, submenu_hover_index, submenu_open):
        """Draw dropdown menus (FILE and EDIT).

        Args:
            menu_open: 'FILE', 'EDIT', or None
            menu_hover_index: Which menu item is hovered
            submenu_hover_index: Which submenu item is hovered
            submenu_open: 'NEW_PUZZLE' or None
        """
        if menu_open == 'FILE':
            self._draw_file_menu(menu_hover_index, submenu_open, submenu_hover_index)
        elif menu_open == 'EDIT':
            self._draw_edit_menu(menu_hover_index)

    def _draw_file_menu(self, menu_hover_index, submenu_open, submenu_hover_index):
        """Draw FILE dropdown menu."""
        menu_items = ['New Puzzle', 'Load Puzzle...', 'Save Puzzle...', 'Exit']
        item_height = 30
        menu_width = 150
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
            if menu_hover_index == i:
                pygame.draw.rect(self.screen, MENU_HOVER, (menu_x, item_y, menu_width, item_height))
            # Text
            text = FONT_MENU.render(item, True, MENU_TEXT)
            self.screen.blit(text, (menu_x + 10, item_y + 6))

        # Draw New Puzzle submenu if open
        if submenu_open == 'NEW_PUZZLE':
            self._draw_new_puzzle_submenu(menu_x + menu_width, menu_y, submenu_hover_index)

    def _draw_new_puzzle_submenu(self, x, y, submenu_hover_index):
        """Draw New Puzzle submenu with difficulty levels.

        Args:
            x, y: Position
            submenu_hover_index: Which submenu item is hovered
        """
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
            if submenu_hover_index == i:
                pygame.draw.rect(self.screen, MENU_HOVER, (x, item_y, submenu_width, item_height))
            # Text
            text = FONT_MENU.render(item, True, MENU_TEXT)
            self.screen.blit(text, (x + 10, item_y + 6))

    def _draw_edit_menu(self, menu_hover_index):
        """Draw Edit dropdown menu."""
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
            if menu_hover_index == i:
                pygame.draw.rect(self.screen, MENU_HOVER, (menu_x, item_y, menu_width, item_height))
            # Text
            text = FONT_MENU.render(item, True, MENU_TEXT)
            self.screen.blit(text, (menu_x + 10, item_y + 6))

    def trigger_cell_animation(self, row, col, duration=200):
        """Trigger a fill animation for a cell.

        Args:
            row, col: Cell position
            duration: Animation duration in milliseconds
        """
        cell_key = (row, col)
        self.cell_animations[cell_key] = {
            'start_time': pygame.time.get_ticks(),
            'duration': duration,
            'type': 'fill'
        }

    def get_pulse_scale(self, pulse_time, duration=150):
        """Get scale for pulse animation.

        Args:
            pulse_time: Time when pulse started
            duration: Animation duration

        Returns: Scale factor (1.0 = normal, peaks at ~1.1)
        """
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

    def _get_cell_color(self, row, col, base_color):
        """Get cell color with smooth animation fade-in effect.

        Args:
            row, col: Cell position
            base_color: Target color (RGB tuple)

        Returns: Interpolated color (RGB tuple)
        """
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
