# Sudoku Game - Python Pygame Application

A fully-featured Sudoku game built with Python and Pygame, featuring a modern UI with smooth animations, user input validation, error highlighting, and an educational algorithm visualizer.

## 📚 Documentation Hub

| Category | Location | Purpose |
|----------|----------|---------|
| **Navigation** | [design/NAVIGATION_GUIDE.md](./design/NAVIGATION_GUIDE.md) | Find what you need quickly |
| **Design Docs** | [design/README.md](./design/README.md) | Colors, animations, UI decisions |
| **Testing** | [tests/procedures/README.md](./tests/procedures/README.md) | Phase 5 testing procedures |
| **Project Status** | [docs/PROJECT_STATUS.md](./docs/PROJECT_STATUS.md) | Complete project report |
| **Code Guidelines** | [AGENTS.md](./AGENTS.md) | Style and architecture |
| **Quick Start** | Below | Get playing in 30 seconds |

## Features

✅ **Modern UI Design** - Clean interface with Material Design colors and smooth animations  
✅ **Blank 9x9 Grid** - Start with an empty Sudoku grid with enhanced visual hierarchy  
✅ **Interactive Cell Selection** - Click to select cells with smooth highlighting animations  
✅ **Number Entry** - Type numbers 1-9 to fill cells with visual feedback  
✅ **Finalize Button** - Validates your completed puzzle  
✅ **Clear Button** - Reset the entire grid to start over  
✅ **Educational Solver** - Animated step-by-step backtracking with smooth cell fill animations  
✅ **Advanced Algorithm Panel** - Progress bars, pulsing statistics, and real-time metrics  
✅ **Visual Progress Tracking** - Steps and backtracks displayed with animated progress bars  
✅ **Smooth Animations** - Cell fills, button hover effects, stat pulses  
✅ **Solver Controls** - Pause/resume, adjust speed, and stop at any time  
✅ **Error Highlighting** - Invalid entries highlighted with soft, pleasant colors  
✅ **Visual Feedback** - Toast-style message display with backgrounds  
✅ **Intuitive Controls** - Mouse and keyboard support with real-time hover feedback  

## Installation

### Prerequisites
- Python 3.7 or higher
- uv (Python package manager)

### Setup

1. **Clone or download this repository**

2. **Install dependencies**
   ```bash
   uv sync
   ```

## How to Run

Navigate to the project directory and run:

```bash
python run.py
```

Or with uv:
```bash
uv run python run.py
```

## Testing

The project includes a comprehensive test suite with 122 unit tests covering all modules.

### Run All Tests

```bash
uv run pytest tests/ -v
```

### Test Coverage

- **122 tests** covering all modules (Phase 5 automated testing)
  - `test_animations.py` - 24 tests (animations and easing)
  - `test_color_palette.py` - 16 tests (Material Design colors)
  - `test_game.py` - 22 tests (game logic and state)
  - `test_menu.py` - 30 tests (menu system and file I/O)
  - `test_solver.py` - 30 tests (solver algorithms and puzzle generation)
- **100% pass rate** across all tests
- Execution time: ~2 seconds

### Phase 5 Testing

For comprehensive Phase 5 testing procedures (manual testing with visual verification):
- **Start**: [tests/procedures/PHASE5_QUICK_START.txt](./tests/procedures/PHASE5_QUICK_START.txt) (5 min read)
- **Detailed**: [tests/procedures/PHASE5_TESTING.md](./tests/procedures/PHASE5_TESTING.md) (360+ lines)
- **Track Results**: [tests/procedures/PHASE5_TESTING_RESULTS.md](./tests/procedures/PHASE5_TESTING_RESULTS.md)

### Run Specific Tests

```bash
# Run only solver tests
uv run pytest tests/test_solver.py -v

# Run only menu tests
uv run pytest tests/test_menu.py -v

# Run animation tests
uv run pytest tests/test_animations.py -v

# Run a specific test class
uv run pytest tests/test_solver.py::TestSudokuSolver -v
```

See [tests/README.md](./tests/README.md) for detailed test documentation.

## How to Play

### Controls

**Mouse:**
- Click on any cell to select it (highlighted in light blue)
- Click buttons to perform actions

**Keyboard:**
- Press **1-9** to enter a number in the selected cell
- Press **0**, **Backspace**, or **Delete** to clear a cell
- Use number pad keys (1-9) as an alternative

### Buttons (2x2 Grid Layout)

**Row 1:**

1. **Finalize** (Green)
   - Validates your completed puzzle
   - Shows success message if correct
   - Highlights errors in red if there are conflicts

2. **Clear** (Red)
   - Clears the entire grid
   - Resets all cells to empty

**Row 2:**

3. **Solve Algo** (Dark Blue)
   - Solves the puzzle step-by-step with animation
   - Shows algorithm execution in real-time with a side panel
   - Uses backtracking algorithm with visual feedback
   - Shows "No solution exists!" if puzzle is unsolvable
   - Press SPACE to pause/resume, UP/DOWN to adjust speed, ESC to stop

4. **Solve Fast** (Light Blue)
   - Solves the puzzle instantly without animation
   - Displays final algorithm statistics in the side panel
   - Shows total steps and backtrack count instantly

### Game Rules

A valid Sudoku puzzle must satisfy:
- Each row contains digits 1-9 without repetition
- Each column contains digits 1-9 without repetition
- Each 3x3 box contains digits 1-9 without repetition

### Visual Indicators

- **Light Blue** - Currently selected cell
- **Yellow** - Cell being evaluated by the solver
- **Light Red** - Cells with conflicts/errors
- **Green Message** - Success (puzzle solved correctly)
- **Red Message** - Error (conflicts found or incomplete)
- **Blue Message** - Information (grid cleared, solving)

## Educational Solver Features

The Sudoku game includes two solving modes for learning about algorithms:

### Two Solving Modes

**Mode 1: Solve Algo (Animated Education)**
- Click "Solve Algo" to watch the algorithm step-by-step
- Shows real-time visualization of the backtracking process
- Side panel displays:
  - **Current Cell** - Which cell is being evaluated (row, col)
  - **Steps** - Total number of evaluation steps taken
  - **Backtracks** - How many times the algorithm had to backtrack
  - **Valid Candidates** - Numbers that can legally be placed in current cell
- Speed is adjustable during solving

**Mode 2: Solve Fast (Instant Solve)**
- Click "Solve Fast" to solve instantly without animation
- Completes in milliseconds
- Side panel shows final statistics:
  - **Steps** - Total steps the algorithm would have taken
  - **Backtracks** - Total backtracks needed
- Perfect when you want the answer immediately but still want to see algorithm complexity

### Solver Controls

**During animated solving (Solve Algo):**
- **SPACE** - Pause and resume the solving animation
- **UP Arrow** - Increase speed (faster animation)
- **DOWN Arrow** - Decrease speed (slower animation)
- **ESC** - Stop the solver completely

**After solving (both modes):**
- Click any button to close the final panel
- The panel displays:
  - Total steps taken
  - Number of backtracks
  - Valid candidates (if still animating)

### Understanding the Algorithm

The solver uses the **backtracking algorithm**:

1. Find an empty cell
2. Determine which numbers (1-9) are valid for that cell (no conflicts in row, column, or 3x3 box)
3. Try placing the first valid candidate
4. Recursively solve the rest of the puzzle
5. If no solution is found, backtrack (undo) and try the next candidate
6. Repeat until puzzle is solved or all possibilities exhausted

The animation helps visualize this process by:
- Highlighting the current cell being worked on (yellow)
- Showing valid candidates for that cell in the side panel
- Counting steps and backtracks
- Allowing you to pause and examine the algorithm state at any point

## Project Structure

```
sudoku/
├── src/
│   ├── constants.py                # Layout, colors, fonts, utilities (157 lines)
│   ├── solver.py                   # Pure algorithm logic (303 lines)
│   ├── ui.py                       # All UI rendering (450 lines)
│   ├── menu.py                     # Menu system & file I/O (176 lines)
│   └── sudoku_game.py              # Game orchestration (454 lines)
├── tests/
│   ├── test_solver.py              # Algorithm tests (28 tests)
│   ├── test_menu.py                # Menu system tests (30 tests)
│   └── README.md                   # Test documentation
├── test/ (legacy)
│   ├── test_*.py                   # Legacy test scripts
│   └── *.md                        # Legacy test docs
├── design/
│   ├── README.md                   # Design docs hub
│   ├── QUICK_START.md              # User guide
│   └── [design documentation]
├── sudoku-legacy/
│   ├── sudoku3.c                   # Original C solver (2006)
│   └── sudoku-legacy-analysis.md   # Comparative analysis
├── run.py                          # Launcher script
├── README.md                        # This file (user documentation)
├── CLAUDE.md                        # Project instructions
├── AGENTS.md                        # Agent and coding guidelines
├── pyproject.toml                   # Project metadata and dependencies
└── pyproject.lock                   # Locked dependencies
```

## Technical Details

### Architecture

The application uses a modular, layered architecture with clear separation of concerns:

**Layer 1: Foundation**
- `constants.py` - All visual constants, colors, fonts, layout utilities

**Layer 2: Algorithm (Testable, no Pygame)**
- `solver.py` - Pure algorithm logic
  - Sudoku validation (row, column, box constraints)
  - Backtracking solver (instant and step-by-step)
  - Puzzle generation with configurable difficulty
  - File I/O (save/load JSON)

**Layer 3: Menu System (Testable, no Pygame)**
- `menu.py` - Menu state and interaction handling
  - Menu open/close, hover state tracking
  - FILE menu (New Puzzle, Load, Save, Exit)
  - EDIT menu (Clear Grid)
  - Action-based interface for extensibility

**Layer 4: UI Rendering (Pygame)**
- `ui.py` - All visual rendering
  - Grid drawing with cell states and animations
  - Button rendering with hover effects
  - Menu dropdowns and submenus
  - Algorithm visualization panel
  - Message toasts

**Layer 5: Orchestration**
- `sudoku_game.py` - Game state and event coordination
  - Game loop management
  - Event handling (mouse, keyboard)
  - State management (grid, selected cell, errors, solver state)
  - Solver coordination

### Modularization Benefits

✅ **Testability** - Solver and menu have zero Pygame dependency, enabling fast unit tests (58 tests, 0.9s)
✅ **Reusability** - Solver can be used in CLI tools, web APIs, or other projects
✅ **Maintainability** - Each module has single responsibility
✅ **Extensibility** - Clean interfaces allow adding features without breaking existing code

### Key Components

1. **Grid Rendering** (ui.py)
   - 9x9 cell grid with 60px cells
   - Thick borders for 3x3 boxes
   - Dynamic cell highlighting and animations

2. **Validation System** (solver.py)
   - Real-time conflict detection
   - Comprehensive Sudoku rule checking
   - Valid candidate calculation

3. **Solver Algorithm** (solver.py)
   - Backtracking algorithm with step-by-step support
   - Efficient empty cell finding
   - Constraint satisfaction

### Color Scheme (Material Design)

**Grid**:
- Background: White (#FFFFFF)
- Cell borders (thin): Light Gray (#B4B4B4)
- Box borders (thick): Dark Blue (#193787)

**Cell States**:
- Selected: Light Blue (#96DCFF)
- Solving: Soft Yellow (#FFFAC8)
- Error: Soft Red (#FFC8C8)

**Buttons**:
- Finalize: Green (#4CAF50) → Hover: (#64C864)
- Clear: Red (#E53935) → Hover: (#FF646464)
- Solve Algo: Blue (#4285F4) → Hover: (#64A0FF)
- Solve Fast: Cyan (#00BCD4) → Hover: (#64DCFF)

**UI Elements**:
- Text Primary: Dark Gray (#424242)
- Text Subtle: Medium Gray (#9E9E9E)
- Panel Background: Light Gray (#F5F5F5)
- Panel Border: Medium Blue (#6496C8)

## Troubleshooting

### Pygame not found
If you get an import error for pygame:
```bash
pip install --upgrade pygame
```

### Window doesn't appear
Make sure you have a display available. On some systems, you may need to set:
```bash
export DISPLAY=:0
```

### Performance issues
The application runs at 60 FPS. If you experience lag:
- Close other applications
- Update your graphics drivers
- Ensure Python is not running in debug mode

## Completed Enhancements

✅ **Modular Architecture** - Clean separation of concerns (5 focused modules)
✅ **Comprehensive Test Suite** - 58 tests covering algorithm and menu (95%+ coverage)
✅ **Menu System** - FILE/EDIT menus with puzzle generation and file I/O
✅ **Puzzle Generator** - Random puzzle generation (Easy/Medium/Hard)
✅ **Save/Load Puzzles** - JSON-based persistence with metadata
✅ **Speed Controls** - UP/DOWN arrows to adjust solver animation speed
✅ **Visual Feedback** - Cell animations, progress bars, pulsing stats
✅ **Educational Solver** - Step-by-step visualization with algorithm metrics

## Possible Future Enhancements

- [ ] Timer and scoring system
- [ ] Hint system (suggest valid placements)
- [ ] Undo/Redo functionality
- [ ] Multiple color themes (light/dark mode)
- [ ] Difficulty analyzer (auto-detect puzzle difficulty)
- [ ] Puzzle database (library of famous puzzles)
- [ ] Web version (Tauri or web framework)

## Project Documentation Structure

```
C:\BOB\sudoku\
├── design/                          # Design & UI Documentation
│   ├── NAVIGATION_GUIDE.md          # Where to find everything
│   ├── README.md                    # Design overview
│   └── TEXT_SELECTION_NOTES.md      # UI technical notes
│
├── tests/procedures/                # Phase 5 Testing Documentation
│   ├── PHASE5_QUICK_START.txt       # 5-minute quick reference
│   ├── PHASE5_TESTING.md            # Detailed procedures (360+ lines)
│   ├── PHASE5_TESTING_RESULTS.md    # Results tracker
│   └── PHASE5_EXECUTION_SUMMARY.md  # Overview
│
├── docs/                            # Project Status & Reports
│   ├── PROJECT_STATUS.md            # Complete project report
│   └── README.md                    # Documentation index
│
├── src/                             # Source Code
│   ├── sudoku_game.py               # Main game logic
│   ├── ui.py                        # UI rendering
│   ├── solver.py                    # Solver algorithms
│   ├── menu.py                      # Menu system
│   └── constants.py                 # Constants and utilities
│
├── tests/                           # Test Suite (122 tests)
│   ├── test_*.py                    # Unit tests
│   ├── procedures/                  # Phase 5 testing docs
│   └── README.md                    # Testing overview
│
├── CLAUDE.md                        # Project instructions
├── AGENTS.md                        # Code style guidelines
└── README.md                        # This file
```

### Quick Links by Task

**I want to...**
- **Play the game**: Run `uv run src/sudoku_game.py` (see "How to Run" above)
- **Test Phase 5**: Start with [tests/procedures/PHASE5_QUICK_START.txt](./tests/procedures/PHASE5_QUICK_START.txt)
- **Understand design**: See [design/README.md](./design/README.md)
- **Check project status**: See [docs/PROJECT_STATUS.md](./docs/PROJECT_STATUS.md)
- **Find documentation**: See [design/NAVIGATION_GUIDE.md](./design/NAVIGATION_GUIDE.md)
- **Learn code guidelines**: See [AGENTS.md](./AGENTS.md)

## License

This project is open source and available for educational purposes.

## Author

Created as a Python Pygame demonstration project.

---

**Enjoy playing Sudoku!** 🎮