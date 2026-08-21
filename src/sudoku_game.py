import pygame
import sys
import signal
from collections import deque

# Import all constants from constants module
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
        lerp, ease_in_out, draw_progress_bar, draw_rounded_rect
    )
    from .solver import SudokuSolver, generate_puzzle, generate_complete_grid, save_puzzle, load_puzzle
    from .ui import UIRenderer
    from .menu import MenuSystem
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
        lerp, ease_in_out, draw_progress_bar, draw_rounded_rect
    )
    from solver import SudokuSolver, generate_puzzle, generate_complete_grid, save_puzzle, load_puzzle
    from ui import UIRenderer
    from menu import MenuSystem

class SudokuGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Sudoku Game - Educational Solver")
        self.clock = pygame.time.Clock()

        # UI renderer
        self.ui = UIRenderer(self.screen)

        # Menu system
        self.menu = MenuSystem()

        # Game state
        self.grid = [[0 for _ in range(9)] for _ in range(9)]
        self.solution = [[0 for _ in range(9)] for _ in range(9)]
        self.selected_cell = (0, 0)
        self.error_cells = set()
        self.frozen_cells = set()  # Immutable initial cells
        self.puzzle_difficulty = "medium"  # Track difficulty: easy/medium/hard
        self.message = "Ready to play - Enter numbers in selected cell"
        self.message_color = BLUE

        # Button positions
        self.finalize_button = pygame.Rect(BUTTON_X1, BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT)
        self.clear_button = pygame.Rect(BUTTON_X2, BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT)
        self.solve_algo_button = pygame.Rect(BUTTON_X1, BUTTON_Y2, BUTTON_WIDTH, BUTTON_HEIGHT)
        self.solve_fast_button = pygame.Rect(BUTTON_X2, BUTTON_Y2, BUTTON_WIDTH, BUTTON_HEIGHT)

        # Solver state
        self.solving = False
        self.solve_paused = False
        self.solve_fast = False
        self.current_cell = None
        self.candidates = []
        self.step_count = 0
        self.backtrack_count = 0
        self.step_time = 0
        self.step_delay = 300
        self.show_final_panel = False
        self.waiting_for_difficulty = False

        # Timer state (wall-clock time for solving)
        self.solver_start_time = None  # milliseconds when solving started
        self.solver_pause_time = None  # accumulated pause time
        self.solver_total_pause = 0    # total pause accumulation
        self.solver_final_time = None  # frozen time when solve completes (for display)

        # Input state
        self.mouse_pos = (0, 0)
        self.last_step_count = 0
        self.last_backtrack_count = 0
        self.step_pulse_time = 0
        self.backtrack_pulse_time = 0

    def _process_menu_action(self, action):
        """Process menu action returned by MenuSystem.handle_click()"""
        if action is True:  # Menu item clicked, menu state updated by MenuSystem
            return
        if action is False:  # Menu not involved
            return
        if not isinstance(action, tuple):
            return

        action_type, item_index = action
        difficulties = ['easy', 'medium', 'hard']

        if action_type == 'new_puzzle':
            # Generate puzzle for given difficulty
            difficulty = difficulties[item_index] if item_index < 3 else 'medium'
            puzzle, solution, msg, color = MenuSystem.generate_puzzle(difficulty)
            if puzzle:
                self.grid = puzzle
                self.solution = solution
                self.puzzle_difficulty = difficulty  # Track original difficulty
                self.error_cells.clear()
                self.selected_cell = (0, 0)
                self.solving = False
                self.show_final_panel = False
                # Mark all non-empty cells as frozen (initial puzzle state)
                self.frozen_cells = set((i, j) for i in range(9) for j in range(9) if puzzle[i][j] != 0)
                self.message = msg
                self.message_color = color
            else:
                self.message = msg
                self.message_color = color
            self.menu.close_menu()

        elif action_type == 'file_menu':
            if item_index == 1:  # Load Puzzle
                puzzle, solution, difficulty, clues, frozen_cells, msg, color = MenuSystem.load_puzzle_file()
                if puzzle:
                    self.grid = puzzle
                    self.solution = solution or puzzle
                    self.puzzle_difficulty = difficulty  # Use loaded difficulty
                    self.frozen_cells = frozen_cells if frozen_cells else set()
                    self.show_final_panel = False
                    self.solving = False
                    self.error_cells.clear()
                    self.message = msg
                    self.message_color = color
                else:
                    self.message = msg
                    self.message_color = color
            elif item_index == 2:  # Save Puzzle
                msg, color = MenuSystem.save_puzzle_file(self.grid, self.solution, self.frozen_cells, self.puzzle_difficulty)
                self.message = msg
                self.message_color = color
            elif item_index == 3:  # Exit
                return False  # Signal to quit
            self.menu.close_menu()

        elif action_type == 'edit_menu':
            if item_index == 0:  # Clear Grid
                self.clear_grid()
            self.menu.close_menu()

    def handle_click(self, pos):
        """Handle mouse click events"""
        x, y = pos

        # Check menu bar first
        menu_result = self.menu.handle_click(pos)
        if menu_result is not False:
            action = self._process_menu_action(menu_result)
            if action is False:
                return False  # Exit game
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
        # --- Button shortcuts (F=Finalize, C=Clear, A=Algo, S=SolveFast) ---
        if key == pygame.K_f:  # Finalize
            self.finalize_entry()
            return
        elif key == pygame.K_c:  # Clear
            if not (mod & pygame.KMOD_CTRL):  # Not Ctrl+C
                self.clear_grid()
                return
        elif key == pygame.K_a:  # Solve Algo
            self.solve_puzzle(animated=True)
            return
        elif key == pygame.K_s:  # Solve Fast
            self.solve_puzzle(animated=False)
            return

        # --- Copy stats with Ctrl+C ---
        if (mod & pygame.KMOD_CTRL) and key == pygame.K_c:
            if self.solving or self.show_final_panel:
                stats = self._get_solver_stats()
                try:
                    import subprocess
                    # Copy to clipboard (cross-platform)
                    process = subprocess.Popen(['clip'], stdin=subprocess.PIPE, shell=True)
                    process.communicate(stats.encode('utf-8'))
                    self.message = "Stats copied to clipboard!"
                    self.message_color = GREEN
                except Exception:
                    # Fallback if clipboard not available
                    self.message = f"Stats: {stats[:50]}..."
                    self.message_color = BLUE
            return

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
            now = pygame.time.get_ticks()
            if self.solve_paused:
                # Record when pause started
                self.solver_pause_time = now
                self.message = "Solver paused (SPACE to resume)"
                self.message_color = DARK_GRAY
            else:
                # Add pause duration to total pause time
                if self.solver_pause_time is not None:
                    self.solver_total_pause += now - self.solver_pause_time
                    self.solver_pause_time = None
                self.message = "Solving... (Press SPACE to pause, ESC to stop)"
                self.message_color = BLUE
            return

        if key == pygame.K_ESCAPE and self.solving:
            self.solving = False
            self.solver_final_time = self.get_solver_elapsed_time()  # Freeze timer on stop
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
    
    
    def finalize_puzzle(self):
        """Validate the puzzle — check Sudoku rules first, then completeness"""
        solver = SudokuSolver(self.grid)
        errors = solver.find_errors()

        if errors:
            self.error_cells = errors
            self.message = f"Found {len(errors)} conflict(s)!"
            self.message_color = RED
        elif not solver.is_complete():
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
        self.frozen_cells.clear()
        self.selected_cell = (0, 0)  # Auto-select top-left
        self.error_cells.clear()
        self.message = "Grid cleared!"
        self.message_color = BLUE
        self.show_final_panel = False
        self.solver_start_time = None
        self.solver_final_time = None
    
    def solve_puzzle(self, animated=True):
        """Start solving: animated step-by-step or fast"""
        # Check if puzzle is already complete
        solver = SudokuSolver(self.grid)
        if solver.is_complete():
            self.message = "Puzzle is already complete!"
            self.message_color = BLUE
            self.show_final_panel = False
            return

        self.solving = True
        self.solve_fast = not animated
        self.solve_paused = False
        self.step_count = 0
        self.backtrack_count = 0
        self.current_cell = None
        self.candidates = []
        self.step_time = pygame.time.get_ticks()
        self.show_final_panel = False

        # Freeze user-entered cells (non-empty cells at solve time)
        self.frozen_cells = set((i, j) for i in range(9) for j in range(9) if self.grid[i][j] != 0)

        # Initialize timer
        self.solver_start_time = pygame.time.get_ticks()
        self.solver_pause_time = None
        self.solver_total_pause = 0
        self.solver_final_time = None  # Reset frozen time for new solve

        if animated:
            self.solver_gen = self._solve_with_steps()
            self.message = "Solving... (Press SPACE to pause, ESC to stop)"
        else:
            # Fast solve: run to completion immediately
            self.solve_fast_complete()

    def get_solver_elapsed_time(self):
        """Get elapsed time since solver started (excluding pauses).

        Returns: elapsed milliseconds (int)
        """
        # If solve is complete, return frozen final time
        if self.solver_final_time is not None:
            return self.solver_final_time

        if self.solver_start_time is None:
            return 0

        now = pygame.time.get_ticks()
        # If currently paused, don't include time since pause started
        if self.solve_paused and self.solver_pause_time is not None:
            elapsed = (self.solver_pause_time - self.solver_start_time) - self.solver_total_pause
        else:
            elapsed = (now - self.solver_start_time) - self.solver_total_pause
        return max(0, elapsed)

    def format_solver_time(self, milliseconds):
        """Format elapsed time as seconds, min:sec, or hr:min:sec.

        Args:
            milliseconds: elapsed time in milliseconds

        Returns: formatted time string
        """
        seconds = milliseconds // 1000
        minutes = seconds // 60
        hours = minutes // 60

        if hours > 0:
            remaining_minutes = minutes % 60
            remaining_seconds = seconds % 60
            return f"{hours}h {remaining_minutes}m {remaining_seconds}s"
        elif minutes > 0:
            remaining_seconds = seconds % 60
            return f"{minutes}m {remaining_seconds}s"
        else:
            return f"{seconds}s"

    def _get_solver_stats(self):
        """Get formatted solver statistics for copying.

        Returns: formatted string with all solver stats
        """
        elapsed_ms = self.get_solver_elapsed_time()
        elapsed_str = self.format_solver_time(elapsed_ms)
        stats = f"Steps: {self.step_count}\nBacktracks: {self.backtrack_count}\nTime: {elapsed_str}"
        if self.current_cell:
            row, col = self.current_cell
            stats += f"\nCurrent Cell: ({row+1}, {col+1})"
        if self.candidates:
            stats += f"\nCandidates: {' '.join(map(str, sorted(self.candidates)))}"
        return stats

    def solve_fast_complete(self):
        """Solve instantly without animation, tracking steps/backtracks"""
        # Use _solve_with_steps but consume all yields without animation to track metrics
        gen = self._solve_with_steps()
        try:
            while True:
                next(gen)
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
        self.error_cells.clear()

        # Freeze timer at final elapsed time (prevent further updates)
        if self.solver_start_time is not None:
            self.solver_final_time = self.get_solver_elapsed_time()

    def _solve_with_steps(self):
        """Generator that yields after each solve step for animation"""
        solver = SudokuSolver(self.grid)

        def backtrack_with_ui():
            # Find empty cell
            empty = solver.find_empty_cell()
            if not empty:
                return True

            row, col = empty
            self.current_cell = (row, col)
            self.candidates = solver.get_candidates(row, col)
            self.step_count += 1
            yield  # Pause here to display this step

            # Try numbers 1-9
            for num in self.candidates:
                solver.grid[row][col] = num
                self.grid = solver.grid  # Keep game grid in sync
                self.ui.trigger_cell_animation(row, col, duration=150)
                yield  # Show filled cell
                if (yield from backtrack_with_ui()):
                    return True
                solver.grid[row][col] = 0  # Backtrack
                self.grid = solver.grid  # Keep game grid in sync
                self.backtrack_count += 1
                self.ui.trigger_cell_animation(row, col, duration=100)
                yield  # Show backtrack

            return False

        result = yield from backtrack_with_ui()
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

    def run(self):
        """Main game loop"""
        running = True

        def signal_handler(sig, frame):
            """Handle Ctrl+C cleanly"""
            nonlocal running
            running = False

        # Register Ctrl+C handler for clean shutdown
        signal.signal(signal.SIGINT, signal_handler)

        try:
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
                self.screen.fill((250, 250, 250))
                self.ui.draw_menu_bar()
                self.ui.draw_grid(self.grid, self.selected_cell, self.current_cell, self.error_cells,
                                self.solving, self.frozen_cells)
                self.ui.draw_buttons(self.mouse_pos)
                self.ui.draw_message(self.message, self.message_color)
                if self.solving or self.show_final_panel:
                    elapsed_ms = self.get_solver_elapsed_time()
                    elapsed_str = self.format_solver_time(elapsed_ms)
                    self.ui.draw_solver_panel(self.backtrack_count, self.step_count, self.current_cell,
                                            self.candidates, self.solving, self.solve_paused,
                                            self.show_final_panel, self.solve_fast, elapsed_str)

                # Update and draw menu dropdowns
                self.menu.update_hover(self.mouse_pos)
                self.ui.draw_menu_dropdowns(self.menu.menu_open, self.menu.menu_hover_index,
                                           self.menu.submenu_hover_index, self.menu.submenu_open)

                pygame.display.flip()
                self.clock.tick(60)
        except KeyboardInterrupt:
            pass
        finally:
            pygame.quit()
            sys.exit()


if __name__ == "__main__":
    game = SudokuGame()
    game.run()

# Made with Bob
