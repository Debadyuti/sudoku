# High Level Requirements for Sudoku Application

## Validation and Puzzle State
- "Finalize" button essentially need to validate and "finalize" sudoku grid based on below 3 lenses
  - If the puzzle entry is valid based on duplicate number check on same row, column and 3x3 grid (box)
  - If the puzzle is solvable (single or multiple solution exists)
  - If the puzzle has exactly one solution
- Based on above, below 4 types of decisions for `PUZZLE_STATE` (and corresponding message in toast)
  - RED: `INVALID`
  - RED: `NOT_SOLVABLE`
  - AMBER: `MULTIPLE_SOLUTIONS`
  - GREEN: `SINGLE_SOLUTION`
- Empty grid is special case of `MULTIPLE_SOLUTIONS`
- "Finalize" action means make the puzzle populated values has Greyed out/blue (ideally make these read-only unless "Clear" button is clicked)
- "Finalize" can only be done on AMBER or GREEN state puzzles, not RED states.

## System Generated Puzzles
- Generate puzzle for which only single solution exists
- Automatically make the puzzle "Finalize" - GREEN state
- For Easy, Mediam, Hard, refer design docs and label as per algorithmic complexity rather than clue count

## Solve Algo (A) button click
- Ideally start form "Finalize" puzzle state - GREEN or AMBER
- If the puzzle is neither "Finalize", nor RED puzzle state (user just making entries and click Solve), check "Finalize" button click functionality first before starting solution algorithm (freeze grid appropriately before solution algorithm starts)
- If puzzle is paused and resumed, there is a potential user might have changed the data and puzzle is NOT_SOLVABLE state, in that case consider only frozen rows, rest of the entries are free for backtracking retry.

## Solve Fast (F) button click
- Solve using default animation algo (chosen from the menu or system default when application starts)
- If the puzzle is neither "Finalize", nor RED puzzle state (user just making entries and click Solve), check "Finalize" button click functionality first before starting solution algorithm (freeze grid appropriately before solution algorithm starts)
- If Solve Algo is clicked and paused, it's possible that puzzle is in NOT_SOLVABLE state. In that case consider only frozen rows and allow algorithm to perform backtrack retry on rest of the entries (instead of showing INVALID puzzle)

## Clear button click
- Reset grid entirely including frozen puzzle grid
- Don't reset Algorithm choice, let it be user chosen values (refer Algorithm menu)

## Puzzle Solution Algorithms
### DANCING LINKS (Algorithm X)
- Most efficient, use for system solution for puzzle generation and validation
- It will be evaluated later for animation candidate (not animation candidate yet)
### HYBRID (Constraint Prop + Heuristics)
- Closer to most efficient, primary candidate for animation (system default for Algorithm menu) - top choice for Algorithm menu (new menu for Animation choice)
### CONSTRAINT PROPAGATION (AC-3)
- Next option in Algorithm menu (2nd)
### BACKTRACK + MRV
- Next option in Algorithm menu (3rd)
### NAIVE BACKTRACKING
- Next option in Algorithm menu (4th)

## Algorithm menu (NEW)
- Create a menu of available algorithms listed above (only provide Animation algorithms with priority mentioned above)
- Make 1st Algorithm as system default during application startup, however, user can choose and ticket any menu item from Algorithm choices
- As long as the app is opened, keep user's algorithm choice active
- Algorithm choice from menu will drive Solve Algo (A) and Solve Fast (F) button click.

## File menu
### New (CTRL+N)
- Create this as first option for new empty grid puzzle (different from New Puzzle)
### Exit
- Ensure this menu is working (closing the application)

## VIEW menu (NEW)
- Create Algorithm Statistics item
- Show error message if puzzle state is RED
- Show statistics for other puzzle state as per below
- Clicking "Algorithm Statistics" will show below statistics for every algorithm in a grid (irrespective of Algorithm menu choice)
  - Algo Name (provide all algo - including DANCING LINKS)
  - Step count
  - Backtrack count
  - Time complexity (instead of showing exact time in ms, is there a time complexity for specific puzzle grid as ms time depends on hardware etc.)
  - Memory (space) Complexity