# Implementation Plan: Sudoku Requirements

**Based on**: sudoku-requirements.md  
**Status**: Comprehensive roadmap for Phases 7-9  
**Priority Order**: Validation/Puzzle State → System Generated Puzzles → Algorithm Menu → Statistics

---

## Phase Overview

```
┌─────────────────────────────────────────────────────────────┐
│ PHASE 7: Core Validation & Puzzle State Management         │
├─────────────────────────────────────────────────────────────┤
│ (2-3 weeks)                                                 │
│                                                             │
│ 7.1: Validation Engine (3 days)                            │
│ 7.2: Puzzle State System (2 days)                          │
│ 7.3: Finalize Button Redesign (2 days)                     │
│ 7.4: System Generated Puzzles (3 days)                     │
│ 7.5: Algorithm Selection Integration (2 days)              │
│ 7.6: Testing & Refinement (2 days)                         │
│                                                             │
│ Deliverable: v1.0.0 with validation + generation           │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ PHASE 8: Algorithm Menu & Hybrid Implementation            │
├─────────────────────────────────────────────────────────────┤
│ (1-2 weeks)                                                 │
│                                                             │
│ 8.1: Hybrid Algorithm Implementation (5 days)              │
│ 8.2: Algorithm Menu UI (2 days)                            │
│ 8.3: Menu Integration (2 days)                             │
│ 8.4: Testing (2 days)                                      │
│                                                             │
│ Deliverable: v1.1.0 with Hybrid + Algorithm Menu           │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ PHASE 9: Algorithm Statistics & Reporting                  │
├─────────────────────────────────────────────────────────────┤
│ (1-2 weeks)                                                 │
│                                                             │
│ 9.1: Algorithm Statistics Collection (3 days)              │
│ 9.2: Complexity Analysis (2 days)                          │
│ 9.3: Statistics UI & Menu (3 days)                         │
│ 9.4: Testing & Polish (2 days)                             │
│                                                             │
│ Deliverable: v1.2.0 with Statistics View                   │
└─────────────────────────────────────────────────────────────┘
```

---

## PHASE 7: Validation & Puzzle State System

### Overview

The core foundation: every puzzle must have a well-defined state (INVALID, NOT_SOLVABLE, MULTIPLE_SOLUTIONS, SINGLE_SOLUTION).

### 7.1: Validation Engine (3 days)

#### What Needs Building

```
Validation Pipeline:
├─ STEP 1: Basic Validation (Duplicate Check)
│  └─ is_valid_placement() [ALREADY EXISTS]
│
├─ STEP 2: Solvability Check
│  ├─ Can puzzle be solved?
│  └─ solve_backtrack() [ALREADY EXISTS]
│
├─ STEP 3: Solution Uniqueness Check
│  ├─ Does puzzle have exactly 1 solution?
│  └─ count_solutions() [NEW]
│
└─ STEP 4: Classify Puzzle State
   └─ INVALID | NOT_SOLVABLE | MULTIPLE_SOLUTIONS | SINGLE_SOLUTION
```

#### Code Changes: `solver.py`

**New Method: `count_solutions()`**

```python
def count_solutions(self, limit=2):
    """Count number of solutions (stop at limit for performance)
    
    Args:
        limit: Stop counting after finding this many (default 2)
               - If limit=2, we know: 0 (unsolvable), 1 (unique), 2+ (multiple)
    
    Returns: Number of solutions found (capped at limit)
    """
    solutions = []
    
    def backtrack():
        if len(solutions) >= limit:
            return  # Stop early (performance)
        
        empty = self.find_empty_cell()
        if not empty:
            solutions.append([row[:] for row in self.grid])
            return
        
        row, col = empty
        for num in range(1, 10):
            if self.is_valid_placement(row, col, num):
                self.grid[row][col] = num
                backtrack()
                self.grid[row][col] = 0
    
    grid_backup = [row[:] for row in self.grid]
    backtrack()
    self.grid[:] = grid_backup
    
    return len(solutions)
```

**New Enum: `PuzzleState`**

```python
from enum import Enum

class PuzzleState(Enum):
    INVALID = ("INVALID", (255, 0, 0))              # RED
    NOT_SOLVABLE = ("NOT_SOLVABLE", (255, 0, 0))    # RED
    MULTIPLE_SOLUTIONS = ("MULTIPLE_SOLUTIONS", (255, 165, 0))  # AMBER
    SINGLE_SOLUTION = ("SINGLE_SOLUTION", (0, 200, 0))  # GREEN
```

**New Method: `validate_puzzle()`**

```python
def validate_puzzle(self):
    """Validate puzzle and return state + message
    
    Returns: (PuzzleState, message_str, color)
    """
    # Step 1: Check for duplicates
    errors = self.find_errors()
    if errors:
        return (PuzzleState.INVALID, 
                f"Found {len(errors)} conflicts!", 
                (255, 0, 0))
    
    # Step 2: Check if solvable
    # Save grid
    grid_backup = [row[:] for row in self.grid]
    
    # Try to solve
    solver = SudokuSolver([row[:] for row in self.grid])
    if not solver.solve_backtrack():
        self.grid[:] = grid_backup
        return (PuzzleState.NOT_SOLVABLE,
                "Puzzle is not solvable!",
                (255, 0, 0))
    
    # Step 3: Check solution uniqueness
    solver = SudokuSolver([row[:] for row in grid_backup])
    num_solutions = solver.count_solutions(limit=2)
    
    self.grid[:] = grid_backup
    
    if num_solutions == 0:
        return (PuzzleState.NOT_SOLVABLE,
                "Not solvable",
                (255, 0, 0))
    elif num_solutions == 1:
        return (PuzzleState.SINGLE_SOLUTION,
                "Valid puzzle - exactly one solution!",
                (0, 200, 0))
    else:
        return (PuzzleState.MULTIPLE_SOLUTIONS,
                f"Multiple solutions exist ({num_solutions}+)",
                (255, 165, 0))
```

**Effort**: ~80 lines of new code  
**Testing**: 10-15 new unit tests

---

### 7.2: Puzzle State System (2 days)

#### What Needs Building

Track puzzle state and frozen cells throughout game lifecycle.

#### Code Changes: `sudoku_game.py`

**Add to `__init__`**

```python
# Puzzle state tracking (Phase 7)
self.puzzle_state = None  # PuzzleState enum
self.state_message = ""
self.state_color = (0, 0, 0)
self.finalized = False  # Is puzzle finalized?
self.frozen_cells = set()  # Read-only cells after finalize
self.solution_grid = None  # Reference solution (for validation)
```

**New Method: `finalize_puzzle()`** (Replace current)

```python
def finalize_puzzle(self):
    """Validate and finalize puzzle
    
    Process:
    1. Validate puzzle (check duplicates, solvability, uniqueness)
    2. If valid, freeze puzzle cells (read-only)
    3. Update UI accordingly
    """
    solver = SudokuSolver(self.grid)
    
    # Validate
    state, message, color = solver.validate_puzzle()
    self.puzzle_state = state
    self.state_message = message
    self.state_color = color
    
    # Only finalize on GREEN or AMBER state
    if state in [PuzzleState.SINGLE_SOLUTION, PuzzleState.MULTIPLE_SOLUTIONS]:
        self.finalized = True
        # Freeze all non-empty cells
        self.frozen_cells = set((i, j) for i in range(9) for j in range(9) 
                               if self.grid[i][j] != 0)
        
        # Store reference solution
        solver_copy = SudokuSolver([row[:] for row in self.grid])
        solver_copy.solve_backtrack()
        self.solution_grid = solver_copy.grid
        
        message_suffix = " (Puzzle finalized - cells are read-only)"
        self.state_message += message_suffix
    
    # Show message with appropriate color
    self.message = self.state_message
    self.message_color = self.state_color
    self.show_final_panel = False
```

**Update `_set_cell()` method**

```python
def _set_cell(self, row, col, value):
    """Set cell value (check if cell is frozen)"""
    
    # Check if cell is frozen (after finalize)
    if self.finalized and (row, col) in self.frozen_cells:
        self.message = "Cell is frozen! Click 'Clear' to unlock."
        self.message_color = RED
        return
    
    # Otherwise, allow modification
    self.grid[row][col] = value
    self._save_move_state()  # For undo/redo
    self.error_cells.clear()
    self.hint_candidates = []
```

**Effort**: ~100 lines of new code  
**Testing**: 8-10 new unit tests

---

### 7.3: Finalize Button & UI Redesign (2 days)

#### What Needs Changing

**UI Changes**:
1. Finalize button shows state visually (color coded)
2. Frozen cells render as greyed out/blue and read-only
3. Toast message shows puzzle state + color

#### Code Changes: `ui.py`

**Update `draw_buttons()` method**

```python
def draw_buttons(self):
    """Draw buttons with state-aware colors"""
    
    # Finalize button color based on puzzle state
    if self.game.finalized:
        button_color = (0, 200, 0)  # GREEN if finalized
        text = "FINALIZED"
    elif self.game.puzzle_state == PuzzleState.INVALID:
        button_color = (255, 0, 0)  # RED
        text = "FINALIZE (INVALID)"
    elif self.game.puzzle_state == PuzzleState.NOT_SOLVABLE:
        button_color = (255, 0, 0)  # RED
        text = "FINALIZE (NOT SOLVABLE)"
    elif self.game.puzzle_state == PuzzleState.MULTIPLE_SOLUTIONS:
        button_color = (255, 165, 0)  # AMBER
        text = "FINALIZE (MULTIPLE)"
    elif self.game.puzzle_state == PuzzleState.SINGLE_SOLUTION:
        button_color = (0, 200, 0)  # GREEN
        text = "FINALIZE (UNIQUE)"
    else:
        button_color = (100, 150, 255)  # BLUE (neutral)
        text = "FINALIZE"
    
    # Draw button with calculated color
    # ... (existing drawing code)
```

**Update `draw_cells()` method**

```python
def draw_cells(self):
    """Draw cells with frozen highlighting"""
    
    for i in range(9):
        for j in range(9):
            # ... existing cell rendering ...
            
            # If frozen, use special color
            if (i, j) in self.game.frozen_cells:
                cell_bg_color = (200, 220, 255)  # Light blue
                # Render as read-only (no selection highlight possible)
```

**Effort**: ~50 lines of changes  
**Testing**: Visual testing (no unit tests needed)

---

### 7.4: System Generated Puzzles (3 days)

#### What Needs Building

Generate puzzles with guaranteed **single solution** at difficulty levels.

#### Key Insight

Current code:
```python
def generate_puzzle(difficulty='medium'):
    solution = generate_complete_grid()
    puzzle = copy(solution)
    # Randomly remove clues (NO uniqueness check!)
    # Result: Often multiple solutions
```

Must change to:
```python
def generate_puzzle(difficulty='medium'):
    solution = generate_complete_grid()
    puzzle = copy(solution)
    
    # Carefully remove clues ONE BY ONE
    # After each removal, CHECK if still unique solution
    # Keep removal only if unique
    # Continue until reach target difficulty
```

#### Code Changes: `solver.py`

**New Method: `generate_puzzle_with_uniqueness()`**

```python
def generate_puzzle_with_uniqueness(difficulty='medium', timeout_seconds=30):
    """Generate puzzle with GUARANTEED single solution
    
    Args:
        difficulty: 'easy' (1-20 clues), 'medium' (20-40), 'hard' (40-60)
        timeout_seconds: Give up if takes too long
    
    Returns: (puzzle_grid, solution_grid, difficulty_measure)
    
    Algorithm:
    1. Generate complete valid grid (solution)
    2. Copy to puzzle
    3. Randomly remove clues ONE BY ONE
    4. After each removal: verify still has unique solution
    5. Stop when reach target clue count
    """
    
    import time
    start_time = time.time()
    
    # Generate complete solution
    solution = generate_complete_grid()
    puzzle = [row[:] for row in solution]
    
    # Difficulty mapping
    difficulty_map = {
        'easy': (10, 25),       # 10-25 clues
        'medium': (20, 35),     # 20-35 clues
        'hard': (30, 50)        # 30-50 clues
    }
    
    min_clues, max_clues = difficulty_map.get(difficulty, (20, 35))
    target_clues = random.randint(min_clues, max_clues)
    
    cells = [(i, j) for i in range(9) for j in range(9)]
    random.shuffle(cells)
    
    removed = 0
    
    for row, col in cells:
        # Check timeout
        if time.time() - start_time > timeout_seconds:
            break
        
        # Try removing this cell
        if puzzle[row][col] != 0:
            backup = puzzle[row][col]
            puzzle[row][col] = 0
            
            # Check: still unique solution?
            solver = SudokuSolver([row[:] for row in puzzle])
            num_solutions = solver.count_solutions(limit=2)
            
            if num_solutions == 1:
                # Good! Keep removal
                removed += 1
                
                if removed >= (81 - target_clues):
                    # Reached target
                    break
            else:
                # Bad! Restore cell
                puzzle[row][col] = backup
    
    clue_count = sum(1 for row in puzzle for cell in row if cell != 0)
    
    return puzzle, solution, clue_count
```

**Update `generate_puzzle()`** to use new method

```python
def generate_puzzle(difficulty='medium'):
    """Public API (calls new method)"""
    return generate_puzzle_with_uniqueness(difficulty)
```

**Effort**: ~120 lines of new code  
**Performance**: 30-60 seconds per puzzle (acceptable for generation, not user-facing)  
**Testing**: 5-8 new tests

---

### 7.5: Algorithm Selection Integration (2 days)

#### What Needs Building

Wire selected algorithm to Solve Algo button and puzzle generation.

#### Code Changes

**In `sudoku_game.py`**

```python
def __init__(self):
    # ... existing code ...
    
    # Algorithm selection (Phase 7)
    self.selected_algorithm = "hybrid"  # Default: 'hybrid', 'constraint_prop', 'mrv', 'naive', 'dancing_links'
    self.algorithm_stats = {}  # Track stats for each algorithm
```

**Update `solve_puzzle()` method**

```python
def solve_puzzle(self, animated=True):
    """Solve using selected algorithm"""
    
    # Use selected algorithm
    if self.selected_algorithm == "dancing_links":
        # For instant solve (not step-by-step)
        result = self._solve_dancing_links()
    elif self.selected_algorithm == "hybrid":
        result = self._solve_hybrid(animated)
    elif self.selected_algorithm == "constraint_prop":
        result = self._solve_constraint_prop(animated)
    elif self.selected_algorithm == "mrv":
        result = self._solve_mrv(animated)
    else:
        result = self._solve_naive(animated)
    
    return result
```

**Effort**: ~50 lines of refactoring  
**Testing**: 5-6 new tests

---

### 7.6: Testing & Refinement (2 days)

#### Test Cases to Add

```
Validation Tests:
✓ Valid puzzle with no conflicts
✓ Invalid puzzle with row duplicates
✓ Invalid puzzle with column duplicates
✓ Invalid puzzle with box duplicates
✓ Solvable with single solution
✓ Solvable with multiple solutions
✓ Unsolvable puzzle
✓ Empty grid (special case)

Finalize Tests:
✓ Finalize SINGLE_SOLUTION puzzle
✓ Finalize MULTIPLE_SOLUTIONS puzzle
✓ Cannot finalize INVALID puzzle
✓ Frozen cells are read-only
✓ Clear button unlocks frozen cells

Generation Tests:
✓ Easy puzzle generates with correct clue range
✓ Medium puzzle generates with correct clue range
✓ Hard puzzle generates with correct clue range
✓ Generated puzzle has single solution
✓ Generated puzzle is solvable
```

**Effort**: ~200 lines of test code

---

## Summary: Phase 7 Deliverables

| Component | Status | Tests | Effort |
|-----------|--------|-------|--------|
| Validation Engine | New | 10 | 3 days |
| Puzzle State System | New | 10 | 2 days |
| UI Redesign | Modified | 0 | 2 days |
| System Generated Puzzles | New | 8 | 3 days |
| Algorithm Integration | Modified | 6 | 2 days |
| Testing & Polish | New | 20 | 2 days |
| **TOTAL** | | **54** | **~14 days** |

---

## Key Features Phase 7 Enables

✅ Puzzle state clearly communicated (RED/AMBER/GREEN)  
✅ Frozen cells after finalize (read-only)  
✅ System-generated puzzles with guaranteed single solution  
✅ Accurate difficulty classification (by clue count + uniqueness)  
✅ Foundation for algorithm selection (Phase 8)  
✅ Foundation for statistics collection (Phase 9)  

---

## Compatibility With Phase 8-9

Phase 7 creates foundation for:

**Phase 8**: Algorithm Menu
- Can now swap algorithms at runtime
- Each algorithm gets stats collected

**Phase 9**: Algorithm Statistics
- Validation now generates data for all algorithms
- Statistics dashboard can show comparison

---

## Files to Modify/Create

### Modify
- `src/solver.py` - Add validation + generation
- `src/sudoku_game.py` - Add state system + algorithm integration
- `src/ui.py` - Add state-aware rendering
- `tests/test_validation.py` - NEW (validation tests)

### Create
- `src/puzzle_state.py` - New enum for states (optional, can be in solver.py)

---

## Recommendation

**Start with Phase 7 immediately after deciding on algorithm choice:**

1. ✅ Decide: Algorithm for Phase 8 (Hybrid recommended)
2. ✅ Implement Phase 7: Validation + Puzzle State (2 weeks)
3. ✅ Implement Phase 8: Algorithm Menu + Hybrid (1-2 weeks)
4. ✅ Release v1.1.0
5. ⏳ Implement Phase 9: Statistics (1-2 weeks)
6. ⏳ Release v1.2.0

---

**Document Created**: 2026-08-22  
**Status**: Ready for Phase 7 implementation  
**Prerequisites**: Algorithm decision (Phase 8 choice)  
**Estimated Duration**: 14 days for Phase 7
