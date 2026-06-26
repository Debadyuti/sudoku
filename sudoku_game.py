import pygame
import sys

# Initialize Pygame
pygame.init()

# Constants
WIDTH = 600
HEIGHT = 700
GRID_SIZE = 540
CELL_SIZE = GRID_SIZE // 9
BUTTON_HEIGHT = 50
BUTTON_WIDTH = 160
MARGIN = 30

# Layout — derived from constants so everything stays in sync
GRID_BOTTOM = MARGIN + GRID_SIZE          # 570
MESSAGE_Y   = GRID_BOTTOM + 14           # 584  — message zone top
BUTTON_Y    = GRID_BOTTOM + 55           # 625  — button row top
# Three buttons equally spaced inside [MARGIN .. WIDTH-MARGIN] (540 px usable)
# gap = (540 - 3*BUTTON_WIDTH) / 4  →  (540 - 480) / 4 = 15 px
_BTN_GAP    = (WIDTH - 2 * MARGIN - 3 * BUTTON_WIDTH) // 4  # 15
BUTTON_X = [
    MARGIN + _BTN_GAP,
    MARGIN + _BTN_GAP * 2 + BUTTON_WIDTH,
    MARGIN + _BTN_GAP * 3 + BUTTON_WIDTH * 2,
]

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
        pygame.display.set_caption("Sudoku Game")
        self.clock = pygame.time.Clock()
        
        # Game state
        self.grid = [[0 for _ in range(9)] for _ in range(9)]
        self.selected_cell = None
        self.error_cells = set()
        self.message = ""
        self.message_color = BLACK
        
        # Button positions — equally spaced, computed from layout constants
        self.finalize_button = pygame.Rect(BUTTON_X[0], BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT)
        self.clear_button    = pygame.Rect(BUTTON_X[1], BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT)
        self.solve_button    = pygame.Rect(BUTTON_X[2], BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT)
        
    def draw_grid(self):
        """Draw the Sudoku grid"""
        # Draw cells
        for i in range(9):
            for j in range(9):
                x = MARGIN + j * CELL_SIZE
                y = MARGIN + i * CELL_SIZE
                
                # Highlight selected cell
                if self.selected_cell == (i, j):
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
        """Draw the control buttons"""
        # Finalize button
        pygame.draw.rect(self.screen, GREEN, self.finalize_button)
        pygame.draw.rect(self.screen, BLACK, self.finalize_button, 2)
        text = FONT_SMALL.render("Finalize", True, WHITE)
        text_rect = text.get_rect(center=self.finalize_button.center)
        self.screen.blit(text, text_rect)
        
        # Clear button
        pygame.draw.rect(self.screen, RED, self.clear_button)
        pygame.draw.rect(self.screen, BLACK, self.clear_button, 2)
        text = FONT_SMALL.render("Clear", True, WHITE)
        text_rect = text.get_rect(center=self.clear_button.center)
        self.screen.blit(text, text_rect)
        
        # Solve button
        pygame.draw.rect(self.screen, BLUE, self.solve_button)
        pygame.draw.rect(self.screen, BLACK, self.solve_button, 2)
        text = FONT_SMALL.render("Solve", True, WHITE)
        text_rect = text.get_rect(center=self.solve_button.center)
        self.screen.blit(text, text_rect)
    
    def draw_message(self):
        """Draw status message — left-aligned, between grid and buttons"""
        if self.message:
            text = FONT_SMALL.render(self.message, True, self.message_color)
            self.screen.blit(text, (MARGIN, MESSAGE_Y))
    
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
        elif self.solve_button.collidepoint(pos):
            self.solve_puzzle()
    
    def handle_key(self, key, mod=0):
        """Handle keyboard input"""
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
    
    def solve_puzzle(self):
        """Solve the puzzle using backtracking algorithm"""
        self.message = "Solving..."
        self.message_color = BLUE
        pygame.display.flip()
        
        if self.solve_backtrack():
            self.message = "Puzzle solved!"
            self.message_color = GREEN
            self.error_cells.clear()
        else:
            self.message = "No solution exists!"
            self.message_color = RED
    
    def solve_backtrack(self):
        """Backtracking algorithm to solve Sudoku"""
        # Find empty cell
        empty = self.find_empty_cell()
        if not empty:
            return True  # Puzzle solved
        
        row, col = empty
        
        # Try numbers 1-9
        for num in range(1, 10):
            if self.is_valid_placement(row, col, num):
                self.grid[row][col] = num
                
                if self.solve_backtrack():
                    return True
                
                # Backtrack
                self.grid[row][col] = 0
        
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
            
            # Draw everything
            self.screen.fill(WHITE)
            self.draw_grid()
            self.draw_buttons()
            self.draw_message()
            
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = SudokuGame()
    game.run()

# Made with Bob
