# Agent and Coding Instructions for Sudoku Project

## Project Organization

### Folder Structure Convention

```
sudoku/
├── src/                      # Source code
│   └── sudoku_game.py        # Main application
├── test/                     # Test files and debug-related docs
│   ├── test_*.py             # Test scripts
│   ├── *_test.md             # Debug/test documentation
│   └── debug_logs/           # Temporary debug output
├── design/                   # Design and architectural documentation
│   ├── QUICK_START.md
│   ├── MENU_SYSTEM_IMPLEMENTATION.md
│   ├── UI_ENHANCEMENT_LOG.md
│   └── [other design docs]
├── sudoku-legacy/            # Legacy code and analysis
│   ├── sudoku3.c
│   └── sudoku-legacy-analysis.md
├── README.md                 # User documentation
├── CLAUDE.md                 # Points to AGENTS.md
├── AGENTS.md                 # Agent instructions (this file)
├── pyproject.toml            # Project metadata and dependencies
└── pyproject.lock            # Locked dependencies
```

### Organization Rules

- **`src/`**: All production source code goes here
  - Main application code
  - Core algorithms
  - Utility functions
  
- **`test/`**: All test and debug-related files
  - Unit tests (`test_*.py`)
  - Integration tests
  - Debug/test documentation (`*_test.md`, `*_fix.md`)
  - Temporary test data
  
- **`design/`**: All design and architectural documentation
  - Feature specifications
  - Implementation guides
  - Enhancement logs
  - Architecture decisions
  - User guides and quick starts
  
- **`sudoku-legacy/`**: Legacy code and historical analysis
  - Original C solver code
  - Comparative analysis documents
  
- **Root level**: Only critical files
  - `README.md` - User-facing documentation
  - `CLAUDE.md` - Project instructions pointer
  - `AGENTS.md` - This file
  - `pyproject.toml` - Dependencies
  - `.gitignore` - Git configuration

---

## Core Principles

- Work incrementally in small, simple steps
- Validate and check each increment before moving on
- Identify root cause before fixing issues
- Use latest library APIs and tools

## Code Style

- No overengineering; keep it simple
- Use exception handlers only when needed
- Write clear, concise docstring comments
- Be sparing with comments outside docstrings
- Keep functions and methods short and focused
- Name things clearly

## Dependency Management

- Use `uv` as the Python package manager
- Always run: `uv run xxx` instead of `python3 xxx`
- Always install with: `uv add xxx` instead of `pip install xxx`
- Maintain dependencies in `pyproject.toml`

## Debugging and Problem Solving

### When Troubleshooting

1. Identify root cause BEFORE fixing
2. Reproduce the problem consistently
3. PROVE THE PROBLEM FIRST - don't guess
4. Try one test at a time and be methodical
5. Don't jump to conclusions or apply workarounds

### Process

- Read error messages carefully
- Check git history for context
- Test changes incrementally
- Verify fixes work as expected

## Project Structure

```
sudoku/
├── sudoku_game.py      # Main application
├── pyproject.toml      # Project metadata and dependencies
├── README.md           # User documentation
├── CLAUDE.md           # This points to AGENTS.md
└── AGENTS.md           # Agent instructions (this file)
```

## Testing and Verification

- Test the UI in a browser/window before reporting completion
- Test golden path and edge cases
- Monitor for regressions in other features
- Type checking and tests verify code correctness, not feature correctness

## Documentation

- Keep README.md concise
- Update README when adding features or changing setup
- No emojis in code, logging, or print statements (except in final README if contextually appropriate)

## Git Practices

- Work on branches for non-trivial changes
- Write clear, descriptive commit messages
- Reference issues when applicable
- Keep commits focused on single logical changes

---

**All future updates and project-specific coding guidelines should be added to this file.**
