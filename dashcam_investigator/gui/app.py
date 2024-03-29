import logging
import pandas as pd
import sys
from pathlib import Path
from PySide2 import QtWidgets, QtGui, QtCore
from core.get_file_count import get_file_count
from core.process_files import process_files
from core.generate_report import generate_report
from gui.worker_class import Worker
from gui.new_project_class import NewProjectDialog
from project_manager.project_datatypes import FileAttributes
from project_manager.project_manager import ProjectManager
from gui.qt_models import PandasTableModel, VideoListModel, NavigationListModel
from gui.QtMainWindow import Ui_MainWindow
from PySide2.QtMultimedia import QMediaPlayer, QMediaPlaylist
from PySide2.QtCore import QUrl
from utils.common import convert_to_seconds

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
        # Navigation
        ######################################
        # Load the navigation list
        navigation_model = NavigationListModel(NAVIGATION_PAGES)
        self.navigation_tab.setModel(navigation_model)
        self.navigation_tab.setStyleSheet("QListView::item { padding: 25px; }")
        # Handle navigation
        self.navigation_tab.clicked.connect(self.navigate)

        ######################################
        # Project controls
        ######################################
        # Handle starting a new project
        self.new_project_button.clicked.connect(self.start_new_project)
        # Handle opening an existing project
        self.existing_project_button.clicked.connect(self.open_existing_project)

        ######################################
        # Report generation
        ######################################
        self.actionGenerate_Report.triggered.connect(self.create_report)

        ######################################
        # Video selection controls
        ######################################
        # Collect the currently selected item from the tree view
        self.dir_tree_view.clicked.connect(self.on_selected)
        # Collect the currently selected item from list view
        self.video_list_view.clicked.connect(self.on_vid_selected)

        # Define media player
        logger.debug("Loading media player")
        self.mediaPlayer = QMediaPlayer()
        self.mediaPlaylist = QMediaPlaylist()
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
        # Save/flag video controls
        ######################################
        # Save note/flag status when button is clicked
        self.note_status.setStyleSheet("QLabel { color : green; }")
        self.save_note_button.clicked.connect(self.save_note)
        self.flag_video_button.clicked.connect(self.flag_video)

    ######################################
    # Thread signal collectors
    ######################################
    def update_progress_dialog(self, current):
        self.progress.setLabelText(f"Processing files... ({current}/{self.file_count})")
        self.progress.setValue(current)

    def update_object(self, output):
        self.project_object = output
        self.project_manager.write_project_file(data=self.project_object)
        logger.debug(f"Processing completed!")
        # Navigate to the project page
        self.load_data()
        self.stack_widget.setCurrentIndex(1)

    def thread_complete(self):
        self.progress.hide()
        logger.debug(f"Thread completed execution.")

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
        if file_name != None:
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
        logger.debug(f"Starting a new project. Launched new project dialog.")
        dialog = NewProjectDialog(self)
        dialog.exec()
        # If the user closes the dialog by clicking on 'Okay', then begin processing
        if dialog.result() == 1:
            logger.debug(f"Retreiving values entered into dialog.")
            input_dir, output_dir, case_name, investigator_name = dialog.save()

            # Create a new project manager object and begin processing data
            logger.debug(f"Creating a new project with inputs provided.")
            self.project_manager = ProjectManager(
                input_dir=input_dir,
                output_dir=output_dir,
                case_name=case_name,
                investigator_name=investigator_name,
            )
            self.project_object = self.project_manager.new_project()

            # Get the total number of files in the directory
            logger.debug(f"Counting files in directory")
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
        # Populate the video table view
        self.list_model = VideoListModel(self.project_object.video_files)
        self.video_list_view.setModel(self.list_model)

        # Load current project directory to tree view
        tree_path = Path(self.project_object.project_info.input_directory).resolve()
        logger.debug(f"Loading selected input directory to the TreeView -> {tree_path}")
        model = QtWidgets.QFileSystemModel()
        model.setRootPath(str(tree_path))
        self.dir_tree_view.setModel(model)
        self.dir_tree_view.setRootIndex(model.index(str(tree_path)))

        # Ensure that the tree view shows only the name columns
        self.dir_tree_view.hideColumn(1)
        self.dir_tree_view.hideColumn(2)
        self.dir_tree_view.hideColumn(3)
        self.dir_tree_view.show()

    ######################################
    # Generate a report
    ######################################
    def create_report(self):
        if self.project_object != None:
            report_path = generate_report(self.project_object)
            self.project_object.project_info.report_path = str(report_path.resolve())
            self.project_manager.write_project_file(data=self.project_object)
            dlg = QtWidgets.QMessageBox(self)
            dlg.setWindowTitle("Report generator")
            dlg.setStandardButtons(QtWidgets.QMessageBox.Close)
            dlg.setIcon(QtWidgets.QMessageBox.Information)
            dlg.setText(f"Report generated!\n View the report at : {report_path}")
            dlg.exec_()

    ######################################
    # Notes/flag controls
    ######################################
    def save_note(self):
        """
        Saves the text in the Notes textbox to the project object.
        """
        logger.debug(f"Saved note for -> {self.current_video.name}")
        self.current_video.notes = self.notes_textbox.toPlainText()
        self.project_manager.write_project_file(data=self.project_object)
        self.note_status.setText("Note saved!")

    def flag_video(self):
        """
        Set flagged property to True and write to file.
        """
        index = self.video_list_view.selectedIndexes()
        logger.debug(f"Flagged video -> {self.current_video.name}")
        self.current_video.flagged = not self.current_video.flagged
        if self.current_video.flagged:
            self.note_status.setText("Video flagged!")
        else:
            self.note_status.setText("Video un-flagged!")
        self.project_manager.write_project_file(data=self.project_object)
        self.list_model.dataChanged.emit(index[0], index[0])

    ######################################
    # Actions when a video is selected from tree view or list
    ######################################
    def on_vid_selected(self, selected_index):
        """
        When a video is selected from the List View, get the file name and pass it to load_video_data
        """
        self.load_video_data(selected_index.data())

    def on_selected(self, selected_index):
        """
        When a file is selected from the Tree view, get the file name and pass it to load_video_data
        """
        self.note_status.setText("")
        # Get the path of the selected file
        fs = QtWidgets.QFileSystemModel()

        if not fs.isDir(selected_index):
            file_name = fs.fileName(selected_index)
            self.load_video_data(file_name)

    def load_video_data(self, video_name):
        """
        This function retrieves the information for the selected video.
        The information is used to load the video into the player and load maps, metadata, graphs and notes.
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
        metadata_file = self.current_video.meta_files[1]

        ######################################
        # Video player
        ######################################
        # Stop current video and clear playlist
        self.mediaPlayer.stop()
        self.mediaPlaylist.clear()
        # Add selected video to playlist and initalise the media player
        logger.debug(
            f"New item selected. Adding to playlist -> {str(video_path.resolve())}"
        )
        self.mediaPlaylist.addMedia(QUrl.fromLocalFile(str(video_path.resolve())))
        self.mediaPlayer.setPlaylist(self.mediaPlaylist)

        # Set currently playing label
        self.video_title.setText(f"Currently playing : {str(video_path.resolve())}")

        ######################################
        # Map tab
        ######################################
        with Path(map_file).open() as f:
            html_str = f.read()
        self.maps_web_view.setHtml(html_str)

        ######################################
        # Metadata tab
        ######################################
        metadata_df = pd.read_csv(metadata_file).T
        metadata_df.rename(columns={0: "Value"}, inplace=True)
        self.metadata_model = PandasTableModel(metadata_df)
        self.metadata_table.setModel(self.metadata_model)

        ######################################
        # Speed Graph tab
        ######################################
        with Path(graph_file).open() as f:
            graph_str = f.read()
        self.graph_web_view.setHtml(graph_str)

        ######################################
        # Notes tab
        ######################################
        self.notes_textbox.setText(str(self.current_video.notes))


def run():
    logger.info("---Running Dashcam Investigator---")
    app = QtWidgets.QApplication([])
    logger.debug("Initialising and displaying main window")
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
