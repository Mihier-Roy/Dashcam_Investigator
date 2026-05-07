# PyInstaller spec for Dashcam Investigator. Cross-platform: works on Windows,
# Linux, and macOS. Build with: `uv run pyinstaller DashcamInvestigator.spec`.
#
# Output: dist/DashcamInvestigator/ (a one-folder bundle). On Windows the
# launcher is DashcamInvestigator.exe; on Linux/macOS it's DashcamInvestigator.
#
# ExifTool is intentionally NOT bundled: on Linux it's a Perl script and on
# Windows users typically install it system-wide. The app probes the PATH at
# startup (gui/app.py) and shows a helpful dialog if it's missing.

import sys
from pathlib import Path

from PyInstaller.utils.hooks import collect_submodules

SPEC_DIR = Path(SPECPATH).resolve()
IS_WINDOWS = sys.platform.startswith("win")

datas = [
    (str(SPEC_DIR / "gpx.fmt"), "."),
    (str(SPEC_DIR / "log.conf"), "."),
    (
        str(SPEC_DIR / "dashcam_investigator" / "gui" / "assets"),
        "dashcam_investigator/gui/assets",
    ),
]

binaries = []
if IS_WINDOWS:
    # Optional convenience: if exiftool.exe sits next to the spec, ship it.
    bundled_exiftool = SPEC_DIR / "exiftool.exe"
    if bundled_exiftool.is_file():
        binaries.append((str(bundled_exiftool), "."))

hiddenimports = collect_submodules("dashcam_investigator")

a = Analysis(
    [str(SPEC_DIR / "dashcam_investigator" / "__main__.py")],
    pathex=[str(SPEC_DIR)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="DashcamInvestigator",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,  # --windowed: no terminal on any platform
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="DashcamInvestigator",
)
