# Design Documentation

This folder contains design-related documentation and technical notes.

## Files

### Design & UI Notes
- **TEXT_SELECTION_NOTES.md** - Technical notes on text selection in Pygame
  - Current status: Pygame renders text as bitmaps (not selectable)
  - Workarounds: Ctrl+C to copy, or pygame-gui integration
  - Recommendation: Current Ctrl+C approach is optimal
  - Implementation details for future enhancement

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

## Related Documentation

- **PROJECT_STATUS.md** (docs/) - Complete project status report
- **PHASE5_TESTING.md** (tests/procedures/) - Testing procedures
- **AGENTS.md** (root) - Code style and architecture guidelines
- **CLAUDE.md** (root) - Project instructions

---

**Last Updated**: 2026-08-21  
**Status**: Complete (Phase 4 - Color Palette implemented)
