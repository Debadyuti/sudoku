# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for macOS (.app bundle)
# Run on a Mac with:  python -m PyInstaller SudokuGame_mac.spec

a = Analysis(
    ['sudoku_game.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='SudokuGame',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,        # must be False for pygame apps
    target_arch=None,            # None = native arch; set 'universal2' for Apple-Silicon + Intel fat binary
    codesign_identity=None,
    entitlements_file=None,
)

app = BUNDLE(
    exe,
    name='SudokuGame.app',
    icon=None,                   # replace with 'SudokuGame.icns' if you have an icon file
    bundle_identifier='com.sudoku.game',
    info_plist={
        'CFBundleName': 'SudokuGame',
        'CFBundleDisplayName': 'Sudoku Game',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0',
        'NSHighResolutionCapable': True,
        'NSPrincipalClass': 'NSApplication',
        'NSAppleScriptEnabled': False,
    },
)
