import pygame
import sys
from collections import deque

# Initialize Pygame
pygame.init()

# Constants
WIDTH = 900
HEIGHT = 700
GRID_SIZE = 540
CELL_SIZE = GRID_SIZE // 9
BUTTON_HEIGHT = 50
BUTTON_WIDTH = 140
MARGIN = 30
PANEL_WIDTH = 260  # Right panel for algorithm visualization

# Layout — derived from constants so everything stays in sync
GRID_BOTTOM = MARGIN + GRID_SIZE          # 570
MESSAGE_Y   = GRID_BOTTOM + 14           # 584  — message zone top
BUTTON_Y    = GRID_BOTTOM + 55           # 625  — button row top (row 1)
BUTTON_Y2   = GRID_BOTTOM + 95           # 655  — button row 2
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

# Fonts
FONT_LARGE = pygame.font.Font(None, 40)
FONT_MEDIUM = pygame.font.Font(None, 32)
FONT_SMALL = pygame.font.Font(None, 24)


class SudokuGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Sudoku Game - Educational Solver")
        self.clock = pygame.time.Clock()

        # Game state
        self.grid = [[0 for _ in range(9)] for _ in range(9)]
        self.selected_cell = None
        self.error_cells = set()
        self.message = ""
        self.message_color = BLACK

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
        
    def draw_grid(self):
        """Draw the Sudoku grid"""
        # Draw cells
        for i in range(9):
            for j in range(9):
                x = MARGIN + j * CELL_SIZE
                y = MARGIN + i * CELL_SIZE

                # Highlight current solving cell
                if self.solving and self.current_cell == (i, j):
                    pygame.draw.rect(self.screen, (255, 255, 150), (x, y, CELL_SIZE, CELL_SIZE))  # Yellow
                # Highlight selected cell
                elif self.selected_cell == (i, j):
                    pygame.draw.rect(self.screen, LIGHT_BLUE, (x, y, CELL_SIZE, CELL_SIZE))
                # Highlight error cells
                elif (i, j) in self.error_cells:
                    pygame.draw.rect(self.screen, LIGHT_RED, (x, y, CELL_SIZE, CELL_SIZE))
                else:
                    pygame.draw.rect(self.screen, WHITE, (x, y, CELL_SIZE, CELL_SIZE))

                # Draw cell border
                pygame.draw.rect(self.screen, BLACK, (x, y, CELL_SIZE, CELL_SIZE), 1)

                # Draw number if present
                if self.grid[i][j] != 0:
                    text = FONT_MEDIUM.render(str(self.grid[i][j]), True, BLACK)
                    text_rect = text.get_rect(center=(x + CELL_SIZE // 2, y + CELL_SIZE // 2))
                    self.screen.blit(text, text_rect)
        
        # Draw thick lines for 3x3 boxes
        for i in range(10):
            thickness = 3 if i % 3 == 0 else 1
            # Horizontal lines
            pygame.draw.line(self.screen, BLACK,
                           (MARGIN, MARGIN + i * CELL_SIZE),
                           (MARGIN + GRID_SIZE, MARGIN + i * CELL_SIZE),
                           thickness)
            # Vertical lines
            pygame.draw.line(self.screen, BLACK,
                           (MARGIN + i * CELL_SIZE, MARGIN),
                           (MARGIN + i * CELL_SIZE, MARGIN + GRID_SIZE),
                           thickness)
    
    def draw_buttons(self):
        """Draw the control buttons in 2x2 grid"""
        # Finalize button
        pygame.draw.rect(self.screen, GREEN, self.finalize_button)
        pygame.draw.rect(self.screen, BLACK, self.finalize_button, 2)
        text = pygame.font.Font(None, 20).render("Finalize", True, WHITE)
        text_rect = text.get_rect(center=self.finalize_button.center)
        self.screen.blit(text, text_rect)

        # Clear button
        pygame.draw.rect(self.screen, RED, self.clear_button)
        pygame.draw.rect(self.screen, BLACK, self.clear_button, 2)
        text = pygame.font.Font(None, 20).render("Clear", True, WHITE)
        text_rect = text.get_rect(center=self.clear_button.center)
        self.screen.blit(text, text_rect)

        # Solve Algo button (animated)
        pygame.draw.rect(self.screen, BLUE, self.solve_algo_button)
        pygame.draw.rect(self.screen, BLACK, self.solve_algo_button, 2)
        text = pygame.font.Font(None, 20).render("Solve Algo", True, WHITE)
        text_rect = text.get_rect(center=self.solve_algo_button.center)
        self.screen.blit(text, text_rect)

        # Solve Fast button
        fast_color = (100, 180, 255)  # Lighter blue
        pygame.draw.rect(self.screen, fast_color, self.solve_fast_button)
        pygame.draw.rect(self.screen, BLACK, self.solve_fast_button, 2)
        text = pygame.font.Font(None, 20).render("Solve Fast", True, WHITE)
        text_rect = text.get_rect(center=self.solve_fast_button.center)
        self.screen.blit(text, text_rect)
    
    def draw_message(self):
        """Draw status message — left-aligned, between grid and buttons"""
        if self.message:
            text = FONT_SMALL.render(self.message, True, self.message_color)
            self.screen.blit(text, (MARGIN, MESSAGE_Y))

    def draw_solver_panel(self):
        """Draw algorithm visualization panel on the right"""
        if not self.solving and not self.show_final_panel:
            return

        panel_x = MARGIN + GRID_SIZE + 20
        panel_y = MARGIN

        # Panel background
        pygame.draw.rect(self.screen, (240, 240, 240),
                        (panel_x, panel_y, PANEL_WIDTH, GRID_SIZE))
        pygame.draw.rect(self.screen, DARK_GRAY,
                        (panel_x, panel_y, PANEL_WIDTH, GRID_SIZE), 2)

        # Title
        title = FONT_SMALL.render("Algorithm State", True, BLACK)
        self.screen.blit(title, (panel_x + 10, panel_y + 10))

        y_offset = panel_y + 45

        # Current cell info
        if self.current_cell:
            row, col = self.current_cell
            cell_text = FONT_SMALL.render(f"Cell: ({row}, {col})", True, BLACK)
            self.screen.blit(cell_text, (panel_x + 10, y_offset))
            y_offset += 35

        # Step count
        step_text = FONT_SMALL.render(f"Steps: {self.step_count}", True, BLACK)
        self.screen.blit(step_text, (panel_x + 10, y_offset))
        y_offset += 30

        # Backtrack count
        back_text = FONT_SMALL.render(f"Backtracks: {self.backtrack_count}", True, RED)
        self.screen.blit(back_text, (panel_x + 10, y_offset))
        y_offset += 35

        # Candidates
        candidates_label = FONT_SMALL.render("Valid candidates:", True, BLACK)
        self.screen.blit(candidates_label, (panel_x + 10, y_offset))
        y_offset += 25

        candidates_str = " ".join(map(str, sorted(self.candidates))) if self.candidates else "None"
        cand_text = pygame.font.Font(None, 20).render(candidates_str, True, BLUE)
        self.screen.blit(cand_text, (panel_x + 10, y_offset))
        y_offset += 30

        # Status
        if self.show_final_panel:
            status = "COMPLETED"
            status_color = GREEN
        elif self.solve_fast:
            status = "SOLVED (FAST)"
            status_color = GREEN
        else:
            status = "PAUSED" if self.solve_paused else "SOLVING..."
            status_color = DARK_GRAY if self.solve_paused else GREEN

        status_text = FONT_SMALL.render(status, True, status_color)
        self.screen.blit(status_text, (panel_x + 10, y_offset))

        # Info text at bottom
        info_font = pygame.font.Font(None, 16)
        if self.show_final_panel:
            info1 = info_font.render("Click button", True, DARK_GRAY)
            info2 = info_font.render("to close panel", True, DARK_GRAY)
            self.screen.blit(info1, (panel_x + 5, panel_y + GRID_SIZE - 75))
            self.screen.blit(info2, (panel_x + 5, panel_y + GRID_SIZE - 55))
        elif self.solving and not self.solve_fast:
            info1 = info_font.render("SPACE: pause/resume", True, DARK_GRAY)
            info2 = info_font.render("UP/DOWN: speed", True, DARK_GRAY)
            info3 = info_font.render("ESC: stop solver", True, DARK_GRAY)
            self.screen.blit(info1, (panel_x + 5, panel_y + GRID_SIZE - 75))
            self.screen.blit(info2, (panel_x + 5, panel_y + GRID_SIZE - 55))
            self.screen.blit(info3, (panel_x + 5, panel_y + GRID_SIZE - 35))
    
    def handle_click(self, pos):
        """Handle mouse click events"""
        x, y = pos
        
        # Check if click is on grid
        if MARGIN <= x <= MARGIN + GRID_SIZE and MARGIN <= y <= MARGIN + GRID_SIZE:
            col = (x - MARGIN) // CELL_SIZE
            row = (y - MARGIN) // CELL_SIZE
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
        self.selected_cell = None
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
                yield  # Show filled cell
                if (yield from backtrack()):
                    return True
                self.grid[row][col] = 0  # Backtrack
                self.backtrack_count += 1
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
            self.screen.fill(WHITE)
            self.draw_grid()
            self.draw_buttons()
            self.draw_message()
            if self.solving or self.show_final_panel:
                self.draw_solver_panel()

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = SudokuGame()
    game.run()

# Made with Bob
