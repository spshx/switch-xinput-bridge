"""Build dist/switch-xinput-bridge.exe with PyInstaller.

vgamepad is listed explicitly instead of using --collect-all: importing it
connects to the ViGEmBus driver, which build machines don't have, and
--collect-all would also bundle the driver installers it ships with.
"""
import importlib.util
import os
import struct
import sys
from pathlib import Path

import PyInstaller.__main__

ROOT = Path(__file__).resolve().parent.parent
vgamepad_dir = Path(importlib.util.find_spec("vgamepad").origin).parent
arch = "x64" if struct.calcsize("P") == 8 else "x86"
dll = vgamepad_dir / "win" / "vigem" / "client" / arch / "ViGEmClient.dll"
if not dll.exists():
    sys.exit(f"ViGEmClient.dll not found at {dll}")

os.chdir(ROOT)
PyInstaller.__main__.run([
    "--noconfirm", "--onefile", "--clean",
    "--name", "switch-xinput-bridge",
    "--paths", "src",
    "--distpath", "dist", "--workpath", "build", "--specpath", "build",
    "--hidden-import", "vgamepad",
    "--hidden-import", "vgamepad.win.virtual_gamepad",
    "--hidden-import", "vgamepad.win.vigem_client",
    "--hidden-import", "vgamepad.win.vigem_commons",
    "--add-binary", f"{dll}{os.pathsep}vgamepad/win/vigem/client/{arch}",
    "src/switch_xinput_bridge/__main__.py",
])
