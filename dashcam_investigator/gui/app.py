import json
import logging
import sys
from pathlib import Path

import pandas as pd
from PySide6 import QtCore, QtWidgets
from PySide6.QtCore import QUrl
from PySide6.QtMultimedia import QMediaPlayer

from dashcam_investigator.core.generate_report import generate_report
from dashcam_investigator.core.get_file_count import get_file_count
from dashcam_investigator.core.process_files import process_files
from dashcam_investigator.gui.main_window import setup_ui
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
        self.mediaPlayer.setVideoOutput(self.video_player)
        self.play_button.clicked.connect(self.play_video)
        self.pause_button.clicked.connect(self.pause_video)
        self.stop_button.clicked.connect(self.stop_video)
        self.mediaPlayer.durationChanged.connect(self.change_duration)
        self.mediaPlayer.positionChanged.connect(self.change_position)
        self.horizontal_slider.sliderMoved.connect(self.video_position)

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
        self.progress.setLabelText(f"Processing files... ({current}/{self.file_count})")
        self.progress.setValue(current)

    def update_object(self, output):
        self.project_object = output
        self.project_manager.write_project_file(data=self.project_object)
        logger.debug("Processing completed!")
        self.load_data()
        self.stack_widget.setCurrentIndex(1)

    def thread_complete(self):
        self.progress.hide()
        logger.debug("Thread completed execution.")

    # --- Video player controls ----------------------------------------
    def play_video(self):
        self.mediaPlayer.play()
        duration = self.mediaPlayer.duration()
        sec, min = convert_to_seconds(int(duration))
        self.total_duration.setText(f"{min}:{sec}")

    def pause_video(self):
        self.mediaPlayer.pause()

    def stop_video(self):
        self.mediaPlayer.stop()

    def change_position(self, position):
        self.horizontal_slider.setValue(position)
        sec, min = convert_to_seconds(int(position))
        self.current_duration.setText(f"{min}:{sec}")

    def change_duration(self, duration):
        self.horizontal_slider.setRange(0, duration)

    def video_position(self, position):
        self.mediaPlayer.setPosition(position)

    # --- Project lifecycle --------------------------------------------
    def open_existing_project(self):
        file_name = QtWidgets.QFileDialog.getOpenFileName(
            self, "Open project", "", "Dashcam Investigator (dashcam_investigator.json)"
        )
        if not file_name or not file_name[0]:
            return
        file_path = Path(file_name[0])
        logger.debug(f"Opening existing project file -> {file_path}")
        if file_path.name != "dashcam_investigator.json":
            QtWidgets.QMessageBox.warning(
                self,
                "Open project",
                "Please select a dashcam_investigator.json file.",
            )
            return
        self.project_object = self.project_manager.load_existing_project(file_path)
        self.load_data()
        self.stack_widget.setCurrentIndex(1)

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
        self.progress = QtWidgets.QProgressDialog(
            "Processing files...", None, 0, self.file_count, self
        )
        self.progress.setWindowModality(QtCore.Qt.WindowModal)
        self.progress.setWindowTitle("Processing files...")
        self.progress.setWindowFlags(
            QtCore.Qt.Window
            | QtCore.Qt.WindowTitleHint
            | QtCore.Qt.CustomizeWindowHint
        )
        self.progress.show()

        worker = Worker(process_files, input_dir, self.project_object)
        worker.signals.result.connect(self.update_object)
        worker.signals.finished.connect(self.thread_complete)
        worker.signals.progress.connect(self.update_progress_dialog)
        self.threadpool.start(worker)

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
        self.project_manager.write_project_file(data=self.project_object)
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
        self.current_video: FileAttributes = [
            video
            for video in self.project_object.video_files
            if video.name == video_name
        ][0]
        logger.debug(f"Loading video information for -> {self.current_video.name}")

        video_path = Path(self.current_video.file_path)

        self.mediaPlayer.stop()
        logger.debug(f"New item selected. Loading -> {str(video_path.resolve())}")
        self.mediaPlayer.setSource(QUrl.fromLocalFile(str(video_path.resolve())))
        self.video_title.setText(f"Currently playing : {str(video_path.resolve())}")

        self._render_output_panels(self.current_video)

    def _render_output_panels(self, video: FileAttributes) -> None:
        """Re-render the map + graph panels around the given video's output files."""
        map_html = self._read_output(video, index=0)
        graph_html = self._read_output(video, index=1)

        self.map_panel.set_context({
            "title": video.name,
            "subtitle": "GPS track",
            "inner_html": map_html,
            "empty_icon": "map-pin",
            "empty_title": "No map available",
            "empty_body": "This video has no GPS data.",
        })
        self.graph_panel.set_context({
            "title": video.name,
            "subtitle": "Speed profile",
            "inner_html": graph_html,
            "empty_icon": "bar-chart",
            "empty_title": "No speed profile",
            "empty_body": "This video has no speed data.",
        })

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

    # --- BridgeController protocol -----------------------------------
    def request_new_project(self) -> None:
        self.start_new_project()

    def request_open_project(self) -> None:
        self.open_existing_project()

    def select_video(self, name: str) -> None:
        if self.project_object is None:
            return
        match = [v for v in self.project_object.video_files if v.name == name]
        if not match:
            logger.warning("select_video: no video named %r in project", name)
            return
        self.load_video_data(name)
        self.bridge.emit_video(self.current_video)

    def set_flag(self, name: str, flagged: bool) -> None:
        if self.project_object is None:
            return
        match = [v for v in self.project_object.video_files if v.name == name]
        if not match:
            logger.warning("set_flag: no video named %r in project", name)
            return
        video = match[0]
        video.flagged = bool(flagged)
        if self.current_video and self.current_video.name == name:
            self.current_video.flagged = video.flagged
        self.project_manager.write_project_file(data=self.project_object)
        logger.debug("Flag persisted -> %s = %s", name, video.flagged)
        self.bridge.flag_changed.emit(name, video.flagged)

    def save_notes(self, name: str, text: str) -> None:
        if self.project_object is None:
            return
        match = [v for v in self.project_object.video_files if v.name == name]
        if not match:
            logger.warning("save_notes: no video named %r in project", name)
            return
        video = match[0]
        video.notes = text
        if self.current_video and self.current_video.name == name:
            self.current_video.notes = text
        self.project_manager.write_project_file(data=self.project_object)
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

    def get_metadata_json(self, name: str) -> str:
        if self.project_object is None:
            return "[]"
        match = [v for v in self.project_object.video_files if v.name == name]
        if not match:
            return "[]"
        video = match[0]
        if not video.meta_files or len(video.meta_files) < 2:
            return "[]"
        metadata_path = Path(video.meta_files[1])
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


def run():
    logger.info("---Running Dashcam Investigator---")
    app = QtWidgets.QApplication([])
    app.setOrganizationName(ORG_NAME)
    app.setApplicationName(APP_NAME)
    logger.debug("Initialising and displaying main window")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
