# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['D:\\Khamsat\\CTrader-project\\trading_tracker5555555\\main.py'],
    pathex=[],
    binaries=[],
    datas=[('utils', 'utils'), ('pages', 'pages')],
    hiddenimports=['telethon', 'customtkinter', 'PIL', 'asyncio', 'logging', 'json', 'tkinter', 'tkinter.messagebox', 'datetime', 're', 'threading'],
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
    name='Telegram_4_Trading',
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
    icon=['D:\\Khamsat\\CTrader-project\\trading_tracker5555555\\utils\\icon.ico'],
)
