# Sudoku Game Modularization Plan

## Current State
- **File**: `src/sudoku_game.py`
- **Lines**: 1,169
- **Content**: Game loop, UI drawing, solver algorithm, menu logic, file I/O — all mixed

## Target: 4-Module Architecture

```
src/
├── sudoku_game.py       (Main game class & event loop) ~150 lines
├── ui.py                (All drawing methods)          ~350 lines
├── solver.py            (Algorithm logic)              ~150 lines
├── menu.py              (Menu system & file I/O)       ~250 lines
└── constants.py         (All constants & colors)       ~80 lines
```

---

## Module Breakdown

### 1. **`constants.py`** (New - Extract)
**Purpose**: Centralize all constants, colors, fonts  
**Lines**: ~80

**Contains**:
- Window dimensions (WIDTH, HEIGHT, MARGIN, etc.)
- Layout constants (GRID_TOP, BUTTON_Y, PANEL_WIDTH, etc.)
- Color palette (WHITE, BLACK, LIGHT_BLUE, MENU_BG, etc.)
- Font definitions (FONT_LARGE, FONT_SMALL, etc.)
- Animation utilities (lerp, ease_in_out, draw_progress_bar, draw_rounded_rect)

**Why**: Single source of truth for all visual constants. Easy to theme/adjust globally.

**Import by**: All other modules

```python
# constants.py
import pygame

pygame.init()

# Window & Layout
WIDTH = 900
HEIGHT = 800
GRID_SIZE = 540
# ... (all constants)

# Helper functions
def lerp(a, b, t):
    ...

def ease_in_out(t):
    ...
```

---

### 2. **`solver.py`** (Extract)
**Purpose**: Pure algorithm logic (no Pygame, no drawing)  
**Lines**: ~150

**Contains**:
- `generate_complete_grid()` — Generate valid grid
- `SudokuSolver` class:
  - `is_valid_placement(row, col, num)` — Validation
  - `get_candidates(row, col)` — Find valid numbers
  - `find_empty_cell()` — Find next cell to fill
  - `solve_backtrack()` — Core backtracking algorithm
  - `solve_fast_complete()` — Instant solve with stats
  - `find_errors()` — Validate user input
  - `is_complete()` — Check if puzzle solved

**Why**: Testable in isolation (no Pygame dependency). Can be imported by other projects.

**Import by**: sudoku_game.py

```python
# solver.py
class SudokuSolver:
    def __init__(self, grid):
        self.grid = grid
    
    def is_valid_placement(self, row, col, num):
        ...
    
    def get_candidates(self, row, col):
        ...
    
    def solve_backtrack(self):
        ...
```

---

### 3. **`ui.py`** (Extract)
**Purpose**: All Pygame drawing and visual rendering  
**Lines**: ~350

**Contains**:
- `UIRenderer` class:
  - `draw_grid(grid, selected_cell, errors, solving_state)` — Grid rendering
  - `draw_buttons()` — Button panel (Finalize, Clear, Solve Algo, Solve Fast)
  - `draw_message(message, color)` — Toast message display
  - `draw_solver_panel(steps, backtracks, candidates, current_cell)` — Right-side panel
  - `get_cell_color(row, col, base_color, animations)` — Color interpolation
  - `draw_progress_bar()` — Reusable progress bar
  - Helper methods for button hover states, animations

**Why**: All visual logic isolated. Easier to polish UI without touching game logic. Can swap renderer implementations later if needed.

**Import by**: sudoku_game.py, menu.py

**Constructor**:
```python
# ui.py
class UIRenderer:
    def __init__(self, screen):
        self.screen = screen
        self.button_hover_state = {}
        self.animations = {}  # Track ongoing animations
    
    def draw_grid(self, grid, selected_cell, errors, solving_state):
        ...
    
    def draw_buttons(self):
        ...
    
    def draw_solver_panel(self, stats):
        ...
```

---

### 4. **`menu.py`** (Extract & New)
**Purpose**: Menu bar, file I/O, puzzle generation  
**Lines**: ~250

**Contains**:
- `MenuSystem` class:
  - `draw_menu_bar()` — Menu rendering
  - `draw_menu_dropdowns()` — Dropdown menus
  - `handle_menu_click(mouse_pos)` — Menu interaction
  - `_draw_file_menu()` — File menu items
  - `_draw_edit_menu()` — Edit menu items
  - `_draw_new_puzzle_submenu(x, y)` — Difficulty submenu
- `PuzzleGenerator` class:
  - `generate_new_puzzle(difficulty)` — Create random puzzle
  - Difficulty settings (clue counts by level)
- `PuzzleIO` class:
  - `save_puzzle_dialog()` — Save to file
  - `load_puzzle_dialog()` — Load from file
  - `save_to_json(puzzle, filepath)` — JSON export
  - `load_from_json(filepath)` — JSON import

**Why**: Menu system can grow independently. Puzzle generation is self-contained. File I/O logic separated from game state.

**Import by**: sudoku_game.py

```python
# menu.py
class MenuSystem:
    def __init__(self, screen):
        self.screen = screen
        self.open_menu = None
        self.menu_hover_index = -1
    
    def draw_menu_bar(self):
        ...
    
    def handle_menu_click(self, mouse_pos):
        ...

class PuzzleGenerator:
    @staticmethod
    def generate_new_puzzle(difficulty):
        ...

class PuzzleIO:
    @staticmethod
    def save_puzzle(puzzle, filepath):
        ...
```

---

### 5. **`sudoku_game.py`** (Refactored - Core)
**Purpose**: Game loop, state management, event handling, orchestration  
**Lines**: ~150

**Contains**:
- `SudokuGame` class:
  - `__init__()` — Initialize game state (grid, selected_cell, message, etc.)
  - `run()` — Main event loop (unchanged structure)
  - `handle_click(pos)` — Route clicks to grid/buttons/menu
  - `handle_key(key, mod)` — Route keyboard input
  - `render()` — Call all drawing methods
  - `update()` — Update animations/state
  - Helper: `finalize_puzzle()`, `clear_grid()`, `solve_puzzle()` (now delegate to solver)

**Why**: High-level orchestration only. Imports and delegates to specialized modules. Easy to understand game flow without implementation details.

**Import**: constants, solver, ui, menu

```python
# sudoku_game.py
from constants import *
from solver import SudokuSolver
from ui import UIRenderer
from menu import MenuSystem, PuzzleGenerator

class SudokuGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.solver = SudokuSolver(self.grid)
        self.ui = UIRenderer(self.screen)
        self.menu = MenuSystem(self.screen)
        # Game state...
    
    def run(self):
        # Main loop: handle events → update → render
        ...
    
    def handle_click(self, pos):
        # Route to menu, grid, or buttons
        ...
    
    def render(self):
        # Call ui.draw_grid(), ui.draw_buttons(), menu.draw_menu_bar(), etc.
        ...
```

---

## Import Graph

```
constants.py
    ↑
    ├── ui.py
    ├── solver.py
    ├── menu.py
    │    └── (imports solver for puzzle generation)
    └── sudoku_game.py
         ├── (imports all of above)
         └── (orchestrates them)

run.py
    └── sudoku_game.py
```

---

## Data Flow

### Example: User clicks "Solve Algo" button
```
sudoku_game.run()
    → pygame event: MOUSEBUTTONDOWN at (x, y)
    → handle_click((x, y))
    → route to ui.find_button_at_pos((x, y))
    → button found: "Solve Algo"
    → game_state.solving = True
    → spawn solver animation:
        self.solver.solve_backtrack()
        → yields steps with cell positions
        → ui.draw_solver_panel() updates
        → ui.trigger_cell_animation()
    → render() each frame until complete
```

### Example: User selects "File > New Puzzle > Medium"
```
sudoku_game.run()
    → pygame event: MOUSEBUTTONDOWN at menu
    → handle_click() → menu.handle_menu_click()
    → menu item: "New Puzzle > Medium"
    → callback: puzzle_gen.generate_new_puzzle("Medium")
    → returns: new grid (9×9 with ~27 clues)
    → sudoku_game.grid = new grid
    → ui.draw_grid(new grid)
    → display message: "Puzzle generated! (27 clues)"
```

---

## Refactoring Steps (Sequential)

### Step 1: Create `constants.py`
- Extract all constants, colors, fonts from sudoku_game.py
- Extract animation utilities (lerp, ease_in_out, draw_progress_bar, draw_rounded_rect)
- Test: `from constants import WIDTH, FONT_LARGE` works

### Step 2: Create `solver.py`
- Extract `generate_complete_grid()` function
- Extract all validation/solving methods into `SudokuSolver` class
- Move: `is_valid_placement()`, `get_candidates()`, `find_empty_cell()`, `solve_backtrack()`, `find_errors()`, `is_complete()`
- Test: `solver = SudokuSolver(grid); solver.is_valid_placement(0, 0, 5)` works

### Step 3: Create `ui.py`
- Extract all `draw_*()` methods into `UIRenderer` class
- Extract: `draw_grid()`, `draw_buttons()`, `draw_message()`, `draw_solver_panel()`, `get_cell_color()`
- Move animation state tracking (button_hover_state, cell_animations, etc.) to UIRenderer
- Test: `ui = UIRenderer(screen); ui.draw_grid(grid, None, {})` works

### Step 4: Create `menu.py`
- Extract menu methods into `MenuSystem` class
- Extract: `draw_menu_bar()`, `draw_menu_dropdowns()`, `handle_menu_click()`, `_draw_file_menu()`, `_draw_edit_menu()`, `_draw_new_puzzle_submenu()`
- Extract puzzle generation into `PuzzleGenerator` class
- Extract file I/O into `PuzzleIO` class
- Test: `menu = MenuSystem(screen); menu.draw_menu_bar()` works

### Step 5: Refactor `sudoku_game.py`
- Remove extracted methods (now in other modules)
- Import: `from constants import *; from solver import SudokuSolver; from ui import UIRenderer; from menu import MenuSystem, PuzzleGenerator`
- Update `__init__()`: Instantiate solver, ui, menu
- Update `render()`: Call `self.ui.draw_grid()`, `self.ui.draw_buttons()`, etc.
- Update `handle_click()`: Route to menu first, then grid, then buttons
- Update `solve_puzzle()`, `finalize_puzzle()`, `clear_grid()`: Delegate to solver
- Test: `python run.py` still works end-to-end

### Step 6: Update `run.py`
- No changes needed (still imports SudokuGame from sudoku_game.py)
- Just verify it still works

---

## Before vs After

### Before
```
src/sudoku_game.py (1,169 lines)
├── Constants (80 lines)
├── Helper functions (30 lines)
├── Puzzle generation (50 lines)
├── UI rendering (350 lines)
├── Menu system (150 lines)
├── File I/O (100 lines)
├── Solver algorithm (150 lines)
├── Game state & loop (200 lines)
└── Event handling (100 lines)

→ Hard to navigate, risky edits (change UI might break solver)
```

### After
```
src/
├── constants.py (80 lines) — Pure data & helpers
├── solver.py (150 lines) — Algorithm only (no Pygame)
├── ui.py (350 lines) — Drawing only
├── menu.py (250 lines) — Menu & file I/O (self-contained)
└── sudoku_game.py (150 lines) — Game loop & orchestration

→ Clear separation, testable modules, low coupling
```

---

## Benefits

| Aspect | Before | After |
|--------|--------|-------|
| **Navigation** | Scroll 1,169 lines | Jump to relevant 80-350 line module |
| **Testing** | Can't test solver without Pygame | Test solver with pure Python |
| **Reusability** | Tightly coupled | Solver module can be imported by other projects |
| **UI Polish** | Risk breaking solver when editing draw_* | Edit UI.py in isolation |
| **Menu Expansion** | Clutters sudoku_game.py | Grows in menu.py independently |
| **Debugging** | Find bug in 1,169 line file | Narrow down: solver? UI? Menu? |
| **Collaboration** | Hard to parallel work | One dev works on UI, another on solver |

---

## No Risk Refactoring

- Tests aren't affected (no test files yet)
- Import path stays the same (`from sudoku_game import SudokuGame`)
- User-facing behavior unchanged
- Easy rollback if needed (git revert)
- Can test incrementally at each step

---

## Implementation Effort

| Step | Time | Risk |
|------|------|------|
| Create constants.py | 10 min | Very Low |
| Create solver.py | 15 min | Very Low |
| Create ui.py | 20 min | Very Low |
| Create menu.py | 15 min | Very Low |
| Refactor sudoku_game.py | 15 min | Low |
| Test end-to-end | 10 min | Low |
| **Total** | **~85 min** | **Low** |

---

## Next Steps

1. **Approve this plan** — Does the split make sense? Any concerns?
2. **Execute step-by-step** — I'll do Step 1 (constants.py) first, verify it works, then Step 2, etc.
3. **Keep git clean** — One commit per step, clear messages
4. **Preserve history** — Old sudoku_game.py will live in test/ if needed for reference

Ready to proceed? Let me know if you'd like adjustments to the split.
