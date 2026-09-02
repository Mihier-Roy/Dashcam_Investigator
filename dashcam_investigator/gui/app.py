import ctypes
import json
import logging
import shutil
import sys
from pathlib import Path

import pandas as pd
import PySide6
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import QUrl
from PySide6.QtMultimedia import QMediaPlayer

from dashcam_investigator.constants import PROJECT_FILE_NAME
from dashcam_investigator.core.generate_report import generate_report
from dashcam_investigator.core.get_file_count import get_file_count
from dashcam_investigator.core.process_files import process_files
from dashcam_investigator.exceptions import (
    DashcamInvestigatorError,
    ProjectLoadError,
    ProjectSaveError,
)
from dashcam_investigator.gui.main_window import _icon, setup_ui
from dashcam_investigator.gui.new_project_class import NewProjectDialog
from dashcam_investigator.gui.theme import ThemeManager
from dashcam_investigator.gui.web.bridge import Bridge
from dashcam_investigator.gui.worker_class import Worker
from dashcam_investigator.project_manager.project_datatypes import FileAttributes
from dashcam_investigator.project_manager.project_manager import ProjectManager
from dashcam_investigator.utils.common import convert_to_seconds
from dashcam_investigator.utils.custom_json_functions import ProjectEncoder

logger = logging.getLogger(__name__)

ORG_NAME = "DashcamInvestigator"
APP_NAME = "DashcamInvestigator"

# Transport-icon tint per resolved theme; mirrors tokens.css --text.
_TRANSPORT_TINT = {"light": "#0f172a", "dark": "#e6e8eb"}

_AV_LOG_ERROR = 16  # libavutil/log.h


def _quiet_ffmpeg_logging() -> None:
    """Raise the bundled FFmpeg log level to ERROR.

    Qt Multimedia's FFmpeg backend leaves libavutil at its default WARNING
    level, which prints `[swscaler @ ...] deprecated pixel format used` to
    stderr once per frame for JPEG-range (yuvj420p) footage -- common for
    GoPro and many dashcams. Qt exposes no knob for this, so call
    av_log_set_level on the libavutil PySide6 ships. Must run after
    QMediaPlayer has loaded the FFmpeg plugin: libavutil can't be dlopen'd
    on its own (unresolved OpenSSL symbols), but once Qt has it in-process
    ctypes just reuses that handle.
    """
    lib_dir = Path(PySide6.__file__).parent / "Qt" / "lib"
    candidates = sorted(lib_dir.glob("libavutil.so.*"))
    if not candidates:
        logger.debug("No bundled libavutil found; leaving FFmpeg log level as-is")
        return
    try:
        ctypes.CDLL(str(candidates[0])).av_log_set_level(_AV_LOG_ERROR)
    except (OSError, AttributeError) as exc:
        logger.debug("Could not set FFmpeg log level: %s", exc)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.project_manager = ProjectManager()
        self.project_object = None
        self.current_video = None

        self.threadpool = QtCore.QThreadPool()
        logger.debug(f"Multithreading with {self.threadpool.maxThreadCount()} threads")

        # The bridge must exist before setup_ui constructs WebPanels.
        self.bridge = Bridge(self, parent=self)
        self.theme_manager = ThemeManager(self.bridge, parent=self)

        setup_ui(self, self.bridge)

        self._wire_menu_actions()
        self._wire_media_player()

        self._restore_settings()
        self.theme_manager.apply_initial()

    # --- Setup helpers -------------------------------------------------
    def _wire_menu_actions(self) -> None:
        self.action_new_project.triggered.connect(self.start_new_project)
        self.action_open_project.triggered.connect(self.open_existing_project)
        self.actionGenerate_Report.triggered.connect(self.create_report)

    def _wire_media_player(self) -> None:
        self.mediaPlayer = QMediaPlayer(self)
        _quiet_ffmpeg_logging()
        self.mediaPlayer.setVideoOutput(self.video_player)
        self._transport_icons: dict[tuple[str, str], QtGui.QIcon] = {}
        self.play_pause_button.toggled.connect(self._on_play_pause_toggled)
        self.stop_button.clicked.connect(self.stop_video)
        self.mediaPlayer.playbackStateChanged.connect(self._on_playback_state_changed)
        self.mediaPlayer.durationChanged.connect(self.change_duration)
        self.mediaPlayer.positionChanged.connect(self.change_position)
        self.horizontal_slider.sliderMoved.connect(self.video_position)
        self.theme_manager.resolved_changed.connect(self._refresh_transport_icons)

    # --- QSettings persistence ----------------------------------------
    def _restore_settings(self) -> None:
        s = QtCore.QSettings()
        geometry = s.value("window/geometry")
        if geometry:
            self.restoreGeometry(geometry)
        h_state = s.value("window/h_splitter")
        if h_state:
            self.h_splitter.restoreState(h_state)
        v_state = s.value("window/v_splitter")
        if v_state:
            self.v_splitter.restoreState(v_state)

    def _save_settings(self) -> None:
        s = QtCore.QSettings()
        s.setValue("window/geometry", self.saveGeometry())
        s.setValue("window/h_splitter", self.h_splitter.saveState())
        s.setValue("window/v_splitter", self.v_splitter.saveState())

    def closeEvent(self, event):  # noqa: N802 (Qt API)
        self._save_settings()
        super().closeEvent(event)

    # --- Worker signal collectors -------------------------------------
    def update_progress_dialog(self, current):
        self.progress.setValue(current)

    def update_status_label(self, message: str):
        self.progress.setLabelText(
            f"({self.progress.value()}/{self.file_count}) {message}"
        )

    def update_object(self, output):
        self.project_object = output
        self._persist_project()
        logger.debug("Processing completed!")
        self.load_data()
        self.stack_widget.setCurrentIndex(1)

    def thread_complete(self):
        self.progress.hide()
        logger.debug("Thread completed execution.")

    def _persist_project(self) -> None:
        """Write the current project to disk, showing an error dialog on failure."""
        try:
            self.project_manager.write_project_file(data=self.project_object)
        except ProjectSaveError as exc:
            logger.error("Failed to save project: %s", exc)
            QtWidgets.QMessageBox.critical(
                self, "Save error", f"Could not save the project file:\n\n{exc}"
            )

    def _on_worker_error(self, err_tuple: tuple):
        exc_type, exc_value, _ = err_tuple
        if issubclass(exc_type, DashcamInvestigatorError):
            message = str(exc_value)
        else:
            message = f"An unexpected error occurred.\nSee the log file for details.\n\n{exc_value}"
        logger.error("Worker error: %s: %s", exc_type.__name__, exc_value)
        self.progress.hide()
        QtWidgets.QMessageBox.critical(self, "Processing error", message)

    # --- Video player controls ----------------------------------------
    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:  # noqa: N802 (Qt API)
        focus_widget = QtWidgets.QApplication.focusWidget()
        typing_widgets = (QtWidgets.QLineEdit, QtWidgets.QTextEdit, QtWidgets.QPlainTextEdit)
        if isinstance(focus_widget, typing_widgets):
            super().keyPressEvent(event)
            return

        if event.key() == QtCore.Qt.Key.Key_Space and self.current_video is not None:
            self.play_pause_button.toggle()
            event.accept()
            return
        if event.key() == QtCore.Qt.Key.Key_Right and self.current_video is not None:
            self.mediaPlayer.setPosition(self.mediaPlayer.position() + 5000)
            event.accept()
            return
        if event.key() == QtCore.Qt.Key.Key_Left and self.current_video is not None:
            self.mediaPlayer.setPosition(max(0, self.mediaPlayer.position() - 5000))
            event.accept()
            return
        super().keyPressEvent(event)

    def _on_play_pause_toggled(self, checked: bool) -> None:
        if checked:
            self.mediaPlayer.play()
        else:
            self.mediaPlayer.pause()

    def _on_playback_state_changed(self, state) -> None:
        playing = state == QMediaPlayer.PlaybackState.PlayingState
        self.play_pause_button.blockSignals(True)
        self.play_pause_button.setChecked(playing)
        self.play_pause_button.blockSignals(False)
        self._refresh_transport_icons()

    def _transport_icon(self, name: str) -> QtGui.QIcon:
        theme = self.theme_manager.resolved()
        key = (name, theme)
        icon = self._transport_icons.get(key)
        if icon is None:
            icon = self._transport_icons[key] = _icon(name, _TRANSPORT_TINT[theme])
        return icon

    def _refresh_transport_icons(self, _resolved: str | None = None) -> None:
        playing = self.play_pause_button.isChecked()
        self.play_pause_button.setIcon(self._transport_icon("pause" if playing else "play"))
        self.play_pause_button.setToolTip("Pause (Space)" if playing else "Play (Space)")
        self.stop_button.setIcon(self._transport_icon("square"))

    def stop_video(self):
        self.mediaPlayer.stop()

    def change_position(self, position):
        self.horizontal_slider.setValue(position)
        sec, min = convert_to_seconds(int(position))
        self.current_duration.setText(f"{min}:{sec}")

    def change_duration(self, duration):
        self.horizontal_slider.setRange(0, duration)
        sec, min = convert_to_seconds(int(duration))
        self.total_duration.setText(f"{min}:{sec}")

    def video_position(self, position):
        self.mediaPlayer.setPosition(position)

    # --- Project lifecycle --------------------------------------------
    def open_existing_project(self):
        file_name = QtWidgets.QFileDialog.getOpenFileName(
            self, "Open project", "", "Dashcam Investigator (dashcam_investigator.json)"
        )
        if not file_name or not file_name[0]:
            return
        self.open_project_path(Path(file_name[0]))

    def open_project_path(self, path: Path, interactive: bool = True) -> bool:
        """Load a project from `path` (its json file, or the directory containing it).

        Shared by the "Open project" dialog and the `--project` CLI flag.
        `interactive=False` (used for the CLI flag) logs errors instead of
        popping a blocking message box, so headless/`--screenshot` runs
        can't hang waiting for input nobody can provide.
        Returns True on success, False otherwise.
        """
        file_path = path / PROJECT_FILE_NAME if path.is_dir() else path
        logger.debug(f"Opening existing project file -> {file_path}")
        if file_path.name != PROJECT_FILE_NAME:
            message = "Please select a dashcam_investigator.json file."
            if interactive:
                QtWidgets.QMessageBox.warning(self, "Open project", message)
            else:
                logger.error(message)
            return False
        try:
            self.project_object = self.project_manager.load_existing_project(file_path)
        except ProjectLoadError as exc:
            logger.error("Failed to load project: %s", exc)
            if interactive:
                QtWidgets.QMessageBox.critical(
                    self, "Open error", f"Could not open the project file:\n\n{exc}"
                )
            return False
        self.load_data()
        self.stack_widget.setCurrentIndex(1)
        return True

    def start_new_project(self):
        logger.debug("Starting a new project. Launched new project dialog.")
        dialog = NewProjectDialog(self)
        dialog.exec()
        if dialog.result() != QtWidgets.QDialog.Accepted:
            return

        logger.debug("Retreiving values entered into dialog.")
        input_dir, output_dir, case_name, investigator_name = dialog.save()

        logger.debug("Creating a new project with inputs provided.")
        self.project_manager = ProjectManager(
            input_dir=input_dir,
            output_dir=output_dir,
            case_name=case_name,
            investigator_name=investigator_name,
        )
        self.project_object = self.project_manager.new_project()

        logger.debug("Counting files in directory")
        self.file_count = get_file_count(input_dir)

        logger.debug(f"Processing {self.file_count} files from input directory")
        self.progress = self._make_progress_dialog(self.file_count)

        worker = Worker(process_files, input_dir, self.project_object)
        worker.signals.result.connect(self.update_object)
        worker.signals.finished.connect(self.thread_complete)
        worker.signals.progress.connect(self.update_progress_dialog)
        worker.signals.status.connect(self.update_status_label)
        worker.signals.error.connect(self._on_worker_error)
        self.threadpool.start(worker)

    def _make_progress_dialog(self, total: int) -> QtWidgets.QProgressDialog:
        """Build and show the modal 'Processing files...' progress dialog."""
        progress = QtWidgets.QProgressDialog("Processing files...", None, 0, total, self)
        progress.setWindowModality(QtCore.Qt.WindowModal)
        progress.setWindowTitle("Processing files...")
        progress.setWindowFlags(
            QtCore.Qt.Window | QtCore.Qt.WindowTitleHint | QtCore.Qt.CustomizeWindowHint
        )
        progress.show()
        return progress

    def load_data(self):
        """Push the current project to every WebPanel listening on the bridge."""
        if self.project_object is None:
            return
        logger.debug("Broadcasting project to web panels")
        self.bridge.emit_project(self.project_object)

    # --- Report -------------------------------------------------------
    def create_report(self):
        if self.project_object is None:
            return
        report_path = generate_report(self.project_object)
        self.project_object.project_info.report_path = str(report_path.resolve())
        self._persist_project()
        dlg = QtWidgets.QMessageBox(self)
        dlg.setWindowTitle("Report generator")
        dlg.setStandardButtons(QtWidgets.QMessageBox.Close)
        dlg.setIcon(QtWidgets.QMessageBox.Information)
        dlg.setText(f"Report generated!\n View the report at : {report_path}")
        dlg.exec()
        self.bridge.report_generated.emit(str(report_path.resolve()))

    # --- Video selection ---------------------------------------------
    def load_video_data(self, video_name):
        """
        Load the selected video into the native player and re-render the
        map / graph WebPanels. Metadata + notes update via the bridge.
        """
        video = self._find_video(video_name)
        if video is None:
            return
        self.current_video: FileAttributes = video
        logger.debug(f"Loading video information for -> {self.current_video.name}")

        video_path = Path(self.current_video.file_path)

        self.mediaPlayer.stop()
        # stop() on an already-stopped player emits nothing, so a stale
        # checked state (play pressed with no source) would otherwise drift.
        self._on_playback_state_changed(self.mediaPlayer.playbackState())
        self.player_stack.setCurrentWidget(self.video_player)
        logger.debug(f"New item selected. Loading -> {str(video_path.resolve())}")
        self.mediaPlayer.setSource(QUrl.fromLocalFile(str(video_path.resolve())))
        self.video_title.setText(video_path.name)
        self.video_title.setToolTip(str(video_path.resolve()))

        self._render_output_panels(self.current_video)

    def _render_output_panels(self, video: FileAttributes) -> None:
        """Re-render the map + graph panels around the given video's output files."""
        map_html = self._read_output(video, index=0)
        graph_html = self._read_output(video, index=1)

        self.map_panel.set_context(
            {
                "title": video.name,
                "subtitle": "GPS track",
                "inner_html": map_html,
                "empty_icon": "map-pin",
                "empty_title": "No map available",
                "empty_body": "This video has no GPS data.",
            }
        )
        self.graph_panel.set_context(
            {
                "title": video.name,
                "subtitle": "Speed profile",
                "inner_html": graph_html,
                "empty_icon": "bar-chart",
                "empty_title": "No speed profile",
                "empty_body": "This video has no speed data.",
            }
        )

    @staticmethod
    def _read_output(video: FileAttributes, index: int) -> str | None:
        """Read an output file from a video (map=0, graph=1). None if missing."""
        if not video.output_files or len(video.output_files) <= index:
            return None
        path = Path(video.output_files[index])
        if not path.is_file():
            logger.warning("Output file missing: %s", path)
            return None
        try:
            return path.read_text()
        except OSError as exc:
            logger.warning("Failed to read %s: %s", path, exc)
            return None

    def _find_video(self, name: str) -> FileAttributes | None:
        """Look up a video by name in the current project.

        Returns None silently if no project is loaded, or with a logged
        warning if the project has no video by that name.
        """
        if self.project_object is None:
            return None
        for video in self.project_object.video_files:
            if video.name == name:
                return video
        logger.warning("No video named %r in project", name)
        return None

    # --- BridgeController protocol -----------------------------------
    def request_new_project(self) -> None:
        self.start_new_project()

    def request_open_project(self) -> None:
        self.open_existing_project()

    def select_video(self, name: str) -> None:
        video = self._find_video(name)
        if video is None:
            return
        self.load_video_data(name)
        self.bridge.emit_video(self.current_video)

    def set_flag(self, name: str, flagged: bool) -> None:
        video = self._find_video(name)
        if video is None:
            return
        video.flagged = bool(flagged)
        if self.current_video and self.current_video.name == name:
            self.current_video.flagged = video.flagged
        self._persist_project()
        logger.debug("Flag persisted -> %s = %s", name, video.flagged)
        self.bridge.flag_changed.emit(name, video.flagged)

    def save_notes(self, name: str, text: str) -> None:
        video = self._find_video(name)
        if video is None:
            return
        video.notes = text
        if self.current_video and self.current_video.name == name:
            self.current_video.notes = text
        self._persist_project()
        logger.debug("Notes persisted -> %s (%d chars)", name, len(text))
        self.bridge.notes_saved.emit(name)

    def generate_report(self) -> None:
        self.create_report()

    def set_theme(self, name: str) -> None:
        self.theme_manager.set_mode(name)  # type: ignore[arg-type]

    def get_project_json(self) -> str:
        if self.project_object is None:
            return "null"
        return json.dumps(self.project_object, cls=ProjectEncoder)

    # --- Keyboard shortcut entry points -------------------------------
    def toggle_flag_current(self) -> None:
        if self.current_video is None:
            return
        self.set_flag(self.current_video.name, not self.current_video.flagged)

    def select_next_video(self) -> None:
        self._cycle_video(1)

    def select_previous_video(self) -> None:
        self._cycle_video(-1)

    def request_shortcuts_help(self) -> None:
        QtWidgets.QMessageBox.information(
            self,
            "Keyboard shortcuts",
            "/          Focus the sidebar filter\n"
            "F          Flag / un-flag the current video\n"
            "← / →      Previous / next video (any panel)\n"
            "↑ / ↓      Move selection in the sidebar list\n"
            "Space      Play / pause (player focused)\n"
            "← / →      Seek ±5s (player focused)\n"
            "Ctrl+S     Save notes\n"
            "?          Show this help",
        )

    def _cycle_video(self, step: int) -> None:
        if self.project_object is None:
            return
        videos = self.project_object.video_files
        if not videos:
            return
        current_name = self.current_video.name if self.current_video else None
        try:
            idx = next(i for i, v in enumerate(videos) if v.name == current_name)
        except StopIteration:
            idx = -1
        new_idx = (idx + step) % len(videos)
        self.select_video(videos[new_idx].name)

    def get_metadata_json(self, name: str) -> str:
        video = self._find_video(name)
        if video is None:
            return "[]"
        if not video.meta_files or "csv" not in video.meta_files:
            return "[]"
        metadata_path = Path(video.meta_files["csv"])
        if not metadata_path.is_file():
            logger.warning("Metadata CSV missing: %s", metadata_path)
            return "[]"
        try:
            df = pd.read_csv(metadata_path)
        except Exception as exc:  # noqa: BLE001 — surface as empty table
            logger.warning("Failed to read metadata CSV %s: %s", metadata_path, exc)
            return "[]"
        if df.empty:
            return "[]"
        row = df.iloc[0].to_dict()
        rows = [
            {"property": str(k), "value": "" if pd.isna(v) else str(v)}
            for k, v in row.items()
        ]
        return json.dumps(rows)


def run(
    project_path: Path | None = None,
    screenshot_path: Path | None = None,
    screenshot_delay: float = 2.0,
) -> None:
    logger.info("---Running Dashcam Investigator---")
    app = QtWidgets.QApplication([])
    app.setOrganizationName(ORG_NAME)
    app.setApplicationName(APP_NAME)

    if shutil.which("exiftool") is None:
        QtWidgets.QMessageBox.critical(
            None,
            "ExifTool not found",
            "ExifTool is required but was not found on your PATH.\n\n"
            "Please install ExifTool and ensure it is accessible from the command line.\n"
            "Download: https://exiftool.org",
        )
        logger.error("exiftool not found on PATH — aborting startup")
        sys.exit(1)

    logger.debug("Initialising and displaying main window")
    window = MainWindow()

    if project_path is not None:
        # Non-interactive whenever a screenshot is also requested: a
        # headless/offscreen run has nobody to dismiss a blocking dialog.
        loaded = window.open_project_path(
            project_path, interactive=screenshot_path is None
        )
        if not loaded:
            logger.error(f"Could not open project at startup -> {project_path}")
            sys.exit(1)

    window.show()

    if screenshot_path is not None:

        def _capture_and_quit() -> None:
            window.grab().save(str(screenshot_path))
            logger.info(f"Saved screenshot -> {screenshot_path}")
            app.quit()

        # WebEngine panels (map/graph/notes) render asynchronously; give
        # them a moment to paint before grabbing. Flaky under software
        # rendering, hence the tunable delay rather than a fixed sleep.
        QtCore.QTimer.singleShot(int(screenshot_delay * 1000), _capture_and_quit)

    sys.exit(app.exec())
