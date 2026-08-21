# Sudoku Game - Python Pygame Application

A fully-featured Sudoku game built with Python and Pygame, featuring a modern UI with smooth animations, user input validation, error highlighting, and an educational algorithm visualizer.

📚 **Complete Documentation**: See [design/README.md](./design/README.md) for detailed design docs, user guides, and algorithm analysis.

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
│   └── sudoku_game.py              # Main application (1,081 lines)
├── test/
│   ├── test_*.py                   # Test scripts
│   ├── *_FIX.md                    # Debug and fix documentation
│   └── *_test.md                   # Test documentation
├── design/
│   ├── README.md                   # Design docs hub
│   ├── QUICK_START.md              # User guide
│   ├── MENU_SYSTEM_IMPLEMENTATION.md
│   └── [other design docs]
├── sudoku-legacy/
│   ├── sudoku3.c                   # Original C solver (2006)
│   └── sudoku-legacy-analysis.md   # Comparative analysis
├── run.py                          # Launcher script
├── README.md                        # This file (user documentation)
├── CLAUDE.md                        # Redirect to AGENTS.md
├── AGENTS.md                        # Agent and coding instructions
├── pyproject.toml                   # Project metadata and dependencies
└── pyproject.lock                   # Locked dependencies
```

## Technical Details

### Architecture

The application is built using object-oriented programming with a single `SudokuGame` class that manages:
- Game state (grid, selected cell, errors)
- UI rendering (grid, buttons, messages)
- Event handling (mouse clicks, keyboard input)
- Validation logic (row, column, box checking)
- Solver algorithm (backtracking)

### Key Components

1. **Grid Rendering**
   - 9x9 cell grid with 60px cells
   - Thick borders for 3x3 boxes
   - Dynamic cell highlighting

2. **Validation System**
   - Real-time conflict detection
   - Comprehensive error checking
   - Visual error feedback

3. **Solver Algorithm**
   - Backtracking algorithm
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

## Future Enhancements

Possible features for future versions:
- Difficulty levels (Easy, Medium, Hard)
- Puzzle generator
- Timer and scoring system
- Hint system
- Undo/Redo functionality
- Save/Load puzzles
- Multiple color themes

## License

This project is open source and available for educational purposes.

## Author

Created as a Python Pygame demonstration project.

---

**Enjoy playing Sudoku!** 🎮