# Sudoku Solver Algorithms & Complexity Analysis

**Status**: Algorithm selection for Phase 7+ implementation  
**Focus**: Understanding trade-offs between human learning value vs. computational efficiency

---

## Quick Comparison

| Algorithm | Time to Solve | Backtracks | Human Value | Complexity |
|-----------|--------------|-----------|-------------|-----------|
| **Naive Backtrack** | 200-1000ms | 1000-50,000 | ⭐ Very High | ⭐ Simple |
| **Backtrack + MRV** | 50-500ms | 100-5,000 | ⭐ Very High | ⭐⭐ Moderate |
| **Constraint Prop (AC-3)** | 10-100ms | 10-500 | ⭐⭐⭐ Excellent | ⭐⭐⭐ Complex |
| **Hybrid (Constraint + Heuristics)** | 5-50ms | 5-100 | ⭐⭐⭐⭐ Outstanding | ⭐⭐⭐⭐ Very Complex |
| **Dancing Links (Algorithm X)** | 1-10ms | N/A (no backtrack) | ⭐⭐ Good | ⭐⭐⭐⭐⭐ Very Complex |

---

## Algorithm 1: Naive Backtracking

### How It Works

```
def solve(grid):
    find first empty cell (0)
    
    for each number 1-9:
        if valid placement:
            place number
            recursively solve rest
            if successful: return
            remove number (backtrack)
    
    return failure
```

### Concrete Example

```
Grid:
[1][ ][3]
[ ][5][ ]
[7][ ][9]

Step 1: Find empty cell [0][1]
Step 2: Try 1-9
  Try 1: [1][1][3] / [ ][5][ ] / [7][ ][9] → Check validity
  Try 2: [1][2][3] / [ ][5][ ] / [7][ ][9] → Check validity
  ...
  Try 4: Valid placement → Recurse
  Continue solving...
  If stuck: Backtrack, try 5
  ...
  Try 8: Valid → Success? Or backtrack again
  
Result: May take many attempts
```

### Performance

- **Time Complexity**: O(9^m) where m = empty cells (pessimal)
- **Space Complexity**: O(m) recursion depth
- **Actual Performance**: 200-1000ms for medium puzzle
- **Backtrack Count**: 1,000-50,000 for sparse puzzles

### Why It Fails on Sparse Puzzles

```
Puzzle: 15 clues scattered
┌─ Naive solver scans left-to-right
├─ Finds row 1 mostly empty
├─ For [1][0]: tries 9 candidates
├─ For [1][1]: tries up to 8 more
├─ For [1][2]: tries more candidates
└─ Combinatorial explosion: 9×8×7×... = billions of paths

At row 3 (completely empty): 9^9 possible combinations to explore
Result: 42,000+ backtracks for "easy" puzzle
```

### Example Code (Current Implementation)

```python
def solve_backtrack(self):
    """Naive backtracking solver"""
    empty = self.find_empty_cell()  # Scans left-to-right
    if not empty:
        return True  # Solved
    
    row, col = empty
    for num in range(1, 10):  # Try 1-9 in order
        if self.is_valid_placement(row, col, num):
            self.grid[row][col] = num
            if self.solve_backtrack():
                return True
            self.grid[row][col] = 0  # Backtrack
    
    return False
```

### Human Learning Value

✅ **Very High**
- Easy to visualize: Watch solver try numbers and backtrack
- Shows clear "guess and check" process
- Student can see exactly why each attempt failed
- Perfect for animation (cell fills, then flashes red)

### When to Use

- Educational scenarios (students learning algorithm)
- Animation/visualization (shows step-by-step)
- Puzzles with good distribution of clues
- CPU not a constraint

---

## Algorithm 2: Backtrack + MRV (Minimum Remaining Values)

### How It Works

**Key Insight**: Choose cell with FEWEST candidates first (prunes search tree)

```
def solve_mrv(grid):
    find cell with MINIMUM remaining candidates (not first empty!)
    
    for each candidate of that cell:
        place candidate
        recursively solve
        if successful: return
        remove candidate (backtrack)
    
    return failure
```

### Why MRV Works

```
Example: Multiple choices at cell selection

Naive approach:
├─ Finds [0][0] (has 9 candidates)
├─ Tries [0][0] = 1,2,3,4,5,6,7,8,9
└─ Search tree: 9 × 8 × 7 × ... = huge

MRV approach:
├─ Scans ALL empty cells
├─ Finds [4][5] (has only 2 candidates: 5, 7)
├─ Tries [4][5] = 5 first
├─ Tries [4][5] = 7 second
└─ Search tree: 2 × ... = much smaller!

Effect: Reduces branching factor dramatically
```

### Performance

- **Time Complexity**: Still O(9^m) worst case, but much smaller average
- **Space Complexity**: O(m) same as naive
- **Actual Performance**: 50-500ms for medium puzzle
- **Backtrack Count**: 100-5,000 for same puzzle
- **Improvement**: 10-50x faster than naive for hard puzzles

### Example Code

```python
def solve_with_mrv(self):
    """Backtrack with Minimum Remaining Values heuristic"""
    # Find cell with fewest candidates (not first empty)
    best_cell = None
    min_candidates = 10
    
    for i in range(9):
        for j in range(9):
            if self.grid[i][j] == 0:
                candidates = self.get_candidates(i, j)
                if len(candidates) < min_candidates:
                    min_candidates = len(candidates)
                    best_cell = (i, j, candidates)
                    
                    if min_candidates == 1:  # Can't do better
                        break
    
    if best_cell is None:  # No empty cells
        return True  # Solved
    
    row, col, candidates = best_cell
    
    for num in candidates:  # Only try valid numbers
        self.grid[row][col] = num
        if self.solve_with_mrv():
            return True
        self.grid[row][col] = 0
    
    return False
```

### Human Learning Value

✅ **Very High**
- Shows intelligent search: Why cell picked matters
- Demonstrates heuristic thinking
- Still easy to visualize and animate
- Students learn optimization principles

### When to Use

- Educational + performance improvement needed
- Puzzles with varying clue distribution
- Still want clear backtracking visualization
- Current recommended approach for Phase 6

---

## Algorithm 3: Backtrack + Constraint Propagation (AC-3)

### How It Works

**Key Insight**: Before guessing, eliminate impossible candidates through logical deduction

```
Algorithm:
1. For each empty cell, maintain SET of possible candidates
2. Before trying candidates:
   a. If cell has 1 candidate → assign it (naked single)
   b. If number can only go in 1 cell of row → assign it (hidden single)
   c. Remove candidate from peers
   d. Repeat until no more deductions possible
3. THEN use backtrack on reduced search space
```

### Concrete Example

```
Initial puzzle:
[1][ ][3]
[ ][5][ ]
[7][ ][9]

Step 1: Initialize domains (candidates for each cell)
[1]{fixed}  [ ]{2,4,6,8}  [3]{fixed}
[ ]{2,4,6,8}  [5]{fixed}  [ ]{2,4,6,8}
[7]{fixed}  [ ]{2,4,6,8}  [9]{fixed}

Step 2: Apply constraint propagation
Rule: Number already in row → remove from other cells in row
Row 0 has 1,3 → remove 1,3 from [0][1]
[0][1] now: {2,4,6,8}

Rule: Naked single (1 candidate left)
[0][1] has only {2}? No, still multiple...

Rule: Check columns
Col 0 has 1,7 → remove from [1][0]
[1][0] now: {2,4,6,8}

Continue propagating until stabilized...

Step 3: Cell [0][1] now has reduced candidates {2,4,6,8}
Instead of trying 1-9, only try 4 options
Backtrack count reduced 50%+
```

### AC-3 Algorithm Details

```
def ac3_propagate(domains):
    """Arc Consistency 3 algorithm"""
    queue = [(i, j) for i in range(9) for j in range(9)]
    
    while queue:
        xi, xj = queue.pop(0)
        
        if revise(domains, xi, xj):  # Domains changed
            if len(domains[xi][xj]) == 0:
                return False  # Contradiction found
            
            # Add neighbors to queue
            for neighbor in get_peers(xi, xj):
                if neighbor != (xi, xj):
                    queue.append(neighbor)
    
    return True  # Consistent

def revise(domains, xi, xj):
    """Check if domain of xi consistent with xj"""
    revised = False
    
    for x in list(domains[xi][xj]):
        # If no value in xj is consistent with x
        if not any(value != x and value in domains[xj][neighbor] 
                   for neighbor in [xj]):
            domains[xi][xj].remove(x)
            revised = True
    
    return revised
```

### Performance

- **Time Complexity**: O(n^3 × d^5) for AC-3, then backtrack on reduced space
- **Space Complexity**: O(n × d) where n=81 cells, d=9 candidates per cell
- **Actual Performance**: 10-100ms for medium puzzle
- **Backtrack Count**: 10-500 for same puzzle
- **Improvement**: 100-500x faster than naive

### Example Code for Your Game

```python
def solve_with_constraint_propagation(self):
    """Backtrack + AC-3 constraint propagation"""
    
    # Initialize domains
    domains = [[set(range(1, 10)) for _ in range(9)] for _ in range(9)]
    
    # Remove fixed values
    for i in range(9):
        for j in range(9):
            if self.grid[i][j] != 0:
                domains[i][j] = {self.grid[i][j]}
    
    # Propagate constraints
    if not self.propagate(domains):
        return False  # Unsolvable
    
    # Now use backtrack with reduced domains
    return self.solve_with_domains(domains)

def propagate(self, domains):
    """Constraint propagation"""
    changed = True
    
    while changed:
        changed = False
        
        # Naked singles: cell with 1 candidate
        for i in range(9):
            for j in range(9):
                if len(domains[i][j]) == 1:
                    value = list(domains[i][j])[0]
                    # Remove from peers
                    for peer in self.get_peers(i, j):
                        if value in domains[peer[0]][peer[1]]:
                            domains[peer[0]][peer[1]].remove(value)
                            changed = True
        
        # Hidden singles: value can only go in 1 cell
        # ... implement similar logic
    
    return True  # Consistent
```

### Human Learning Value

✅ **Excellent**
- Shows logical deduction: How constraints narrow possibilities
- Demonstrates "constraint satisfaction" concept
- Can highlight which constraints fired (educational)
- Still visual: See candidates reduce before guessing

### When to Use

- Want better performance + educational value
- Can handle slightly complex code
- Want to teach constraint satisfaction problems
- Recommended for Phase 7+

---

## Algorithm 4: Backtrack + Constraint Propagation + Heuristics

### How It Works

**Key Insight**: Constraint Propagation + multiple deduction rules + MRV selection

Combines:
1. **AC-3 Constraint Propagation** (eliminate impossible candidates)
2. **Multiple Deduction Rules**:
   - Naked singles (1 candidate in cell)
   - Hidden singles (number fits in 1 cell only)
   - Pointing pairs (if number in box limited to row, remove from rest of row)
   - Box/line reduction (similar)
   - Naked pairs/triples (multiple cells have same small set)
   - X-wing, Swordfish, etc.
3. **MRV Heuristic** (pick cell with fewest candidates)

### Performance

- **Time Complexity**: O(n × d^4) constraint checking + backtrack
- **Space Complexity**: O(n × d)
- **Actual Performance**: 5-50ms for medium puzzle
- **Backtrack Count**: 5-100 for same puzzle
- **Improvement**: 1000x+ faster than naive

### Practical Impact

```
Hard puzzle (normally 10,000+ backtracks):

Naive backtrack:
├─ 10,000+ backtracks
├─ 500ms solving time
└─ Many cells tried randomly

Hybrid (Constraint Prop + Heuristics):
├─ 20 backtracks
├─ 20ms solving time
└─ Most cells solved by logic!
```

### Example Implementation (Simplified)

```python
def solve_hybrid(self):
    """Hybrid: constraint propagation + heuristics + backtrack"""
    
    domains = self.initialize_domains()
    
    # Step 1: Maximum constraint propagation
    if not self.apply_all_rules(domains):
        return False  # Unsolvable
    
    # Step 2: If solved, great!
    if self.is_solved(domains):
        self.apply_solution(domains)
        return True
    
    # Step 3: Only backtrack if needed
    return self.solve_with_backtrack(domains)

def apply_all_rules(self, domains):
    """Apply all deduction rules"""
    changed = True
    
    while changed:
        changed = False
        
        # Naked singles
        changed |= self.apply_naked_singles(domains)
        
        # Hidden singles
        changed |= self.apply_hidden_singles(domains)
        
        # Pointing pairs
        changed |= self.apply_pointing_pairs(domains)
        
        # More rules...
    
    return True  # Consistent

def solve_with_backtrack(self, domains):
    """Backtrack only needed for hard puzzles"""
    
    # Find cell with fewest candidates (MRV)
    cell = self.find_mrv_cell(domains)
    
    if cell is None:
        return self.is_solved(domains)
    
    row, col = cell
    
    for value in list(domains[row][col]):
        # Try this value
        domains_copy = self.copy_domains(domains)
        domains_copy[row][col] = {value}
        
        if self.propagate(domains_copy) and self.solve_with_backtrack(domains_copy):
            domains.update(domains_copy)
            return True
    
    return False
```

### Human Learning Value

✅ **Outstanding**
- Shows multiple solving techniques: Logical deduction at work
- Educational: How humans solve Sudoku (not just guessing)
- Can highlight WHICH rule fired (very educational)
- Animation: Show each rule application
- Students learn multiple problem-solving strategies

### When to Use

- Want to teach how humans solve Sudoku
- Performance critical + educational value both matter
- Willing to implement complex rules
- Recommended for Phase 7+ final implementation

---

## Algorithm 5: Dancing Links (Algorithm X)

### How It Works

**Key Insight**: Convert Sudoku to "Exact Cover" problem, solve with dancing links data structure

### Part 1: Problem Formulation

```
Sudoku constraints can be framed as:
"Find a set of (cell, number) pairs that satisfy all constraints"

Example:
- Cell (0,0) must contain exactly 1 number (1-9)
- Row 0 must contain each number (1-9) exactly once
- Column 0 must contain each number (1-9) exactly once
- Box (0,0-0,2) must contain each number (1-9) exactly once

This is an "Exact Cover" problem:
- Universe: All constraints
- Find subset of options (cell-number pairs) that cover each constraint exactly once
```

### Part 2: Matrix Representation

```
Constraint matrix (simplified for 4x4 Sudoku):

                 R1  R2  C1  C2  B1
(R1,1)           1   0   1   0   1
(R1,2)           1   0   0   1   1
(R1,3)           1   0   0   0   0
(R1,4)           1   0   0   0   0
(R2,1)           0   1   1   0   0
(R2,2)           0   1   0   1   0
...

Rows = all possible (cell, number) placements
Columns = all constraints
1 = placement satisfies constraint

Goal: Select rows such that each column has exactly 1 selected row
```

### Part 3: Dancing Links Algorithm

```
def solve_dancing_links():
    # Build sparse matrix (efficient representation)
    matrix = build_constraint_matrix()
    
    def search(depth):
        if matrix is empty:
            return solution found  # All constraints covered
        
        # Choose column with fewest 1s (most constrained)
        column = choose_column_with_fewest_ones(matrix)
        
        # Try each row that covers this column
        for row in rows_covering(column):
            # "Select" this row
            remove_row_and_covered_columns(matrix, row)
            
            # Recurse
            if search(depth + 1):
                return True
            
            # "Unselect" this row (restore matrix)
            restore_row_and_columns(matrix, row)
        
        return False  # Backtrack
    
    return search(0)
```

### Part 4: Data Structure (Dancing Links)

```
Normal matrix: Hard to remove/restore columns

Dancing Links: Doubly-linked lists
- Each 1 in matrix is a node
- Nodes point to each other (up/down/left/right)
- Removing: Break links
- Restoring: Restore links (super fast!)

Visual:
Before removing:
... ← col_header → [1] ← row_header → [1] → ...

After removing column:
... ← next_col ← col_header removed → prev_col → ...
    Nodes still in memory, just unlinked!

To restore: Re-establish links (O(1) operation!)
```

### Performance

- **Time Complexity**: O(2^n) worst case, but massive pruning in practice
- **Actual Performance**: 1-10ms for ANY puzzle (even hardest)
- **Backtrack Count**: N/A (no traditional backtracking)
- **Coverage**: 100% - can solve any valid Sudoku
- **Speed**: 50-100x faster than hybrid for hard puzzles

### Why It's Fast

```
Traditional backtrack:
- Try cell [0][0], then [0][1], then [0][2]...
- Each choice expands search tree

Dancing Links:
- Choose most constrained column first
- Each choice collapses search tree dramatically
- Early detection of contradictions
```

### Example: Why Dancing Links Wins

```
Hard puzzle (normally):
Naive backtrack: 50,000 steps
Hybrid: 500 steps
Dancing Links: 50 steps

Why? Because dancing links intelligently picks constraints
that eliminate huge swaths of the search space early
```

### Code Complexity

```python
# Simplified version (full version ~300 lines)

class Node:
    def __init__(self):
        self.up = self.down = self.left = self.right = self
        self.column = None
        self.row_id = None

class ColumnHeader(Node):
    def __init__(self):
        super().__init__()
        self.size = 0

def cover(column):
    """Remove column and all rows containing it"""
    column.right.left = column.left
    column.left.right = column.right
    
    i = column.down
    while i != column:
        j = i.right
        while j != i:
            j.down.up = j.up
            j.up.down = j.down
            j.column.size -= 1
            j = j.right
        i = i.down

def uncover(column):
    """Restore column (reverse of cover)"""
    i = column.up
    while i != column:
        j = i.left
        while j != i:
            j.column.size += 1
            j.down.up = j
            j.up.down = j
            j = j.left
        i = i.up
    
    column.right.left = column
    column.left.right = column

def search(k, solution):
    """Recursive search with dancing links"""
    if header.right == header:
        return True  # All constraints satisfied
    
    # Choose column with minimum size
    column = choose_column()
    cover(column)
    
    i = column.down
    while i != column:
        solution.append(i.row_id)
        
        j = i.right
        while j != i:
            cover(j.column)
            j = j.right
        
        if search(k + 1, solution):
            return True
        
        # Backtrack
        solution.pop()
        j = i.left
        while j != i:
            uncover(j.column)
            j = j.left
        
        i = i.down
    
    uncover(column)
    return False
```

### Visualization: Why Dancing Links is Elegant

```
Traditional recursive backtrack:
├─ Pick cell randomly
├─ Try 1-9
├─ Deep recursion tree
└─ Many branches explored before contradiction found

Dancing Links:
├─ Pick most constrained column (smartest choice)
├─ Very few options to try
├─ Contradictions detected early
├─ Remove large branches from consideration
└─ Solution found in minimal steps
```

### Human Learning Value

⭐ **Good but Limited**
- Very hard to visualize (matrix operations, link manipulation)
- Not how humans solve Sudoku
- More theoretical than practical for learning
- Excellent for understanding constraint satisfaction
- Poor for animation/step-by-step visualization

### When to Use

- Need absolute best performance (1-10ms any puzzle)
- Not focused on visualization
- Solving known-difficult puzzles
- Research/competition Sudoku
- Backend solver (user doesn't see steps)

---

## Recommendation for Your Game

### Phase 6 (Current): Keep Naive Backtrack + MRV

**Why:**
- ✅ Current code works well
- ✅ 50-500ms is acceptable
- ✅ Great for visualization (clear backtracking)
- ✅ Students see guessing + backtracking clearly

### Phase 7 Improvement: Add Constraint Propagation

**Why:**
- ✅ 10-100x performance improvement
- ✅ Still very visualizable (show constraint rules firing)
- ✅ Educational: Multiple solving strategies
- ✅ Moderate code complexity (~100 lines)
- ✅ Balance performance + learning value

### Phase 8+ (Future): Optional Dancing Links Backend

**Why:**
- ✅ For "instant solve" feature (not step-by-step)
- ✅ Keep constraint prop for visualization
- ✅ Use dancing links for "fast" solve
- ✅ Users choose: watch solving steps vs. instant answer

---

## My Recommendation for YOU

**For your game's educational value: Hybrid (Constraint Prop + Heuristics)**

Why:
1. **Perfect for learning**: Shows multiple solving techniques
2. **Still fast enough**: 5-50ms per puzzle
3. **Highly visualizable**: Can highlight which rule fired
4. **Sweet spot**: Performance + education balance

```
Learning Journey:
├─ Naive Backtrack (Phase 1-5): Understand basic algorithm
├─ Backtrack + MRV (Phase 6): Learn heuristics
├─ Constraint Prop (Phase 7): Learn deduction rules
├─ Hybrid (Phase 7-8): Combine everything (RECOMMENDED)
└─ Dancing Links (Optional): See industrial solver
```

### Implementation Priority

```
Phase 7.1: Add Constraint Propagation (AC-3)
├─ Naked singles rule
├─ Hidden singles rule
├─ Propagate constraints before backtrack

Phase 7.2: Add More Heuristics
├─ Pointing pairs
├─ Box/line reduction
├─ Optional: Naked pairs

Phase 7.3: MRV Selection (already partially done)

Phase 8+: Optional Dancing Links
└─ For "instant solve" feature
```

---

## Difficulty Classification (Using These Algorithms)

Once you implement, you can classify puzzles properly:

```python
def calculate_true_difficulty(puzzle):
    """Use algorithm performance to measure difficulty"""
    
    # Solve with naive backtrack
    naive_backtracks = solve_naive(puzzle)
    
    # Solve with MRV
    mrv_backtracks = solve_mrv(puzzle)
    
    # Solve with constraint prop
    hybrid_backtracks = solve_hybrid(puzzle)
    
    # Classify
    if hybrid_backtracks <= 5:
        return "Easy"  # Mostly solvable by logic
    elif hybrid_backtracks <= 20:
        return "Medium"  # Some guessing needed
    else:
        return "Hard"  # Lots of guessing
    
    # Show user both metrics
    return {
        "difficulty": difficulty,
        "backtracks_naive": naive_backtracks,
        "backtracks_mrv": mrv_backtracks,
        "backtracks_hybrid": hybrid_backtracks
    }
```

---

## Algorithm Selection Matrix

Choose based on your priorities:

| Goal | Algorithm |
|------|-----------|
| **Learning (students)** | Hybrid (Constraint Prop + Heuristics) |
| **Balanced** | Backtrack + Constraint Propagation |
| **Pure performance** | Dancing Links |
| **Simple + fast** | Backtrack + MRV |
| **Simple + educational** | Naive Backtrack |

---

**Next Steps:**

1. ✅ Choose algorithm for Phase 7
2. ⏳ Implement constraint propagation rules
3. ⏳ Integrate with current backtracking solver
4. ⏳ Test and measure performance improvements
5. ⏳ Update UI to visualize constraint rules (optional)

---

**Document Created**: 2026-08-21  
**For**: Phase 7+ algorithm selection and implementation
