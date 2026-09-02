"""
The single QObject exposed to JavaScript over QWebChannel.

The bridge is intentionally a thin façade: signals carry plain JSON
strings; slots are forwarded to a controller (typically the MainWindow)
that owns the project state. Phase 1 wires the surface; later phases
populate the controller methods.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Protocol

from PySide6.QtCore import QObject, Signal, Slot

from dashcam_investigator.utils.custom_json_functions import ProjectEncoder

logger = logging.getLogger(__name__)


class BridgeController(Protocol):
    """Implemented by MainWindow."""

    def request_new_project(self) -> None: ...
    def request_open_project(self) -> None: ...
    def select_video(self, name: str) -> None: ...
    def set_flag(self, name: str, flagged: bool) -> None: ...
    def save_notes(self, name: str, text: str) -> None: ...
    def generate_report(self) -> None: ...
    def set_theme(self, name: str) -> None: ...
    def get_project_json(self) -> str: ...
    def get_metadata_json(self, name: str) -> str: ...

    # Phase 9: keyboard shortcut entry points.
    def toggle_flag_current(self) -> None: ...
    def select_next_video(self) -> None: ...
    def select_previous_video(self) -> None: ...
    def request_shortcuts_help(self) -> None: ...


class Bridge(QObject):
    """Slots are JS→Python; signals are Python→JS."""

    # --- Python → JS ---------------------------------------------------
    project_loaded = Signal(str)  # JSON-serialized ProjectStructure
    video_changed = Signal(str)  # JSON-serialized FileAttributes
    notes_saved = Signal(str)  # video name
    flag_changed = Signal(str, bool)  # name, flagged
    theme_changed = Signal(str)  # "light" | "dark"
    progress = Signal(int, int)  # current, total
    report_generated = Signal(str)  # path to report HTML
    focus_search = Signal()  # sidebar should focus its filter input
    save_requested = Signal()  # the active panel (notes) should save

    def __init__(
        self, controller: BridgeController, parent: QObject | None = None
    ) -> None:
        super().__init__(parent)
        self._controller = controller

    # --- JS → Python ---------------------------------------------------
    @Slot()
    def requestNewProject(self) -> None:  # noqa: N802 (JS naming)
        logger.debug("bridge: requestNewProject")
        self._controller.request_new_project()

    @Slot()
    def requestOpenProject(self) -> None:  # noqa: N802
        logger.debug("bridge: requestOpenProject")
        self._controller.request_open_project()

    @Slot(str)
    def selectVideo(self, name: str) -> None:  # noqa: N802
        logger.debug("bridge: selectVideo(%s)", name)
        self._controller.select_video(name)

    @Slot(str, bool)
    def setFlag(self, name: str, flagged: bool) -> None:  # noqa: N802
        logger.debug("bridge: setFlag(%s, %s)", name, flagged)
        self._controller.set_flag(name, flagged)

    @Slot(str, str)
    def saveNotes(self, name: str, text: str) -> None:  # noqa: N802
        logger.debug("bridge: saveNotes(%s, len=%d)", name, len(text))
        self._controller.save_notes(name, text)

    @Slot()
    def generateReport(self) -> None:  # noqa: N802
        logger.debug("bridge: generateReport")
        self._controller.generate_report()

    @Slot(str)
    def setTheme(self, name: str) -> None:  # noqa: N802
        logger.debug("bridge: setTheme(%s)", name)
        self._controller.set_theme(name)

    @Slot(result=str)
    def getProjectJson(self) -> str:  # noqa: N802
        return self._controller.get_project_json()

    @Slot(str, result=str)
    def getMetadataJson(self, name: str) -> str:  # noqa: N802
        return self._controller.get_metadata_json(name)

    # --- Keyboard shortcut entry points -------------------------------
    @Slot()
    def focusSearch(self) -> None:  # noqa: N802
        logger.debug("bridge: focusSearch")
        self.focus_search.emit()

    @Slot()
    def requestSaveNotes(self) -> None:  # noqa: N802
        logger.debug("bridge: requestSaveNotes")
        self.save_requested.emit()

    @Slot()
    def requestShortcutsHelp(self) -> None:  # noqa: N802
        logger.debug("bridge: requestShortcutsHelp")
        self._controller.request_shortcuts_help()

    @Slot()
    def toggleFlagCurrent(self) -> None:  # noqa: N802
        logger.debug("bridge: toggleFlagCurrent")
        self._controller.toggle_flag_current()

    @Slot()
    def selectNextVideo(self) -> None:  # noqa: N802
        logger.debug("bridge: selectNextVideo")
        self._controller.select_next_video()

    @Slot()
    def selectPreviousVideo(self) -> None:  # noqa: N802
        logger.debug("bridge: selectPreviousVideo")
        self._controller.select_previous_video()

    # --- helpers used by the controller --------------------------------
    def emit_project(self, project: Any) -> None:
        """Emit a ProjectStructure (or any object/dict the encoder handles)."""
        self.project_loaded.emit(json.dumps(project, cls=ProjectEncoder))

    def emit_video(self, video: Any) -> None:
        """Emit a FileAttributes (or dict) representing the selected video."""
        self.video_changed.emit(json.dumps(video, cls=ProjectEncoder))
