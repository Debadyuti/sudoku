# Project Organization Guide

## Folder Structure Convention

This project follows a clean, organized folder structure to keep code, tests, and documentation separate and easy to maintain.

```
sudoku/
├── src/                          # Production source code
│   └── sudoku_game.py            # Main application (1,081 lines)
│
├── test/                         # Test files and debug documentation
│   ├── test_grid_fix.py          # Grid positioning test
│   ├── test_submenu_hover.py     # Submenu hover logic test
│   ├── FIX_UI_OVERLAY_ISSUE.md   # UI overlay bug fix documentation
│   ├── TEST_MENU_LAYERING.md     # Menu layering test documentation
│   ├── SUBMENU_IMPLEMENTATION.md # Submenu implementation details
│   ├── SUBMENU_HOVER_FIX.md      # Submenu hover fix documentation
│   └── MENU_FIXES_COMPLETE.md    # Complete menu fix summary
│
├── design/                       # Design and architectural documentation
│   ├── README.md                 # Design documentation hub
│   ├── QUICK_START.md            # User-friendly quick start guide
│   ├── QUICK_START_v3.md         # v3.0 features quick start
│   ├── MENU_SYSTEM_IMPLEMENTATION.md
│   ├── ENHANCEMENT_COMPLETION_SUMMARY.md
│   ├── UI_ENHANCEMENT_LOG.md
│   ├── QUICK_FIXES_LOG.md
│   ├── CLEANUP_LOG.md
│   └── ENHANCEMENT_LOG.md
│
├── sudoku-legacy/                # Legacy code and historical analysis
│   ├── sudoku3.c                 # Original C solver (2006)
│   └── sudoku-legacy-analysis.md # Comparative algorithm analysis
│
├── run.py                        # Entry point launcher script
├── README.md                     # User documentation (what to play)
├── CLAUDE.md                     # Project instructions (points to AGENTS.md)
├── AGENTS.md                     # Agent coding standards and conventions
├── PROJECT_ORGANIZATION.md       # This file
├── pyproject.toml                # Project metadata and dependencies
├── pyproject.lock                # Locked dependency versions
└── .gitignore                    # Git configuration

```

---

## Folder Purposes

### `src/` - Production Source Code

**Contains**: All production code that runs the application.

**Files**:
- `sudoku_game.py` - Main Sudoku game application
  - Pygame-based GUI
  - Game state management
  - UI rendering
  - Event handling
  - Solver algorithm

**Rules**:
- ✅ Place all application code here
- ✅ Import from `src/` in other modules
- ❌ Don't put test code here
- ❌ Don't put debug scripts here
- ❌ Don't put temporary files here

**Running**:
```bash
python run.py
# or with uv
uv run python run.py
```

---

### `test/` - Test Files and Debug Documentation

**Contains**: Test scripts, debug utilities, and debug-related documentation.

**Subdirectories**:
- Test scripts: `test_*.py`
- Test documentation: `*_test.md`
- Bug fix documentation: `*_FIX.md`
- Temporary debug output: `debug_logs/`

**Examples**:
- `test_grid_fix.py` - Verify grid positioning constants
- `test_submenu_hover.py` - Test submenu hover logic
- `FIX_UI_OVERLAY_ISSUE.md` - Documentation of UI overlay bug and fix
- `SUBMENU_HOVER_FIX.md` - Documentation of submenu hover issue and fix

**Rules**:
- ✅ Place all test scripts here
- ✅ Place debug documentation here (`*_test.md`, `*_FIX.md`)
- ✅ Place temporary test data here
- ✅ Place debug logs here
- ❌ Don't put permanent user documentation here
- ❌ Don't put architectural docs here
- ❌ Don't put design specs here

**Running Tests**:
```bash
python test/test_grid_fix.py
python test/test_submenu_hover.py
```

---

### `design/` - Design and Architectural Documentation

**Contains**: All design specs, architectural decisions, user guides, and enhancement logs.

**Key Files**:
- `README.md` - Design documentation hub (start here!)
- `QUICK_START.md` - User-friendly guide for playing
- `MENU_SYSTEM_IMPLEMENTATION.md` - Menu system technical specs
- `ENHANCEMENT_COMPLETION_SUMMARY.md` - Full architecture overview
- Enhancement logs - History of changes and improvements

**Rules**:
- ✅ Place all design documentation here
- ✅ Place user guides and quick starts here
- ✅ Place feature specifications here
- ✅ Place architectural decisions here
- ✅ Place enhancement logs here
- ❌ Don't put source code here
- ❌ Don't put test scripts here
- ❌ Don't put debug documentation here

**When to Add**:
- New feature specification → `design/`
- Implementation guide → `design/`
- User guide → `design/`
- Enhancement log → `design/`

---

### `sudoku-legacy/` - Legacy Code and Analysis

**Contains**: Original code from 20+ years ago and comparative analysis.

**Files**:
- `sudoku3.c` - Original C-based Sudoku solver (circa 2006)
- `sudoku-legacy-analysis.md` - Comparative analysis vs modern implementation

**Purpose**:
- Historical reference
- Algorithm comparison
- Understanding evolution of the codebase

**Rules**:
- ✅ Keep legacy code as-is (for reference)
- ✅ Document analysis and comparisons
- ❌ Don't modify legacy code
- ❌ Don't use legacy code in current app

---

### Root Level - Critical Files Only

**Contains**: Only essential project files needed at the root.

**Files**:
- `README.md` - User documentation (how to play)
- `CLAUDE.md` - Points to `AGENTS.md`
- `AGENTS.md` - Coding standards and agent instructions
- `PROJECT_ORGANIZATION.md` - This file
- `run.py` - Entry point launcher
- `pyproject.toml` - Project metadata
- `pyproject.lock` - Locked dependencies

**Rules**:
- ✅ Keep only critical files at root
- ✅ Move all source code to `src/`
- ✅ Move all tests to `test/`
- ✅ Move all design docs to `design/`
- ❌ Don't clutter root with multiple Python files
- ❌ Don't put temp files at root

---

## File Naming Conventions

### Source Code (`src/`)
```
sudoku_game.py              # Main application
utility_functions.py        # Helper utilities (if needed)
[feature]_module.py         # Feature-specific modules
```

### Test Files (`test/`)
```
test_*.py                   # Test scripts
*_test.md                   # Test documentation
*_FIX.md                    # Bug fix documentation
```

### Design Documentation (`design/`)
```
QUICK_START.md              # User guide
[FEATURE]_IMPLEMENTATION.md # Technical implementation
[FEATURE]_LOG.md            # Enhancement log
README.md                   # Documentation hub
```

---

## How to Add New Files

### Adding Source Code
1. Place in `src/` folder
2. Name: `feature_name.py`
3. Update imports in `run.py` or `sudoku_game.py` if needed
4. Update `AGENTS.md` if it's a significant new module

### Adding Tests
1. Place in `test/` folder
2. Name: `test_feature_name.py`
3. Document in `test/test_feature_name.md` if complex
4. Run: `python test/test_feature_name.py`

### Adding Design Documentation
1. Place in `design/` folder
2. Name: `FEATURE_NAME.md` or `FEATURE_LOG.md`
3. Link from `design/README.md`
4. Update main documentation if user-facing

### Adding Debug/Fix Documentation
1. Place in `test/` folder (not `design/`)
2. Name: `FEATURE_FIX.md` or `FEATURE_test.md`
3. Include in test summary if relevant
4. Move to archive after issue resolved

---

## Directory Commands

### Create New Test
```bash
cd C:\BOB\sudoku
# Create test script
echo "#!/usr/bin/env python3" > test/test_feature.py
# Create documentation
echo "# Test: Feature Name" > test/test_feature.md
```

### Create New Design Doc
```bash
cd C:\BOB\sudoku
echo "# Feature: Name" > design/FEATURE_IMPLEMENTATION.md
# Update design/README.md with link
```

### Running the Application
```bash
cd C:\BOB\sudoku
python run.py
# or with uv
uv run python run.py
```

---

## Import Paths

When importing from other modules:

### From `run.py`:
```python
# Add src/ to path
import sys
from pathlib import Path
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

# Now import from src/
from sudoku_game import SudokuGame
```

### From Test Scripts:
```python
import sys
from pathlib import Path

# Add src/ to path
src_path = Path(__file__).parent.parent / 'src'
sys.path.insert(0, str(src_path))

# Import from src/
from sudoku_game import SudokuGame
```

---

## Git Workflow

### Files to Ignore
Add to `.gitignore`:
```
__pycache__/
*.pyc
.pytest_cache/
test/debug_logs/
*.tmp
```

### Commit Structure
```bash
# Organize commits by folder:
git add src/sudoku_game.py
git commit -m "feat: add menu system"

git add design/MENU_IMPLEMENTATION.md
git commit -m "docs: document menu implementation"

git add test/test_menu_hover.py
git commit -m "test: add menu hover verification"
```

---

## Current Status

✅ **Reorganization Complete**

Moved to `src/`:
- `sudoku_game.py` (main application)

Moved to `test/`:
- `test_grid_fix.py`
- `test_submenu_hover.py`
- `FIX_UI_OVERLAY_ISSUE.md`
- `TEST_MENU_LAYERING.md`
- `SUBMENU_IMPLEMENTATION.md`
- `SUBMENU_HOVER_FIX.md`
- `MENU_FIXES_COMPLETE.md`

Design docs (already in `design/`):
- All design and user documentation

Entry point created:
- `run.py` - Launcher script

---

## Future Additions

When adding new features:
1. **Code** → `src/sudoku_game.py` (or new module in `src/`)
2. **Tests** → `test/test_feature.py`
3. **Docs** → `design/FEATURE_IMPLEMENTATION.md`
4. **Debugging** → `test/FEATURE_FIX.md` (if needed)

---

**Last Updated**: 2026-08-21  
**Status**: ✅ Fully Organized
