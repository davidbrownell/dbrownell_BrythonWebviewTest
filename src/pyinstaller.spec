# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for dbrownell_BrythonWebviewTest

from pathlib import Path

block_cipher = None
src_dir = Path("dbrownell_BrythonWebviewTest")

a = Analysis(
    [str(src_dir / "ApplicationEntryPoint.py")],
    pathex=["src"],
    binaries=[],
    datas=[
        (str(src_dir / "web" / "static"), "dbrownell_BrythonWebviewTest/web/static"),
        (str(src_dir / "web" / "index.jinja2.py"), "dbrownell_BrythonWebviewTest/web"),
        (str(src_dir / "web" / "__init__.py"), "dbrownell_BrythonWebviewTest/web"),
    ],
    hiddenimports=[
        "uvicorn.logging",
        "uvicorn.loops",
        "uvicorn.loops.auto",
        "uvicorn.protocols",
        "uvicorn.protocols.http",
        "uvicorn.protocols.http.auto",
        "uvicorn.protocols.websockets",
        "uvicorn.protocols.websockets.auto",
        "uvicorn.lifespan",
        "uvicorn.lifespan.on",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="dbrownell_BrythonWebviewTest",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
