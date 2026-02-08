# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Energy Stats Processor
Creates a single-file Windows executable with all dependencies bundled.

Build with: pyinstaller energy-processor.spec
Output: dist/energy-processor.exe
"""

block_cipher = None

a = Analysis(
    ['src\\main.py'],
    pathex=[],
    binaries=[],
    datas=[
        # Include any data files here if needed
        # ('data/sample.csv', 'data'),
    ],
    hiddenimports=[
        # Explicitly include imports that PyInstaller might miss
        'pandas',
        'matplotlib',
        'matplotlib.backends.backend_agg',  # For saving plots
        'scipy',
        'scipy.interpolate',  # Used in graph smoothing
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude unnecessary packages to reduce size
        'tkinter',
        'PyQt5',
        'PyQt6',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='energy-processor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # Compress with UPX if available
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Keep console window for CLI tool
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # icon='icon.ico',  # Uncomment and add icon file if desired
    # version='version_info.txt',  # Uncomment after creating valid version info
)

