"""
This is the entrypoint of the application that configures logging and then executes the GUI.
"""

import argparse
import logging
import logging.config
import sys
from pathlib import Path

from platformdirs import user_log_path

# The dci:// URL scheme must be registered BEFORE QApplication is created,
# which happens inside app.run(). Doing it here at import time keeps the
# ordering correct regardless of how Qt modules get imported below.
from .gui.web.scheme import register_scheme

register_scheme()

from .gui import app  # noqa: E402  (import after register_scheme on purpose)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="dashcam_investigator")
    parser.add_argument(
        "--project",
        type=Path,
        default=None,
        help="Open this project on startup instead of showing the welcome "
        "screen. Accepts a dashcam_investigator.json file or its "
        "containing directory.",
    )
    parser.add_argument(
        "--screenshot",
        type=Path,
        default=None,
        help="Save a screenshot of the main window to this path shortly "
        "after startup, then exit. Combine with QT_QPA_PLATFORM=offscreen "
        "for headless verification (e.g. in CI).",
    )
    parser.add_argument(
        "--screenshot-delay",
        type=float,
        default=2.0,
        help="Seconds to wait before capturing --screenshot, to let "
        "WebEngine panels finish rendering (default: 2.0).",
    )
    return parser.parse_args()


def _resolve_log_dir() -> Path:
    """Per-user log directory across platforms.

    Windows -> %LOCALAPPDATA%/DashcamInvestigator/Logs
    Linux   -> $XDG_STATE_HOME/DashcamInvestigator/log (typically ~/.local/state/...)
    macOS   -> ~/Library/Logs/DashcamInvestigator
    """
    return user_log_path(
        "DashcamInvestigator", "DashcamInvestigator", ensure_exists=True
    )


def _resolve_log_conf() -> Path:
    """Locate log.conf in dev checkouts and PyInstaller-frozen bundles."""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / "log.conf"  # type: ignore[attr-defined]
    return Path(__file__).resolve().parent.parent / "log.conf"


if __name__ == "__main__":
    args = _parse_args()

    log_dir = _resolve_log_dir()
    # fileConfig substitutes %(logPath)s into the file handler args. Forward
    # slashes work on every platform Python's logging module supports.
    log_path_str = log_dir.as_posix()

    logging.config.fileConfig(
        str(_resolve_log_conf()),
        defaults={"logPath": log_path_str},
        disable_existing_loggers=False,
    )

    logger = logging.getLogger(__name__)

    # Launch GUI
    app.run(
        project_path=args.project,
        screenshot_path=args.screenshot,
        screenshot_delay=args.screenshot_delay,
    )
