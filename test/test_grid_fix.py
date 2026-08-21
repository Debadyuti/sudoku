#!/usr/bin/env python3
"""Test script to verify grid positioning fix"""
import sys
sys.path.insert(0, '.')

# Import constants and verify they are correct
from sudoku_game import (
    MENU_HEIGHT, GRID_TOP, MARGIN, GRID_SIZE, CELL_SIZE, WIDTH, HEIGHT
)

print("=" * 60)
print("GRID POSITIONING VERIFICATION")
print("=" * 60)

# Check layout constants
print(f"\nWindow: {WIDTH}×{HEIGHT}px")
print(f"Menu bar height: {MENU_HEIGHT}px")
print(f"Grid top offset: {GRID_TOP}px (should be {MARGIN} + {MENU_HEIGHT} = {MARGIN + MENU_HEIGHT})")
print(f"Grid size: {GRID_SIZE}×{GRID_SIZE}px")
print(f"Cell size: {CELL_SIZE}×{CELL_SIZE}px")

# Verify GRID_TOP is correct
expected_grid_top = MARGIN + MENU_HEIGHT
if GRID_TOP == expected_grid_top:
    print(f"✓ GRID_TOP is correct ({GRID_TOP})")
else:
    print(f"✗ GRID_TOP is wrong: got {GRID_TOP}, expected {expected_grid_top}")

# Check grid extends correctly
grid_bottom = GRID_TOP + GRID_SIZE
print(f"\nGrid layout:")
print(f"  Top: {GRID_TOP}px")
print(f"  Bottom: {grid_bottom}px")
print(f"  Left: {MARGIN}px")
print(f"  Right: {MARGIN + GRID_SIZE}px")

# Verify no overlap with menu
if GRID_TOP >= MENU_HEIGHT:
    print(f"✓ Grid starts below menu bar ({GRID_TOP}px > {MENU_HEIGHT}px)")
else:
    print(f"✗ Grid overlaps menu bar!")

# Verify fits in window
if grid_bottom <= HEIGHT:
    print(f"✓ Grid fits within window height ({grid_bottom}px <= {HEIGHT}px)")
else:
    print(f"⚠ Grid might exceed window height ({grid_bottom}px > {HEIGHT}px)")

print("\n" + "=" * 60)
print("Grid positioning check complete!")
print("=" * 60)
