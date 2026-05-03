import json
import logging
import sys
from pathlib import Path

import pandas as pd
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import QUrl
from PySide6.QtMultimedia import QMediaPlayer

from dashcam_investigator.core.generate_report import generate_report
from dashcam_investigator.core.get_file_count import get_file_count
from dashcam_investigator.core.process_files import process_files
from dashcam_investigator.gui.new_project_class import NewProjectDialog
from dashcam_investigator.gui.qt_models import NavigationListModel
from dashcam_investigator.gui.QtMainWindow import Ui_MainWindow
from dashcam_investigator.gui.theme import ThemeManager
from dashcam_investigator.gui.web.bridge import Bridge
from dashcam_investigator.gui.web.panel import WebPanel
from dashcam_investigator.gui.worker_class import Worker
from dashcam_investigator.project_manager.project_datatypes import FileAttributes
from dashcam_investigator.project_manager.project_manager import ProjectManager
from dashcam_investigator.utils.common import convert_to_seconds
from dashcam_investigator.utils.custom_json_functions import ProjectEncoder

logger = logging.getLogger(__name__)
NAVIGATION_PAGES = ["Welcome", "Project"]


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self) -> None:
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.project_manager = ProjectManager()
        self.project_object = None
        self.current_video = None

        # Intialise a thread pool to run background tasks
        self.threadpool = QtCore.QThreadPool()
        logger.debug(f"Multithreading with {self.threadpool.maxThreadCount()} threads")

        # Move the application window to the center of the screen
        logger.debug("Moving window to the center of the screen")
        # Get current screen size
        screen_size = QtGui.QScreen.availableGeometry(
            QtWidgets.QApplication.primaryScreen()
        )
        # Compute the  coordinates for the center of the screen
        x_coordinates = (screen_size.width() - self.width()) / 2
        y_coordinates = (screen_size.height() - self.height()) / 2 - 20
        self.move(x_coordinates, y_coordinates)

        ######################################
        # Web layer (Phase 3+)
        ######################################
        # Bridge is the single QObject exposed to every WebPanel via QWebChannel.
        self.bridge = Bridge(self, parent=self)
        self.theme_manager = ThemeManager(self.bridge, parent=self)

        # Replace the Qt Designer-built welcome page with a WebPanel rendered
        # from welcome.html. The rest of the stack (project page) stays Qt
        # for now and gets converted in later phases.
        old_welcome = self.stack_widget.widget(0)
        self.stack_widget.removeWidget(old_welcome)
        old_welcome.deleteLater()
        self.welcome_panel = WebPanel("welcome.html", self.bridge, parent=self)
        self.stack_widget.insertWidget(0, self.welcome_panel)
        self.stack_widget.setCurrentIndex(0)

        # Replace the Qt directory tree + video list (file_tab) with a single
        # WebPanel rendering sidebar.html. file_tab was a child of project_page
        # at fixed geometry; we reparent the panel and match the geometry until
        # Phase 7 introduces real layouts.
        sidebar_geo = self.file_tab.geometry()
        sidebar_parent = self.file_tab.parentWidget()
        self.file_tab.hide()
        self.file_tab.deleteLater()
        self.sidebar_panel = WebPanel("sidebar.html", self.bridge, parent=sidebar_parent)
        self.sidebar_panel.setGeometry(sidebar_geo)
        self.sidebar_panel.show()

        # Replace the Metadata and Notes tab contents with WebPanels. Map +
        # Speed Graph stay native here (Phase 6 converts those).
        self.metadata_panel = self._mount_panel_in_tab(self.metadata_tab, "metadata.html")
        self.notes_panel = self._mount_panel_in_tab(self.notes_tab, "notes.html")

        # Push the resolved theme to JS + apply matching QSS now that the
        # webview exists.
        self.theme_manager.apply_initial()

        ######################################
        # Navigation
        ######################################
        # Load the navigation list
        navigation_model = NavigationListModel(NAVIGATION_PAGES)
        self.navigation_tab.setModel(navigation_model)
        self.navigation_tab.setStyleSheet("QListView::item { padding: 25px; }")
        # Handle navigation
        self.navigation_tab.clicked.connect(self.navigate)

        ######################################
        # Report generation
        ######################################
        self.actionGenerate_Report.triggered.connect(self.create_report)

        ######################################
        # Video selection: handled by the sidebar WebPanel via Bridge.selectVideo
        ######################################

        # Define media player
        logger.debug("Loading media player")
        self.mediaPlayer = QMediaPlayer(self)
        # Set the video output from the QMediaPlayer to the QVideoWidget.
        self.mediaPlayer.setVideoOutput(self.video_player)

        ######################################
        # Video playback controls
        ######################################
        # Set the QPushButtons to play, pause and stop the video in the QVideoWidget.
        self.play_button.clicked.connect(self.play_video)
        self.pause_button.clicked.connect(self.pause_video)
        self.stop_button.clicked.connect(self.stop_video)
        # Set the total range for the QSlider.
        self.mediaPlayer.durationChanged.connect(self.change_duration)
        # Set the current value for the QSlider.
        self.mediaPlayer.positionChanged.connect(self.change_position)
        # Set the video position in QMediaPlayer based on the QSlider position.
        self.horizontal_slider.sliderMoved.connect(self.video_position)

        ######################################
        # Save/flag controls live in notes.html — the Bridge routes
        # JS button clicks to set_flag / save_notes below.
        ######################################

    ######################################
    # Tab content mounting
    ######################################
    def _mount_panel_in_tab(self, tab: QtWidgets.QWidget, template_name: str) -> WebPanel:
        """Replace all children of `tab` with a WebPanel filling it via a layout."""
        for child in list(tab.children()):
            if isinstance(child, QtWidgets.QWidget):
                child.hide()
                child.deleteLater()
        existing_layout = tab.layout()
        if existing_layout is not None:
            QtWidgets.QWidget().setLayout(existing_layout)  # detach + drop
        layout = QtWidgets.QVBoxLayout(tab)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        panel = WebPanel(template_name, self.bridge, parent=tab)
        layout.addWidget(panel)
        return panel

    ######################################
    # Thread signal collectors
    ######################################
    def update_progress_dialog(self, current):
        self.progress.setLabelText(f"Processing files... ({current}/{self.file_count})")
        self.progress.setValue(current)

    def update_object(self, output):
        self.project_object = output
        self.project_manager.write_project_file(data=self.project_object)
        logger.debug("Processing completed!")
        # Navigate to the project page
        self.load_data()
        self.stack_widget.setCurrentIndex(1)

    def thread_complete(self):
        self.progress.hide()
        logger.debug("Thread completed execution.")

    ######################################
    # Navigation controls
    ######################################
    def navigate(self, selected_index):
        """
        Set the current page of the stack widget to the index of the list view
        """
        self.stack_widget.setCurrentIndex(selected_index.row())

    ######################################
    # Video player controls
    ######################################
    def play_video(self):
        """
        Handles the clicked signal generated by playButton and plays the video in the mediaPlayer.
        """
        self.mediaPlayer.play()
        duration = self.mediaPlayer.duration()
        sec, min = convert_to_seconds(int(duration))
        self.total_duration.setText(f"{min}:{sec}")

    def pause_video(self):
        """
        Handles the clicked signal generated by playButton and pauses video in the mediaPlayer.
        """
        self.mediaPlayer.pause()

    def stop_video(self):
        """
        Handles the clicked signal generated by playButton and stops the video in the mediaPlayer.
        """
        self.mediaPlayer.stop()

    def change_position(self, position):
        """
        Handles the positionChanged signal generated by the mediaPlayer.
        Sets the current value of the QSlider to the current position of the video in the QMediaPlayer.
        :param position: current position of the video in the QMediaPlayer.
        """
        self.horizontal_slider.setValue(position)
        sec, min = convert_to_seconds(int(position))
        self.current_duration.setText(f"{min}:{sec}")

    def change_duration(self, duration):
        """
        Handles the durationChanged signal generated by the mediaPlayer.
        Sets the range of the QSlider.
        :param duration: Total duration of the video in the QMediaPlayer.
        """
        self.horizontal_slider.setRange(0, duration)

    def video_position(self, position):
        """
        Handles the sliderMoved signal generated by the horizontalSlider.
        Changes the position of the video in the QMediaPlayer on changing the value of the QSlider.
        :param position: Current position value of the QSlider.
        :return:
        """
        self.mediaPlayer.setPosition(position)

    ######################################
    # New/Load project controls
    ######################################
    def open_existing_project(self):
        """
        Launches a QFileDialog which allows the user to select a .json file.
        """
        file_name = QtWidgets.QFileDialog.getOpenFileName(
            self, "Open File", "C:", ("JSON (*.json)")
        )
        if file_name is not None:
            # If project exists, load
            logger.debug(f"Opening existing project file -> {file_name[0]}")
            file_path = Path(file_name[0])
            # If the file is a dashcam_investigator file, load the project from it
            if file_path.name == "dashcam_investigator.json":
                # Load project into object
                self.project_object = self.project_manager.load_existing_project(
                    file_path
                )

                # Load tree and video data
                self.load_data()

                # Navigate to the project page
                self.stack_widget.setCurrentIndex(1)

    def start_new_project(self):
        """
        Launch the new project dialog and setup a new project.
        """
        logger.debug("Starting a new project. Launched new project dialog.")
        dialog = NewProjectDialog(self)
        dialog.exec()
        # If the user closes the dialog by clicking on 'Okay', then begin processing
        if dialog.result() == QtWidgets.QDialog.Accepted:
            logger.debug("Retreiving values entered into dialog.")
            input_dir, output_dir, case_name, investigator_name = dialog.save()

            # Create a new project manager object and begin processing data
            logger.debug("Creating a new project with inputs provided.")
            self.project_manager = ProjectManager(
                input_dir=input_dir,
                output_dir=output_dir,
                case_name=case_name,
                investigator_name=investigator_name,
            )
            self.project_object = self.project_manager.new_project()

            # Get the total number of files in the directory
            logger.debug("Counting files in directory")
            self.file_count = get_file_count(input_dir)

            logger.debug(f"Processing {self.file_count} files from input directory")
            # Initalise progress bar
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

            # Iterate through the directory and categorise files
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

    ######################################
    # Generate a report
    ######################################
    def create_report(self):
        if self.project_object is not None:
            report_path = generate_report(self.project_object)
            self.project_object.project_info.report_path = str(report_path.resolve())
            self.project_manager.write_project_file(data=self.project_object)
            dlg = QtWidgets.QMessageBox(self)
            dlg.setWindowTitle("Report generator")
            dlg.setStandardButtons(QtWidgets.QMessageBox.Close)
            dlg.setIcon(QtWidgets.QMessageBox.Information)
            dlg.setText(f"Report generated!\n View the report at : {report_path}")
            dlg.exec()

    def load_video_data(self, video_name):
        """
        Load the selected video into the native player and the map / graph
        web views. Metadata + notes are now driven by the WebPanels via the
        bridge (see select_video / get_metadata_json / video_changed).
        """
        # Get the attributes of the selected video
        self.current_video: FileAttributes = [
            video
            for video in self.project_object.video_files
            if video.name == video_name
        ][0]

        logger.debug(f"Loading video information for -> {self.current_video.name}")

        video_path = Path(self.current_video.file_path)
        map_file = self.current_video.output_files[0]
        graph_file = self.current_video.output_files[1]

        # Video player (Qt) ---------------------------------------------
        self.mediaPlayer.stop()
        logger.debug(f"New item selected. Loading -> {str(video_path.resolve())}")
        self.mediaPlayer.setSource(QUrl.fromLocalFile(str(video_path.resolve())))
        self.video_title.setText(f"Currently playing : {str(video_path.resolve())}")

        # Map tab (Qt — Phase 6 converts) -------------------------------
        with Path(map_file).open() as f:
            self.maps_web_view.setHtml(f.read())

        # Speed Graph tab (Qt — Phase 6 converts) -----------------------
        with Path(graph_file).open() as f:
            self.graph_web_view.setHtml(f.read())


    ######################################
    # BridgeController protocol — Phase 3 wires new/open/report/theme;
    # video/notes/flag/metadata land in Phases 4-6.
    ######################################
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
    logger.debug("Initialising and displaying main window")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
