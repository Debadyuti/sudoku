#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# build_mac.sh  —  Build SudokuGame.app on macOS
# ---------------------------------------------------------------------------
# Prerequisites (run once):
#   brew install python          # or use python.org installer
#   pip3 install pygame pyinstaller
#
# Usage:
#   chmod +x build_mac.sh
#   ./build_mac.sh
#
# Output:  dist/SudokuGame.app
# ---------------------------------------------------------------------------

set -e

echo "==> Checking Python..."
python3 --version

echo "==> Installing / upgrading dependencies..."
pip3 install --quiet --upgrade pygame pyinstaller

echo "==> Building SudokuGame.app ..."
python3 -m PyInstaller SudokuGame_mac.spec --clean --noconfirm

echo ""
echo "✅  Build complete: dist/SudokuGame.app"
echo ""
echo "To run:   open dist/SudokuGame.app"
echo "To ship:  zip -r SudokuGame_mac.zip dist/SudokuGame.app"
