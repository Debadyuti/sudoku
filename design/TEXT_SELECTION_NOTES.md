# Text Selection in Pygame - Technical Notes

## Current Status

The Sudoku game renders text directly using Pygame's `pygame.font.Font.render()` which produces graphics (bitmap surfaces). These rendered text surfaces are then drawn onto the main game window.

**Limitation**: Pygame does not support native text selection like web browsers or text editors because:
1. Text is rendered as images (bitmaps), not interactive DOM elements
2. No built-in text input/selection widgets
3. Mouse events don't have cursor tracking for text selection
4. No keyboard shortcuts for text selection (Ctrl+A, etc.)

## Why It's Complex

To implement mouse-selectable text in Pygame, you would need:
1. **Text tracking**: Store original text strings alongside rendered surfaces
2. **Cursor positioning**: Calculate which text character is under the mouse
3. **Selection tracking**: Track selection start/end points during mouse drag
4. **Visual feedback**: Highlight selected text with a background color
5. **Copy/paste handling**: Integrate with system clipboard

This typically requires a custom text widget library (like pygame-gui, thorax, or similar), which adds ~15KB+ dependency.

## Practical Workarounds

### Option 1: Copy Button (Current Implementation)
- User presses Ctrl+C to copy solver stats (already working)
- Stats are formatted into readable text
- Copied to system clipboard automatically

**Pros**: Simple, clean, no extra UI
**Cons**: Requires user to know about Ctrl+C feature

### Option 2: Display in System Clipboard View
- Stats are already Ctrl+C copyable
- Users can paste into Notepad to select and view
- Maximum flexibility

### Option 3: Add lightweight Text Selection Widget
- Use pygame-gui library for text selection widgets
- Would add ~200-300 lines of code
- Would increase binary size by ~15KB

**Pros**: Native text selection like desktop apps
**Cons**: Additional dependency, more code to maintain

## Recommendation

**Current Ctrl+C functionality is already optimal** because:
- ✅ Works for all text in the panel
- ✅ Users can paste into their preferred text editor
- ✅ No extra UI complexity
- ✅ No external dependencies
- ✅ Works on all platforms (Windows, Mac, Linux)

**User Discovery**: Add a help message or tooltip indicating "Press Ctrl+C to copy stats"

## Implementation if Needed Later

If text selection becomes critical, this would be the recommended approach:

```python
# Use pygame-gui for text input widget
from pygame_gui.elements import UITextBox

text_box = UITextBox(
    html_text=stats_text,
    relative_rect=pygame.Rect(x, y, width, height)
)

# This gives you:
# - Mouse text selection with visual highlight
# - Ctrl+C/Ctrl+V clipboard integration
# - Keyboard navigation (arrows, home/end)
# - Multiple text styling options
```

**Estimated effort**: 2-3 hours to integrate pygame-gui for this single feature
