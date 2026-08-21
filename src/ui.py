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
        LIGHT_BLUE, LIGHT_RED, SOFT_YELLOW, FROZEN_BG, FROZEN_TEXT,
        GREEN, RED, BLUE, CYAN, ORANGE,
        MENU_BG, MENU_TEXT, MENU_HOVER, MENU_BORDER,
        FONT_LARGE, FONT_MEDIUM, FONT_SMALL, FONT_MENU,
        lerp, ease_in_out, draw_progress_bar, draw_rounded_rect, interpolate_color
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
        LIGHT_BLUE, LIGHT_RED, SOFT_YELLOW, FROZEN_BG, FROZEN_TEXT,
        GREEN, RED, BLUE, CYAN, ORANGE,
        MENU_BG, MENU_TEXT, MENU_HOVER, MENU_BORDER,
        FONT_LARGE, FONT_MEDIUM, FONT_SMALL, FONT_MENU,
        lerp, ease_in_out, draw_progress_bar, draw_rounded_rect, interpolate_color
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

    def draw_grid(self, grid, selected_cell, solving_cell, error_cells, solving_mode=False, frozen_cells=None):
        """Draw the Sudoku grid with enhanced visuals and animations.

        Args:
            grid: 9x9 grid data
            selected_cell: (row, col) of selected cell or None
            solving_cell: (row, col) of current solver cell or None
            error_cells: Set of (row, col) with conflicts
            solving_mode: True if solver is actively running
            frozen_cells: Set of (row, col) with immutable initial cells
        """
        if frozen_cells is None:
            frozen_cells = set()

        # Draw background with subtle gradient effect
        pygame.draw.rect(self.screen, (250, 250, 250), (MARGIN, GRID_TOP, GRID_SIZE, GRID_SIZE))

        # Draw cells
        for i in range(9):
            for j in range(9):
                x = MARGIN + j * CELL_SIZE
                y = GRID_TOP + i * CELL_SIZE

                # Determine base color
                if (i, j) in frozen_cells:
                    base_color = FROZEN_BG
                elif solving_mode and solving_cell == (i, j):
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

                # Draw subtle shadow on right/bottom for depth
                if grid[i][j] != 0 or selected_cell == (i, j):
                    shadow_color = (220, 220, 220)
                    pygame.draw.line(self.screen, shadow_color, (x + CELL_SIZE - 1, y + 1), (x + CELL_SIZE - 1, y + CELL_SIZE - 1), 1)
                    pygame.draw.line(self.screen, shadow_color, (x + 1, y + CELL_SIZE - 1), (x + CELL_SIZE - 1, y + CELL_SIZE - 1), 1)

                # Draw cell border
                border_color = (100, 100, 100) if selected_cell == (i, j) else (180, 180, 180)
                border_width = 2 if selected_cell == (i, j) else 1
                pygame.draw.rect(self.screen, border_color, (x, y, CELL_SIZE, CELL_SIZE), border_width)

                # Draw number if present
                if grid[i][j] != 0:
                    text_color = FROZEN_TEXT if (i, j) in frozen_cells else BLACK
                    text = FONT_MEDIUM.render(str(grid[i][j]), True, text_color)
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
        """Draw control buttons in 2x2 grid with smooth hover transitions.

        Args:
            mouse_pos: (x, y) current mouse position
        """
        btn_configs = [
            (pygame.Rect(BUTTON_X1, BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT), "Finalize", "F", GREEN, (100, 200, 100)),
            (pygame.Rect(BUTTON_X2, BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT), "Clear", "C", RED, (255, 100, 100)),
            (pygame.Rect(BUTTON_X1, BUTTON_Y2, BUTTON_WIDTH, BUTTON_HEIGHT), "Solve Algo", "A", BLUE, (100, 160, 255)),
            (pygame.Rect(BUTTON_X2, BUTTON_Y2, BUTTON_WIDTH, BUTTON_HEIGHT), "Solve Fast", "S", CYAN, (100, 220, 255)),
        ]
        now = pygame.time.get_ticks()

        for btn, label, shortcut, btn_color, hover_color in btn_configs:
            btn_key = label.replace(" ", "_").lower()
            is_hovered = btn.collidepoint(mouse_pos)

            # Track hover timing for smooth 100ms transition
            if is_hovered:
                if btn_key not in self.button_hover_times:
                    self.button_hover_times[btn_key] = now
            else:
                self.button_hover_times.pop(btn_key, None)

            # Calculate smooth color transition (100ms duration)
            hover_progress = 0.0
            if btn_key in self.button_hover_times:
                elapsed = now - self.button_hover_times[btn_key]
                hover_progress = min(1.0, elapsed / 100.0)
                hover_progress = ease_in_out(hover_progress)

            # Interpolate color smoothly
            color = tuple(int(btn_color[i] + (hover_color[i] - btn_color[i]) * hover_progress) for i in range(3))

            # Draw button shadow (smooth scaling, larger on hover)
            base_shadow = 3
            max_shadow = 6
            shadow_offset = base_shadow + (max_shadow - base_shadow) * hover_progress
            shadow_color = (60, 60, 60)
            pygame.draw.rect(self.screen, shadow_color,
                           (btn.x + shadow_offset, btn.y + shadow_offset, btn.width, btn.height))

            # Draw button
            pygame.draw.rect(self.screen, color, btn)
            pygame.draw.rect(self.screen, BLACK, btn, 2)

            # Draw label with smooth font size transition
            base_font_size = 19
            max_font_size = 20
            font_size = base_font_size + (max_font_size - base_font_size) * hover_progress
            text = pygame.font.Font(None, int(font_size)).render(label, True, WHITE)
            text_rect = text.get_rect(center=(btn.centerx, btn.centery - 8))
            self.screen.blit(text, text_rect)

            # Draw keyboard shortcut hint below label
            hint_text = pygame.font.Font(None, 14).render(f"({shortcut})", True, (240, 240, 240))
            hint_rect = hint_text.get_rect(center=(btn.centerx, btn.centery + 12))
            self.screen.blit(hint_text, hint_rect)

    def draw_message(self, message, message_color, message_animation_start=0):
        """Draw status message with toast-style background and slide-in animation.

        Args:
            message: Text message to display
            message_color: RGB tuple for text color
            message_animation_start: Time when message started animating
        """
        if message:
            now = pygame.time.get_ticks()
            text = FONT_SMALL.render(message, True, message_color)

            # Calculate slide-in animation (200ms duration)
            if message_animation_start > 0:
                elapsed = now - message_animation_start
                if elapsed < 200:
                    # Slide in from left over 200ms
                    progress = ease_in_out(elapsed / 200.0)
                    x_offset = lerp(-150, 0, progress)  # Slide from -150px to 0
                    opacity_factor = progress
                else:
                    x_offset = 0
                    opacity_factor = 1.0
            else:
                x_offset = 0
                opacity_factor = 1.0

            # Draw background box with better styling
            padding = 10
            bg_x = MARGIN + x_offset
            bg_rect = pygame.Rect(bg_x, MESSAGE_Y, text.get_width() + 2 * padding, text.get_height() + 2 * padding)

            # Apply opacity via surface
            bg_color = (248, 248, 250)
            if opacity_factor < 1.0:
                # Fade background
                faded_bg = tuple(int(c + (255 - c) * (1 - opacity_factor)) for c in bg_color)
            else:
                faded_bg = bg_color

            # Subtle shadow (fades with opacity)
            shadow_rect = bg_rect.copy()
            shadow_rect.x += 2
            shadow_rect.y += 2
            shadow_color = tuple(int(c * opacity_factor + 200 * (1 - opacity_factor)) for c in (60, 60, 60))
            pygame.draw.rect(self.screen, shadow_color, shadow_rect)

            # Main background
            pygame.draw.rect(self.screen, faded_bg, bg_rect)
            border_color = tuple(int(c * opacity_factor + 220 * (1 - opacity_factor)) for c in (180, 180, 200))
            pygame.draw.rect(self.screen, border_color, bg_rect, 2)

            # Draw text with fading
            text_color = tuple(int(c * opacity_factor + 255 * (1 - opacity_factor)) for c in message_color)
            faded_text = FONT_SMALL.render(message, True, text_color)
            self.screen.blit(faded_text, (bg_x + padding, MESSAGE_Y + padding))

    def draw_solver_panel(self, backtrack_count, step_count, current_cell, candidates,
                         solving, solve_paused, show_final_panel, solve_fast, elapsed_time="0s",
                         step_pulse_time=0, backtrack_pulse_time=0):
        """Draw algorithm visualization panel with metrics and animations.

        Args:
            backtrack_count: Number of backtracks
            step_count: Number of steps taken
            current_cell: (row, col) or None
            candidates: List of valid candidates
            solving: True if solver is active
            solve_paused: True if solver is paused
            show_final_panel: True if showing final results
            solve_fast: True if fast solve mode used
            elapsed_time: Formatted elapsed time string (e.g. "1m 23s")
            step_pulse_time: Time when step counter last updated
            backtrack_pulse_time: Time when backtrack counter last updated
        """
        if not solving and not show_final_panel:
            return

        panel_x = MARGIN + GRID_SIZE + PANEL_GAP
        panel_y = GRID_TOP
        padding = 12
        bar_height = 18
        bar_width = PANEL_WIDTH - 2 * padding

        # Panel background and border
        pygame.draw.rect(self.screen, (248, 248, 250), (panel_x, panel_y, PANEL_WIDTH, GRID_SIZE))
        pygame.draw.rect(self.screen, (100, 150, 200), (panel_x, panel_y, PANEL_WIDTH, GRID_SIZE), 2)

        # Title (single line) with better styling
        title_font = pygame.font.Font(None, 26)
        title = title_font.render("Algorithm", True, (25, 55, 135))
        subtitle = pygame.font.Font(None, 18).render("Visualization", True, (100, 130, 180))
        self.screen.blit(title, (panel_x + padding, panel_y + 10))
        self.screen.blit(subtitle, (panel_x + padding, panel_y + 32))

        y_offset = panel_y + 55

        # Current cell info (1,1-based indexing)
        if current_cell and (solving or show_final_panel):
            row, col = current_cell
            display_row = row + 1  # Convert to 1-based
            display_col = col + 1
            cell_label = pygame.font.Font(None, 20).render("Current Cell:", True, (66, 66, 66))
            self.screen.blit(cell_label, (panel_x + padding, y_offset))
            y_offset += 22
            cell_text = pygame.font.Font(None, 32).render(f"({display_row}, {display_col})", True, (25, 55, 135))
            self.screen.blit(cell_text, (panel_x + padding + 10, y_offset))
            y_offset += 40

        # Backtracks metric (with pulse on update)
        back_label = pygame.font.Font(None, 20).render("Backtracks:", True, (66, 66, 66))
        self.screen.blit(back_label, (panel_x + padding, y_offset))

        # Apply pulse scale to backtrack value
        back_scale = self.get_pulse_scale(backtrack_pulse_time, duration=150)
        back_font_size = int(24 * back_scale)
        back_value = pygame.font.Font(None, back_font_size).render(str(backtrack_count), True, ORANGE)
        back_rect = back_value.get_rect(topleft=(panel_x + padding + 115, y_offset + int(3 * (1 - back_scale))))
        self.screen.blit(back_value, back_rect)
        y_offset += 28

        # Backtracks progress bar with glow
        max_backtracks = 50
        backtrack_pct = min(1.0, backtrack_count / max_backtracks)
        draw_progress_bar(self.screen, panel_x + padding, y_offset, bar_width, bar_height,
                         backtrack_pct, ORANGE, (255, 230, 200))

        # Add glow effect on bar during pulse
        glow = self.get_bar_glow(backtrack_pulse_time, duration=100)
        if glow > 0:
            glow_color = tuple(int(c * glow + 255 * (1 - glow)) for c in ORANGE)
            glow_width = int(bar_width * backtrack_pct)
            pygame.draw.rect(self.screen, glow_color, (panel_x + padding, y_offset, glow_width, bar_height), 2)

        y_offset += 32

        # Steps metric (with pulse on update)
        steps_label = pygame.font.Font(None, 20).render("Steps:", True, (66, 66, 66))
        self.screen.blit(steps_label, (panel_x + padding, y_offset))

        # Apply pulse scale to steps value
        step_scale = self.get_pulse_scale(step_pulse_time, duration=150)
        step_font_size = int(24 * step_scale)
        steps_value = pygame.font.Font(None, step_font_size).render(str(step_count), True, GREEN)
        steps_rect = steps_value.get_rect(topleft=(panel_x + padding + 115, y_offset + int(3 * (1 - step_scale))))
        self.screen.blit(steps_value, steps_rect)
        y_offset += 28

        # Steps progress bar with glow
        max_steps = 200
        steps_pct = min(1.0, step_count / max_steps)
        draw_progress_bar(self.screen, panel_x + padding, y_offset, bar_width, bar_height,
                         steps_pct, GREEN, (220, 240, 220))

        # Add glow effect on bar during pulse
        glow = self.get_bar_glow(step_pulse_time, duration=100)
        if glow > 0:
            glow_color = tuple(int(c * glow + 255 * (1 - glow)) for c in GREEN)
            glow_width = int(bar_width * steps_pct)
            pygame.draw.rect(self.screen, glow_color, (panel_x + padding, y_offset, glow_width, bar_height), 2)

        y_offset += 38

        # Candidates section (scrollable content area)
        # Max content area before status/timer section
        max_content_y = panel_y + GRID_SIZE - 120

        if candidates and solving and y_offset < max_content_y:
            cand_label = pygame.font.Font(None, 20).render("Valid Candidates:", True, (66, 66, 66))
            if y_offset + 25 < max_content_y:
                self.screen.blit(cand_label, (panel_x + padding, y_offset))
                y_offset += 25
                candidates_str = " ".join(map(str, sorted(candidates)))
                cand_text = pygame.font.Font(None, 26).render(candidates_str, True, BLUE)
                self.screen.blit(cand_text, (panel_x + padding, y_offset))

        # Status and Timer at FIXED bottom (never move)
        status_y = panel_y + GRID_SIZE - 90
        info_y = panel_y + GRID_SIZE - 60

        # Status indicator (fixed at bottom)
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
        self.screen.blit(status_text, (panel_x + padding, status_y))

        # Timer at fixed bottom (right below status)
        timer_y = status_y + 30
        timer_label = pygame.font.Font(None, 18).render("Time:", True, (66, 66, 66))
        self.screen.blit(timer_label, (panel_x + padding, timer_y))
        timer_value = pygame.font.Font(None, 22).render(elapsed_time, True, BLUE)
        timer_rect = timer_value.get_rect(topleft=(panel_x + padding + 70, timer_y))
        self.screen.blit(timer_value, timer_rect)

        # Info text at very bottom (larger font)
        info_font = pygame.font.Font(None, 18)
        info_y = panel_y + GRID_SIZE - 28

        if show_final_panel:
            info_text = info_font.render("Click any button", True, (100, 100, 100))
        else:
            info_text = info_font.render("SPACE: pause  UP/DOWN: speed  ESC: stop", True, (100, 100, 100))

        self.screen.blit(info_text, (panel_x + padding, info_y))

    def draw_menu_bar(self):
        """Draw menu bar background and text with improved styling."""
        # Gradient-like effect using slightly darker background
        pygame.draw.rect(self.screen, (252, 252, 254), (0, 0, WIDTH, MENU_HEIGHT))

        # Subtle top border for depth
        pygame.draw.line(self.screen, (220, 220, 220), (0, 0), (WIDTH, 0), 1)

        # Bottom border
        pygame.draw.line(self.screen, (180, 180, 180), (0, MENU_HEIGHT - 1), (WIDTH, MENU_HEIGHT - 1), 1)

        # Menu items with better spacing
        file_text = FONT_MENU.render("FILE", True, (50, 50, 50))
        edit_text = FONT_MENU.render("EDIT", True, (50, 50, 50))

        self.screen.blit(file_text, (12, 6))
        self.screen.blit(edit_text, (67, 6))

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
        """Draw FILE dropdown menu with improved styling."""
        menu_items = ['New Puzzle', 'Load Puzzle...', 'Save Puzzle...', 'Exit']
        item_height = 32
        menu_width = 160
        menu_x = 10
        menu_y = MENU_HEIGHT

        # Draw menu background
        total_height = len(menu_items) * item_height
        pygame.draw.rect(self.screen, (252, 252, 254), (menu_x, menu_y, menu_width, total_height))
        pygame.draw.rect(self.screen, (150, 150, 180), (menu_x, menu_y, menu_width, total_height), 2)

        # Draw items
        for i, item in enumerate(menu_items):
            item_y = menu_y + i * item_height
            # Hover highlight with better color
            if menu_hover_index == i:
                pygame.draw.rect(self.screen, (220, 230, 250), (menu_x, item_y, menu_width, item_height))

            # Text with better contrast
            text = FONT_MENU.render(item, True, (50, 50, 50))
            self.screen.blit(text, (menu_x + 12, item_y + 8))

        # Draw New Puzzle submenu if open
        if submenu_open == 'NEW_PUZZLE':
            self._draw_new_puzzle_submenu(menu_x + menu_width, menu_y, submenu_hover_index)

    def _draw_new_puzzle_submenu(self, x, y, submenu_hover_index):
        """Draw New Puzzle submenu with difficulty levels and improved styling.

        Args:
            x, y: Position
            submenu_hover_index: Which submenu item is hovered
        """
        submenu_items = ['Easy (E)', 'Medium (M)', 'Hard (H)']
        item_height = 32
        submenu_width = 160

        # Draw submenu background
        total_height = len(submenu_items) * item_height
        pygame.draw.rect(self.screen, (252, 252, 254), (x, y, submenu_width, total_height))
        pygame.draw.rect(self.screen, (150, 150, 180), (x, y, submenu_width, total_height), 2)

        # Draw items
        for i, item in enumerate(submenu_items):
            item_y = y + i * item_height
            # Hover highlight with better color
            if submenu_hover_index == i:
                pygame.draw.rect(self.screen, (220, 230, 250), (x, item_y, submenu_width, item_height))

            # Text with better contrast
            text = FONT_MENU.render(item, True, (50, 50, 50))
            self.screen.blit(text, (x + 12, item_y + 8))

    def _draw_edit_menu(self, menu_hover_index):
        """Draw Edit dropdown menu with improved styling."""
        menu_items = ['Clear Grid']
        item_height = 32
        menu_width = 160
        menu_x = 65
        menu_y = MENU_HEIGHT

        # Draw menu background
        total_height = len(menu_items) * item_height
        pygame.draw.rect(self.screen, (252, 252, 254), (menu_x, menu_y, menu_width, total_height))
        pygame.draw.rect(self.screen, (150, 150, 180), (menu_x, menu_y, menu_width, total_height), 2)

        # Draw items
        for i, item in enumerate(menu_items):
            item_y = menu_y + i * item_height
            # Hover highlight with better color
            if menu_hover_index == i:
                pygame.draw.rect(self.screen, (220, 230, 250), (menu_x, item_y, menu_width, item_height))

            # Text with better contrast
            text = FONT_MENU.render(item, True, (50, 50, 50))
            self.screen.blit(text, (menu_x + 12, item_y + 8))

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

    def get_bar_glow(self, pulse_time, duration=100):
        """Get glow effect for progress bars during stat updates.

        Args:
            pulse_time: Time when pulse started
            duration: Animation duration

        Returns: Glow intensity [0, 1]
        """
        now = pygame.time.get_ticks()
        if pulse_time == 0:
            return 0.0
        elapsed = now - pulse_time
        if elapsed > duration:
            return 0.0
        progress = ease_in_out(elapsed / duration)
        # Glow peaks at 0.5, creates subtle highlight
        return max(0, 1.0 - abs(2.0 * progress - 1.0))

    def trigger_cell_animation(self, row, col, duration=200):
        """Trigger a cell highlight animation.

        Args:
            row, col: Cell position
            duration: Animation duration in milliseconds
        """
        self.cell_animations[(row, col)] = {
            'start_time': pygame.time.get_ticks(),
            'duration': duration
        }

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
