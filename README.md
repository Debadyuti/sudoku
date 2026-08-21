# Sudoku Game - Python Pygame Application

A fully-featured Sudoku game built with Python and Pygame, featuring a clean UI, user input validation, error highlighting, and an automatic solver.

## Features

✅ **Blank 9x9 Grid** - Start with an empty Sudoku grid  
✅ **Interactive Cell Selection** - Click to select cells with visual highlighting  
✅ **Number Entry** - Type numbers 1-9 to fill cells  
✅ **Finalize Button** - Validates your completed puzzle  
✅ **Clear Button** - Reset the entire grid to start over  
✅ **Solve Button** - Automatically solves the puzzle using backtracking algorithm  
✅ **Error Highlighting** - Invalid entries are highlighted in red  
✅ **Visual Feedback** - Success and error messages displayed  
✅ **Intuitive Controls** - Mouse and keyboard support  

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
python sudoku_game.py
```

Or with uv:
```bash
uv run python sudoku_game.py
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

### Buttons

1. **Finalize** (Green)
   - Validates your completed puzzle
   - Shows success message if correct
   - Highlights errors in red if there are conflicts

2. **Clear** (Red)
   - Clears the entire grid
   - Resets all cells to empty

3. **Solve** (Blue)
   - Automatically solves the current puzzle
   - Uses backtracking algorithm
   - Shows "No solution exists!" if puzzle is unsolvable

### Game Rules

A valid Sudoku puzzle must satisfy:
- Each row contains digits 1-9 without repetition
- Each column contains digits 1-9 without repetition
- Each 3x3 box contains digits 1-9 without repetition

### Visual Indicators

- **Light Blue** - Currently selected cell
- **Light Red** - Cells with conflicts/errors
- **Green Message** - Success (puzzle solved correctly)
- **Red Message** - Error (conflicts found or incomplete)
- **Blue Message** - Information (grid cleared, solving)

## Application Structure

```
sudoku/
├── sudoku_game.py      # Main application file
├── requirements.txt    # Python dependencies
└── README.md          # This file
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

### Color Scheme

- Grid Background: White
- Grid Lines: Black (thick for boxes, thin for cells)
- Selected Cell: Light Blue (#ADD8E6)
- Error Cells: Light Red (#FFB6C1)
- Finalize Button: Green (#228B22)
- Clear Button: Red (#DC143C)
- Solve Button: Blue (#1E90FF)

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