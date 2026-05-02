"""
ThemeManager: reads the OS color scheme via QStyleHints (Qt 6.5+) and
keeps both Qt (QSS) and the embedded WebViews (data-theme attribute) in
sync. Allows manual override that takes precedence over the OS.

Phase 1 ships the wiring; Phase 2 fills in real QSS files.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Literal

from PySide6.QtCore import QObject, Qt, Signal
from PySide6.QtGui import QGuiApplication

from .web.bridge import Bridge
from .web.renderer import qss_path

logger = logging.getLogger(__name__)

ThemeName = Literal["light", "dark", "system"]


class ThemeManager(QObject):
    """Owns the active theme and broadcasts changes to Qt + JS."""

    resolved_changed = Signal(str)  # "light" | "dark" — after resolving "system"

    def __init__(self, bridge: Bridge, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._bridge = bridge
        self._mode: ThemeName = "system"

        hints = QGuiApplication.styleHints()
        # colorSchemeChanged is Qt 6.5+. We pinned >= 6.5.
        hints.colorSchemeChanged.connect(self._on_os_scheme_changed)

    @property
    def mode(self) -> ThemeName:
        return self._mode

    def resolved(self) -> str:
        if self._mode != "system":
            return self._mode
        scheme = QGuiApplication.styleHints().colorScheme()
        return "dark" if scheme == Qt.ColorScheme.Dark else "light"

    def set_mode(self, mode: ThemeName) -> None:
        if mode not in ("light", "dark", "system"):
            logger.warning("Ignoring unknown theme mode %r", mode)
            return
        self._mode = mode
        self._broadcast()

    def apply_initial(self) -> None:
        """Call once after QApplication is up and Bridge is wired."""
        self._broadcast()

    # --- internals -----------------------------------------------------
    def _on_os_scheme_changed(self, _scheme) -> None:
        if self._mode == "system":
            self._broadcast()

    def _broadcast(self) -> None:
        resolved = self.resolved()
        logger.debug("Theme broadcast: mode=%s resolved=%s", self._mode, resolved)
        self._bridge.theme_changed.emit(resolved)
        self.resolved_changed.emit(resolved)
        self._apply_qss(resolved)

    def _apply_qss(self, resolved: str) -> None:
        path: Path = qss_path() / f"{resolved}.qss"
        if not path.is_file():
            logger.debug("No QSS file at %s; skipping", path)
            return
        app = QGuiApplication.instance()
        if app is None:
            return
        # QGuiApplication doesn't have setStyleSheet; QApplication does. Cast.
        if hasattr(app, "setStyleSheet"):
            app.setStyleSheet(path.read_text())  # type: ignore[attr-defined]
