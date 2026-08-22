# Phase 7 Detailed Task Breakdown

**Based on**: sudoku-requirements.md  
**Implementation Plan**: 2-week sprint (14 days)

---

## Sprint Structure

```
Week 1:
├─ Days 1-3: Validation Engine (7.1)
├─ Days 3-4: Puzzle State System (7.2)
└─ Days 5: Finalize Button & UI (7.3)

Week 2:
├─ Days 6-8: System Generated Puzzles (7.4)
├─ Day 9: Algorithm Integration (7.5)
└─ Days 10-11: Testing & Refinement (7.6)
```

---

## Day 1-3: Validation Engine (7.1)

### Task 7.1.1: Add PuzzleState Enum

**Files**: `src/solver.py`

```python
from enum import Enum

class PuzzleState(Enum):
    """Puzzle validation state"""
    INVALID = "INVALID"              # RED - Has conflicts
    NOT_SOLVABLE = "NOT_SOLVABLE"    # RED - No solution exists
    MULTIPLE_SOLUTIONS = "MULTIPLE_SOLUTIONS"  # AMBER - Multiple solutions
    SINGLE_SOLUTION = "SINGLE_SOLUTION"        # GREEN - Exactly one solution
```

**Checklist**:
- [ ] Create enum with 4 states
- [ ] Document color mapping (RED/AMBER/GREEN)
- [ ] Add to imports in sudoku_game.py

---

### Task 7.1.2: Implement `count_solutions()` Method

**Files**: `src/solver.py` → `SudokuSolver` class

```python
def count_solutions(self, limit=2):
    """Count number of solutions (stop at limit)
    
    Args:
        limit: Stop after finding this many (default 2)
               Performance: We only need to know if 0, 1, or 2+
    
    Returns: Integer count (capped at limit)
    """
```

**Checklist**:
- [ ] Implement backtracking counter
- [ ] Add early exit (when count >= limit)
- [ ] Preserve original grid (backup/restore)
- [ ] Test with solvable puzzles
- [ ] Test with multiple-solution puzzles
- [ ] Test with unsolvable puzzles
- [ ] Measure performance (should be <5 seconds for any puzzle)

**Test Cases**:
```
✓ count_solutions(empty_grid) == 2+ (lots)
✓ count_solutions(valid_puzzle_single) == 1
✓ count_solutions(valid_puzzle_multiple) == 2+
✓ count_solutions(unsolvable_puzzle) == 0
✓ Grid unchanged after counting
✓ Early exit at limit (performance)
```

---

### Task 7.1.3: Implement `validate_puzzle()` Method

**Files**: `src/solver.py` → `SudokuSolver` class

```python
def validate_puzzle(self):
    """Validate puzzle and return (state, message, color)
    
    Steps:
    1. Check for conflicts (duplicates)
    2. Check solvability
    3. Check solution uniqueness
    
    Returns: (PuzzleState, str_message, color_tuple)
    """
```

**Checklist**:
- [ ] Step 1: Check duplicates using `find_errors()`
- [ ] Step 2: Try to solve (quick check)
- [ ] Step 3: Count solutions
- [ ] Return appropriate state
- [ ] Include helpful message
- [ ] Test all 4 state combinations
- [ ] Test edge cases (empty grid)

**Test Cases**:
```
✓ INVALID: Puzzle with duplicates → RED
✓ NOT_SOLVABLE: Puzzle with no solution → RED
✓ MULTIPLE_SOLUTIONS: Puzzle with many → AMBER
✓ SINGLE_SOLUTION: Valid puzzle → GREEN
✓ EMPTY_GRID: Special case → MULTIPLE_SOLUTIONS (treated as AMBER)
✓ Message text helpful and clear
✓ Color values correct
```

---

### Task 7.1.4: Add Unit Tests

**Files**: `tests/test_validation.py` (NEW)

```python
class TestValidation:
    def test_valid_puzzle_single_solution(self):
        # Valid puzzle should return SINGLE_SOLUTION
        
    def test_invalid_puzzle_with_duplicates(self):
        # Puzzle with row duplicates should return INVALID
        
    def test_unsolvable_puzzle(self):
        # Puzzle with no solution should return NOT_SOLVABLE
        
    def test_multiple_solutions(self):
        # Puzzle with many solutions should return MULTIPLE_SOLUTIONS
        
    # ... 10-12 more tests
```

**Checklist**:
- [ ] Create test_validation.py
- [ ] Write 12-15 test cases
- [ ] All tests pass
- [ ] Run full test suite (166 + new tests)

---

## Day 3-4: Puzzle State System (7.2)

### Task 7.2.1: Add State Tracking to Game

**Files**: `src/sudoku_game.py` → `SudokuGame.__init__()`

```python
def __init__(self):
    # ... existing code ...
    
    # Puzzle state tracking (Phase 7)
    self.puzzle_state = None  # PuzzleState enum value
    self.state_message = ""   # Message to display
    self.state_color = (0, 0, 0)  # Color for message
    self.finalized = False    # Is puzzle locked?
    self.frozen_cells = set()  # (row, col) tuples of read-only cells
    self.solution_grid = None  # Stored solution for reference
```

**Checklist**:
- [ ] Add all 5 state variables
- [ ] Initialize to safe defaults
- [ ] Import PuzzleState enum
- [ ] No side effects (game still runs)

---

### Task 7.2.2: Update `handle_key()` for Finalize Shortcut

**Files**: `src/sudoku_game.py` → `handle_key()` method

```python
def handle_key(self, key, mod=0):
    # ... existing shortcuts ...
    
    if key == pygame.K_f:  # F = Finalize (already exists?)
        self.finalize_puzzle()
        return
```

**Checklist**:
- [ ] F key triggers finalize
- [ ] Works without errors
- [ ] Doesn't interfere with other shortcuts

---

### Task 7.2.3: Replace `finalize_puzzle()` Method

**Files**: `src/sudoku_game.py` → `finalize_puzzle()` method

**OLD** (current implementation):
```python
def finalize_puzzle(self):
    # Just checks for conflicts and completeness
```

**NEW** (validation + state + freezing):
```python
def finalize_puzzle(self):
    """Validate and finalize puzzle
    
    1. Validate puzzle (get state)
    2. If valid (GREEN/AMBER), freeze cells
    3. Update UI
    4. Store solution reference
    """
    
    solver = SudokuSolver([row[:] for row in self.grid])
    state, message, color = solver.validate_puzzle()
    
    self.puzzle_state = state
    self.state_message = message
    self.state_color = color
    
    # Only finalize on GREEN or AMBER
    if state in [PuzzleState.SINGLE_SOLUTION, PuzzleState.MULTIPLE_SOLUTIONS]:
        self.finalized = True
        self.frozen_cells = set((i, j) for i in range(9) for j in range(9)
                               if self.grid[i][j] != 0)
        
        # Store reference solution
        solver_copy = SudokuSolver([row[:] for row in self.grid])
        solver_copy.solve_backtrack()
        self.solution_grid = solver_copy.grid
    
    # Show state message
    self.message = self.state_message
    self.message_color = self.state_color
```

**Checklist**:
- [ ] Use validator from solver
- [ ] Get state, message, color
- [ ] Freeze cells if valid
- [ ] Store solution if valid
- [ ] Display correct message
- [ ] Test all state transitions
- [ ] Test RED states (don't freeze)
- [ ] Test AMBER/GREEN states (freeze)

---

### Task 7.2.4: Update `_set_cell()` to Check Frozen

**Files**: `src/sudoku_game.py` → `_set_cell()` method

```python
def _set_cell(self, row, col, value):
    """Set cell value (respecting frozen cells)"""
    
    # Check if cell is frozen after finalize
    if self.finalized and (row, col) in self.frozen_cells:
        self.message = "Cell is frozen! Click Clear to unlock."
        self.message_color = RED
        return
    
    # Normal cell modification
    self.grid[row][col] = value
    self._save_move_state()
    self.error_cells.clear()
    self.hint_candidates = []
```

**Checklist**:
- [ ] Check if finalized
- [ ] Check if cell in frozen set
- [ ] Show warning if frozen
- [ ] Otherwise allow modification
- [ ] Test with frozen cells (should fail)
- [ ] Test with unfrozen cells (should work)

---

### Task 7.2.5: Update `clear_grid()` to Unlock

**Files**: `src/sudoku_game.py` → `clear_grid()` method

```python
def clear_grid(self):
    """Clear grid and unlock frozen cells"""
    
    self.grid = [[0 for _ in range(9)] for _ in range(9)]
    self.frozen_cells.clear()  # Unlock!
    self.finalized = False  # Unlock!
    self.selected_cell = (0, 0)
    self.error_cells.clear()
    self.hint_candidates = []
    self.move_history = []
    self.move_index = -1
    
    # Reset state
    self.puzzle_state = None
    self.state_message = ""
    
    self.message = "Grid cleared!"
    self.message_color = BLUE
```

**Checklist**:
- [ ] Clear frozen_cells set
- [ ] Reset finalized flag
- [ ] Reset puzzle_state
- [ ] Test: After clear, can modify any cell
- [ ] Test: Finalize again works

---

### Task 7.2.6: Add Unit Tests

**Files**: `tests/test_puzzle_state.py` (NEW)

```python
class TestPuzzleState:
    def test_finalize_invalid_puzzle(self):
        # Finalize RED puzzle should not freeze
        
    def test_finalize_valid_puzzle(self):
        # Finalize GREEN puzzle should freeze
        
    def test_frozen_cells_readonly(self):
        # Can't modify frozen cells
        
    def test_clear_unfreezes(self):
        # Clear button unfreezes everything
        
    # ... 8-10 more tests
```

**Checklist**:
- [ ] Write 10-12 tests
- [ ] All tests pass
- [ ] Test frozen cell behavior
- [ ] Test state transitions
- [ ] Run full test suite

---

## Day 5: Finalize Button & UI (7.3)

### Task 7.3.1: Update Button Colors

**Files**: `src/ui.py` → `draw_buttons()` method

```python
def draw_buttons(self):
    # Current: static button colors
    # New: Color based on puzzle state
    
    if self.game.finalized:
        finalize_color = GREEN  # (0, 200, 0)
    elif self.game.puzzle_state == PuzzleState.SINGLE_SOLUTION:
        finalize_color = GREEN
    elif self.game.puzzle_state == PuzzleState.MULTIPLE_SOLUTIONS:
        finalize_color = AMBER  # (255, 165, 0)
    elif self.game.puzzle_state == PuzzleState.INVALID:
        finalize_color = RED
    elif self.game.puzzle_state == PuzzleState.NOT_SOLVABLE:
        finalize_color = RED
    else:
        finalize_color = BLUE  # Default neutral
    
    # Draw finalize button with calculated color
```

**Checklist**:
- [ ] Import PuzzleState
- [ ] Check puzzle state in draw_buttons
- [ ] Set button color accordingly
- [ ] Button label updates to show state
- [ ] Test all 5 color states visually

---

### Task 7.3.2: Render Frozen Cells Differently

**Files**: `src/ui.py` → `draw_cells()` method

```python
def draw_cells(self):
    # In cell drawing loop:
    
    for i in range(9):
        for j in range(9):
            if (i, j) in self.game.frozen_cells:
                # Frozen cell: use blue background
                cell_bg_color = (200, 220, 255)  # Light blue
                # Optional: slightly different text color
                text_color = (0, 0, 100)  # Dark blue
            else:
                # Normal cells
                cell_bg_color = get_normal_color(...)
                text_color = BLACK
            
            # Draw cell with appropriate colors
```

**Checklist**:
- [ ] Frozen cells have light blue background
- [ ] Non-frozen cells unchanged
- [ ] Text color appropriate
- [ ] Test visually: frozen cells clearly different
- [ ] Test visually: after finalize, puzzle cells blue
- [ ] Test visually: after clear, all cells white

---

### Task 7.3.3: Update Message Toast

**Files**: `src/ui.py` → `draw_message()` method

```python
# Update to show state color in message background
# Already have message_color from game.state_color
```

**Checklist**:
- [ ] Message uses state_color
- [ ] RED messages show in red
- [ ] AMBER messages show in amber
- [ ] GREEN messages show in green
- [ ] Test visually: colors appear correctly

---

## Days 6-8: System Generated Puzzles (7.4)

### Task 7.4.1: Implement `generate_puzzle_with_uniqueness()`

**Files**: `src/solver.py` → Top-level function

```python
def generate_puzzle_with_uniqueness(difficulty='medium', timeout_seconds=30):
    """Generate puzzle with guaranteed single solution
    
    Algorithm:
    1. Generate complete valid grid
    2. Randomly remove clues one by one
    3. After each removal, verify still unique solution
    4. Keep removal only if unique
    5. Stop when reach target clue count
    
    Takes 30-60 seconds per puzzle (acceptable for generation)
    """
```

**Checklist**:
- [ ] Generate complete grid first
- [ ] Define difficulty ranges (easy 10-25, medium 20-35, hard 30-50)
- [ ] Implement removal loop
- [ ] Check uniqueness after each removal
- [ ] Only keep removal if still unique
- [ ] Stop when reach target
- [ ] Add timeout (30 seconds)
- [ ] Return (puzzle, solution, clue_count)

**Performance Requirements**:
- [ ] Easy: <30 seconds
- [ ] Medium: 30-60 seconds
- [ ] Hard: 30-90 seconds

---

### Task 7.4.2: Update `generate_puzzle()` API

**Files**: `src/solver.py`

```python
# OLD
def generate_puzzle(difficulty='medium'):
    solution = generate_complete_grid()
    puzzle = copy(solution)
    # Random removal (no uniqueness check)
    return puzzle, solution

# NEW
def generate_puzzle(difficulty='medium'):
    """Public API - generates puzzle with guaranteed single solution"""
    return generate_puzzle_with_uniqueness(difficulty)
```

**Checklist**:
- [ ] Update to use new function
- [ ] Test interface unchanged
- [ ] All existing calls still work
- [ ] Existing tests pass

---

### Task 7.4.3: Wire Into Menu System

**Files**: `src/menu.py` → `generate_puzzle()` method

```python
@staticmethod
def generate_puzzle(difficulty):
    """Generate new puzzle via menu"""
    # Call solver.generate_puzzle()
    puzzle, solution, clue_count = solver.generate_puzzle(difficulty)
    
    # Will now have guaranteed single solution!
    return puzzle, solution, clue_count
```

**Checklist**:
- [ ] Menu calls new generator
- [ ] Puzzle generation still works
- [ ] Generated puzzles now have single solution
- [ ] Test menu: New Puzzle → Easy
- [ ] Test menu: New Puzzle → Medium
- [ ] Test menu: New Puzzle → Hard

---

### Task 7.4.4: Auto-Finalize Generated Puzzles

**Files**: `src/sudoku_game.py` → `_process_menu_action()` method

```python
elif action_type == 'new_puzzle':
    # Generate puzzle with guaranteed single solution
    puzzle, solution, clue_count = MenuSystem.generate_puzzle(difficulty)
    
    if puzzle:
        self.grid = puzzle
        self.solution = solution
        self.puzzle_difficulty = difficulty
        
        # NEW: Auto-validate and freeze
        solver = SudokuSolver([row[:] for row in self.grid])
        state, msg, color = solver.validate_puzzle()
        
        # Should be SINGLE_SOLUTION (guaranteed by generation)
        if state == PuzzleState.SINGLE_SOLUTION:
            self.puzzle_state = state
            self.finalized = True
            self.frozen_cells = set((i, j) for i in range(9) for j in range(9)
                                   if self.grid[i][j] != 0)
            self.solution_grid = self.solution
            
            self.message = f"Puzzle generated ({difficulty}): {clue_count} clues - FINALIZED"
            self.message_color = GREEN
```

**Checklist**:
- [ ] Generated puzzles auto-finalize
- [ ] Puzzle cells are frozen (read-only)
- [ ] State shown as GREEN
- [ ] Can still solve and interact
- [ ] Test: Generate Easy → auto-frozen
- [ ] Test: Generate Medium → auto-frozen
- [ ] Test: Generate Hard → auto-frozen

---

### Task 7.4.5: Unit Tests

**Files**: `tests/test_puzzle_generation.py` (NEW)

```python
class TestPuzzleGeneration:
    def test_generate_easy_puzzle(self):
        # Easy puzzle should have 10-25 clues
        
    def test_generate_medium_puzzle(self):
        # Medium puzzle should have 20-35 clues
        
    def test_generate_hard_puzzle(self):
        # Hard puzzle should have 30-50 clues
        
    def test_generated_puzzle_solvable(self):
        # All generated puzzles must be solvable
        
    def test_generated_puzzle_unique(self):
        # All generated puzzles must have exactly 1 solution
        
    # ... 8-10 more tests
```

**Checklist**:
- [ ] Write 10-12 tests
- [ ] All tests pass
- [ ] Generated puzzles always have 1 solution
- [ ] Clue counts in correct ranges
- [ ] All puzzles solvable

---

## Day 9: Algorithm Integration (7.5)

### Task 7.5.1: Add Algorithm Selection to Game

**Files**: `src/sudoku_game.py` → `__init__()`

```python
def __init__(self):
    # ... existing code ...
    
    # Algorithm selection (Phase 7 / Phase 8 prep)
    self.selected_algorithm = "hybrid"  # Default
    # Valid values: 'hybrid', 'constraint_prop', 'mrv', 'naive', 'dancing_links'
```

**Checklist**:
- [ ] Add algorithm variable
- [ ] Default to 'hybrid' (recommended)
- [ ] Document valid values

---

### Task 7.5.2: Update `solve_puzzle()` to Use Algorithm

**Files**: `src/sudoku_game.py` → `solve_puzzle()` method

```python
def solve_puzzle(self, animated=True):
    """Solve using selected algorithm"""
    
    # Currently uses solve_backtrack directly
    # Update to switch based on selected_algorithm
    
    if animated:
        if self.selected_algorithm == "hybrid":
            self.solver_gen = self._solve_hybrid()
        elif self.selected_algorithm == "constraint_prop":
            self.solver_gen = self._solve_constraint_prop()
        elif self.selected_algorithm == "mrv":
            self.solver_gen = self._solve_with_mrv()
        else:
            self.solver_gen = self._solve_with_steps()  # Naive
    else:
        # Fast solve: currently uses solve_backtrack
        # Update to use selected algorithm instant solve
        self.solve_fast_complete()
```

**Checklist**:
- [ ] Check algorithm selection
- [ ] Route to appropriate solver
- [ ] Fallback to current if not implemented
- [ ] Test: Different algorithms solvable
- [ ] Test: Algorithm selection doesn't break

---

### Task 7.5.3: Unit Tests

**Files**: `tests/test_algorithm_selection.py` (NEW)

```python
class TestAlgorithmSelection:
    def test_algorithm_selection_set(self):
        # Algorithm can be set
        game.selected_algorithm = "hybrid"
        assert game.selected_algorithm == "hybrid"
        
    def test_algorithm_solve_works(self):
        # Selected algorithm can solve puzzle
        game.selected_algorithm = "hybrid"
        game.solve_puzzle()
        # Should complete without error
        
    # ... 5-8 more tests
```

**Checklist**:
- [ ] Write 6-8 tests
- [ ] All tests pass
- [ ] Algorithm selection works

---

## Days 10-11: Testing & Refinement (7.6)

### Task 7.6.1: Integration Testing

**Test Scenarios**:

1. Full User Flow
   - [ ] User generates puzzle → auto-finalized
   - [ ] Frozen cells read-only
   - [ ] Can still solve it
   - [ ] Statistics collected

2. Finalize Flow
   - [ ] Valid puzzle → GREEN, frozen
   - [ ] Invalid puzzle → RED, not frozen
   - [ ] Multiple solutions → AMBER, frozen
   - [ ] No solutions → RED, not frozen

3. State Persistence
   - [ ] Puzzle state survives solve
   - [ ] Frozen cells survive pause/resume
   - [ ] State survives load/save

---

### Task 7.6.2: Performance Testing

**Performance Targets**:
- [ ] Validation < 5 seconds (any puzzle)
- [ ] Generation < 90 seconds (hard)
- [ ] UI responsive during validation
- [ ] No freezes or lag

**Measurements**:
- [ ] Validate easy puzzle: < 1s
- [ ] Validate hard puzzle: < 5s
- [ ] Generate easy: < 30s
- [ ] Generate hard: < 90s
- [ ] FPS stable at 60

---

### Task 7.6.3: Bug Fixes & Polish

**Fixes**:
- [ ] Fix any frozen cell edge cases
- [ ] Fix any state transition issues
- [ ] Fix any UI color issues
- [ ] Fix any message display issues

**Polish**:
- [ ] Ensure consistent messaging
- [ ] Ensure consistent colors
- [ ] Ensure smooth transitions
- [ ] Ensure good user feedback

---

### Task 7.6.4: Full Test Suite Run

**Final Checklist**:
- [ ] All 166 original tests pass
- [ ] All 50+ new tests pass
- [ ] No regressions
- [ ] No crashes
- [ ] No warnings

---

## Success Criteria Phase 7

✅ **Validation Engine**
- Puzzles correctly classified (INVALID/NOT_SOLVABLE/MULTIPLE/SINGLE)
- Validation fast enough for user-facing operations
- Messages clear and helpful

✅ **Puzzle State System**
- States properly tracked
- UI reflects state (colors)
- Frozen cells work correctly
- Clear button unfreezes

✅ **System Generated Puzzles**
- Generated puzzles have guaranteed single solution
- Difficulty ranges correct
- Generation time acceptable
- Auto-finalization works

✅ **Algorithm Integration**
- Algorithm selection variable works
- Can swap algorithms
- All existing algorithms still work
- Ready for Phase 8 menu

✅ **Testing**
- 50+ new unit tests
- All tests passing
- No regressions
- Full test suite coverage

---

## Files Summary

### Modified Files
- `src/solver.py` - Add validation + generation (~250 lines)
- `src/sudoku_game.py` - Add state system (~150 lines)
- `src/ui.py` - Add state-aware rendering (~50 lines)

### New Files
- `tests/test_validation.py` - Validation tests (~150 lines)
- `tests/test_puzzle_state.py` - State tests (~120 lines)
- `tests/test_puzzle_generation.py` - Generation tests (~130 lines)
- `tests/test_algorithm_selection.py` - Algorithm tests (~80 lines)

### Total Addition
- ~450 lines new source code
- ~480 lines new test code
- ~50 lines modified existing code

---

## Next Phase: Phase 8 (Algorithm Menu)

After Phase 7 completes:
- [ ] Algorithm selection ready (variable exists)
- [ ] Multiple solver methods exist (or stubbed)
- [ ] Tests passing

Phase 8 will:
- [ ] Implement Hybrid algorithm
- [ ] Create Algorithm menu UI
- [ ] Wire menu to solver selection

---

**Document Created**: 2026-08-22  
**Total Phase 7 Effort**: 14 days  
**Ready to start**: After algorithm decision
