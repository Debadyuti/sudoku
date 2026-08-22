# Design Documentation

This folder contains design-related documentation and technical notes.

## Quick Navigation

**New to the project?** Start here:
1. Read: `README.md` (this file) - Overview
2. Check: `NAVIGATION_GUIDE.md` - Where to find everything
3. See: Root `README.md` - Project overview
4. Run: `uv run src/sudoku_game.py` - Start the game

**Need specific information?** Use `NAVIGATION_GUIDE.md` for quick links.

## Files in This Folder

### Navigation & Overview
- **NAVIGATION_GUIDE.md** - Complete navigation map for all documentation
  - Directory structure reference
  - Quick links by task
  - File organization summary
  - Where to find what

### Design & UI Technical Notes
- **TEXT_SELECTION_NOTES.md** - Technical notes on text selection in Pygame
  - Current status: Pygame renders text as bitmaps (not selectable)
  - Workarounds: Ctrl+C to copy, or pygame-gui integration
  - Recommendation: Current Ctrl+C approach is optimal
  - Implementation details for future enhancement

### Legacy Documentation
- Various enhancement logs and quick start guides from development phases

## Design Decisions

### Phase 4: Material Design Color Palette

**Color Philosophy**: Modern, professional, accessible (WCAG AA)

**Key Colors**:
```
Selected cell:    Light blue (150, 220, 255)
Error cells:      Soft red (255, 205, 210)
Solving cells:    Warm yellow (255, 245, 157)
Frozen cells:     Light gray (238, 238, 238)

Buttons (Material Design):
  Finalize:       Green (76, 175, 80)
  Clear:          Red (244, 67, 54)
  Solve Algo:     Blue (33, 150, 243)
  Solve Fast:     Cyan (0, 188, 212)
```

### Phase 3: Animation Framework

**Animation Timings** (frame-time independent):
- Cell highlight fade: 200ms
- Button hover transition: 100ms
- Cell fill during solving: 300ms
- Backtrack animation: 200ms
- Counter pulse: 200ms
- Message slide-in: 200ms

**Easing**: Cubic ease-in-out for natural motion

### Phase 2: Visual Enhancements

**UI Components**:
- Shadow effects on buttons (3D feedback)
- Progress bars for steps and backtracks
- Message toast with slide-in animation
- Menu system with hover highlighting
- Keyboard shortcut hints (capitalized)

### Phase 1: Geometry & Layout

**Window**: 920x800px
- Menu bar: 30px (top)
- Grid area: 540x540px (centered)
- Algorithm panel: 260px (right side)
- Buttons: 2x2 layout below grid

## Technical Notes

### Text Rendering
- Pygame uses bitmap rendering (rasterized font)
- Not natively selectable like web/desktop text
- Users can use Ctrl+C to copy solver stats
- Alternative: pygame-gui library for UITextBox
- Estimated effort: 2-3 hours for pygame-gui integration

### Performance
- Animation speed: Delta-time based (frame-independent)
- FPS target: 60 FPS
- Solver: 10-1000ms per step (adjustable)
- Memory: ~50-100MB typical

### Accessibility
- Keyboard-first design (15+ shortcuts)
- WCAG AA color contrast verified
- Material Design color scheme (familiar to users)
- No animations over 500ms (responsive feel)

## Future Enhancements

### Deferred Features
- Dark mode support (complementary colors)
- High contrast mode (accessibility)
- Color-blind modes (deuteranopia, protanopia)
- Configurable themes
- Custom font support

### Possible Frameworks
- pygame-gui: For native UI widgets, text selection
- Modern theme support: Follows OS dark mode
- Custom renderers: For advanced effects

## Phase 7: Distribution & Auto-Update

- **PHASE7_DISTRIBUTION_DESIGN.md** - Complete design for Tauri + GitHub Releases
  - Auto-update architecture
  - Version management workflow
  - GitHub Actions CI/CD setup
  - Release process documentation
  - User experience flow

## Algorithm Analysis & Optimization (Phase 7+)

Essential reading for algorithm selection:

1. **PHASE7_ALGORITHM_SELECTION.md** ⭐ **START HERE**
   - Decision framework: Which algorithm to implement
   - Your findings summarized (42,000 backtracks issue)
   - Implementation roadmap (7-hour plan)
   - PATH A/B/C options for Phase 7
   - **RECOMMENDATION: Hybrid (Constraint Prop + Heuristics)**

2. **ALGORITHMS_AND_COMPLEXITY.md** - Complete reference
   - **5 solver algorithms documented**:
     1. Naive Backtracking (O(9^n), 200-1000ms)
     2. Backtrack + MRV (50-500ms, 100-5000 backtracks)
     3. Constraint Propagation AC-3 (10-100ms)
     4. **Hybrid (Constraint Prop + Heuristics)** ⭐ RECOMMENDED (5-50ms)
     5. Dancing Links Algorithm X (1-10ms)
   - Complexity analysis for each
   - Human learning value assessment
   - Performance benchmarks and trade-offs
   - Difficulty classification based on algorithmic complexity
   - **Key Finding**: Current "easy" (15 clues) = 42,000+ backtracks (actually HARD!)

3. **DANCING_LINKS_DEEP_DIVE.md** - Algorithm X explained
   - Exact cover problem formulation
   - Subset selection strategy
   - Doubly-linked list data structure
   - Why Dancing Links is fast (O(1) remove/restore)
   - Why it doesn't visualize well
   - When to use (instant solve backend, not visualization)

## Related Documentation

- **PROJECT_STATUS.md** (docs/) - Complete project status report
- **PHASE5_TESTING.md** (tests/procedures/) - Testing procedures
- **AGENTS.md** (root) - Code style and architecture guidelines
- **CLAUDE.md** (root) - Project instructions

---

**Last Updated**: 2026-08-21  
**Status**: Phase 6 complete (Hint, Statistics, Undo/Redo) | Phase 7 designed (ready for implementation) | Algorithm analysis complete
