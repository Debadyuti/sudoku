# Documentation Guide

This guide helps you navigate the organized documentation structure.

## Directory Structure

```
C:\BOB\sudoku\
├── src/                      # Source code
│   ├── sudoku_game.py        # Main game logic
│   ├── ui.py                 # UI rendering
│   ├── solver.py             # Solver algorithms
│   ├── menu.py               # Menu system
│   └── constants.py          # Constants and utilities
│
├── tests/                    # Tests and testing documentation
│   ├── README.md             # Testing overview
│   ├── test_*.py             # Unit test files (122 tests)
│   └── procedures/           # Phase 5 testing procedures
│       ├── README.md         # Quick start guide
│       ├── PHASE5_TESTING.md # Detailed procedures
│       ├── PHASE5_QUICK_START.txt    # Quick reference
│       ├── PHASE5_TESTING_RESULTS.md # Results tracker
│       └── PHASE5_EXECUTION_SUMMARY.md # Overview
│
├── design/                   # Design documentation
│   ├── README.md             # Design overview
│   └── TEXT_SELECTION_NOTES.md # UI technical notes
│
├── docs/                     # Project documentation
│   ├── README.md             # Documentation index
│   └── PROJECT_STATUS.md     # Complete project status
│
├── CLAUDE.md                 # Project instructions (ROOT)
├── AGENTS.md                 # Code style guidelines (ROOT)
├── README.md                 # Main readme (ROOT)
├── IMPLEMENTATION_COMPLETE.txt # Implementation notes (ROOT)
└── DOCUMENTATION_GUIDE.md    # This file (ROOT)
```

## Where to Find What

### For Testing (Phase 5)
📁 **Location**: `tests/procedures/`

1. **Quick Start**: `PHASE5_QUICK_START.txt`
   - 5-minute overview
   - Keyboard shortcuts
   - Testing checklist
   - What to look for

2. **Detailed Guide**: `PHASE5_TESTING.md`
   - Complete testing procedures
   - 10 test categories
   - Expected behaviors
   - Potential issues

3. **Results**: `PHASE5_TESTING_RESULTS.md`
   - Testing results tracker
   - 29-item checklist
   - Issues found section

4. **Overview**: `PHASE5_EXECUTION_SUMMARY.md`
   - Phase 5 strategy
   - Test breakdown
   - Success criteria

### For Design Decisions
📁 **Location**: `design/`

1. **Design Overview**: `README.md`
   - Color palette
   - Animation timings
   - UI components
   - Performance notes

2. **Technical Notes**: `TEXT_SELECTION_NOTES.md`
   - Text rendering in Pygame
   - Selection workarounds
   - Alternative approaches

### For Project Status
📁 **Location**: `docs/`

1. **Full Status**: `PROJECT_STATUS.md`
   - Completed phases
   - Current state
   - Future phases
   - Metrics and statistics

2. **Documentation Index**: `README.md`
   - Quick navigation
   - Feature checklist
   - Testing status

### For Code Guidelines
📁 **Location**: Root directory

1. **Code Style**: `AGENTS.md`
   - Style guidelines
   - Architecture patterns
   - Best practices

2. **Project Instructions**: `CLAUDE.md`
   - Project setup
   - Development notes
   - Important guidelines

3. **README**: `README.md`
   - Project overview
   - Quick start
   - Features

## Quick Links

### I want to...

**Run the game**
```bash
cd C:\BOB\sudoku
uv run src/sudoku_game.py
```
📖 See: `README.md`

**Execute Phase 5 testing**
1. Read: `tests/procedures/PHASE5_QUICK_START.txt` (5 min)
2. Follow: `tests/procedures/PHASE5_TESTING.md` (detailed procedures)
3. Track: `tests/procedures/PHASE5_TESTING_RESULTS.md` (results)

**Run unit tests**
```bash
cd C:\BOB\sudoku
uv run pytest tests/ -v
```
📖 See: `tests/README.md`

**Understand design decisions**
📖 See: `design/README.md` and `design/TEXT_SELECTION_NOTES.md`

**Check project status**
📖 See: `docs/PROJECT_STATUS.md`

**Learn code guidelines**
📖 See: `AGENTS.md` (architecture) and `CLAUDE.md` (instructions)

**Understand text selection limitation**
📖 See: `design/TEXT_SELECTION_NOTES.md`

## File Organization Summary

### Root (.md files only)
| File | Purpose |
|------|---------|
| CLAUDE.md | Project instructions |
| AGENTS.md | Code style guidelines |
| README.md | Main project readme |
| DOCUMENTATION_GUIDE.md | This file |

### tests/procedures/ (Phase 5)
| File | Purpose |
|------|---------|
| README.md | Testing guide overview |
| PHASE5_QUICK_START.txt | Quick reference (5 min) |
| PHASE5_TESTING.md | Detailed procedures (360+ lines) |
| PHASE5_TESTING_RESULTS.md | Results tracker |
| PHASE5_EXECUTION_SUMMARY.md | Execution overview |

### design/ (Design Docs)
| File | Purpose |
|------|---------|
| README.md | Design overview |
| TEXT_SELECTION_NOTES.md | UI technical notes |

### docs/ (Project Docs)
| File | Purpose |
|------|---------|
| README.md | Documentation index |
| PROJECT_STATUS.md | Complete status report |

## Navigation Tips

1. **New to the project?**
   - Start: `README.md` (root)
   - Then: `docs/PROJECT_STATUS.md`
   - Finally: `src/sudoku_game.py` (read code)

2. **Need to test?**
   - Start: `tests/procedures/PHASE5_QUICK_START.txt`
   - Reference: `tests/procedures/PHASE5_TESTING.md`
   - Track: `tests/procedures/PHASE5_TESTING_RESULTS.md`

3. **Want to understand design?**
   - Start: `design/README.md`
   - Details: `design/TEXT_SELECTION_NOTES.md`
   - Implementation: `AGENTS.md`

4. **Need the full picture?**
   - Start: `docs/PROJECT_STATUS.md`
   - Details: Specific .md files from there

## File Naming Convention

- **PHASE5_*.md** - Testing documentation (5 files in tests/procedures/)
- **README.md** - Folder overviews (4 files, one per folder)
- **PROJECT_STATUS.md** - Full project report (docs/)
- **TEXT_SELECTION_NOTES.md** - Technical notes (design/)
- **CLAUDE.md, AGENTS.md** - Project guidelines (root)

## Status by Document

| Document | Phase | Status | Last Updated |
|----------|-------|--------|---|
| PROJECT_STATUS.md | 5 | 🟡 Testing | 2026-08-21 |
| PHASE5_TESTING.md | 5 | ✅ Complete | 2026-08-21 |
| PHASE5_QUICK_START.txt | 5 | ✅ Complete | 2026-08-21 |
| PHASE5_TESTING_RESULTS.md | 5 | ✅ Complete | 2026-08-21 |
| TEXT_SELECTION_NOTES.md | Design | ✅ Complete | 2026-08-21 |
| design/README.md | Design | ✅ Complete | 2026-08-21 |

## Maintenance Notes

- **Tests**: Keep tests/ clean - only test files and testing procedures
- **Design**: Keep design/ for UI/design decisions only
- **Docs**: Use docs/ for project-level reports and summaries
- **Root**: Keep minimal - only core instructions and readme

---

**Last Updated**: 2026-08-21  
**Total Documentation**: 8 main markdown files + 4 README.md index files  
**Organization**: Phase 5 ready for testing
