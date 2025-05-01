# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['C:\\Users\\del\\Downloads\\pesquisa\\pesquisa_playlist.py'],
    pathex=[],
    binaries=[('C:\\Windows\\System32\\vcruntime140.dll', '.'), ('C:\\Windows\\System32\\msvcp140.dll', '.')],
    datas=[],
    hiddenimports=['tkinter', 'tkinter.ttk', 'sqlite3', 're', 'requests', 'threading', 'concurrent.futures', 'vlc', 'customtkinter', 'PIL', 'PIL._tkinter_finder', 'charset_normalizer', 'certifi', 'idna', 'urllib3', 'multidict', 'attrs', 'frozenlist', 'aiosignal', 'async_timeout', 'yarl', 'colorama', 'win32_setctime'],
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
    name='PesquisaPlaylist',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
