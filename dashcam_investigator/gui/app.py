import logging
import pandas as pd
import sys
from pathlib import Path
from PySide2 import QtWidgets, QtGui
from project_manager.project_datatypes import ProjectStructure, FileAttributes
from project_manager.project_manager import ProjectManager
from gui.table_models import PandasTableModel
from gui.QtMainWindow import Ui_MainWindow
from PySide2.QtMultimedia import QMediaPlayer, QMediaPlaylist
from PySide2.QtCore import QUrl
from utils.convert_milli import convert_to_seconds

logger = logging.getLogger(__name__)


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    # def __init__(self, dir_path, video_path, metadata_df):
    def __init__(self, project_object):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.project_object = project_object
        self.current_video = None

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

        # Load current directory into tree view
        logger.debug(
            f"Loading selected input directory to the TreeView -> {self.project_object.project_info.input_directory} "
        )
        model = QtWidgets.QFileSystemModel()
        model.setRootPath(
            str(Path(self.project_object.project_info.input_directory).resolve())
        )
        self.dir_tree_view.setModel(model)
        self.dir_tree_view.setRootIndex(
            model.index(
                str(Path(self.project_object.project_info.input_directory).resolve())
            )
        )
        self.dir_tree_view.hideColumn(1)
        self.dir_tree_view.hideColumn(2)
        self.dir_tree_view.hideColumn(3)
        self.dir_tree_view.show()
        # Collect the currently selected item
        self.dir_tree_view.clicked.connect(self.on_selected)

        # Define media player
        logger.debug("Loading media player")
        self.mediaPlayer = QMediaPlayer()
        self.mediaPlaylist = QMediaPlaylist()
        # Set the video output from the QMediaPlayer to the QVideoWidget.
        self.mediaPlayer.setVideoOutput(self.video_player)

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

        # Save note when button is clicked
        self.save_note_button.clicked.connect(self.save_note)

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

    def save_note(self):
        """
        Saves the text in the Notes textbox to the project object.
        """
        logger.debug(f"Saved note for -> {self.current_video.name}")
        self.current_video.notes = self.notes_textbox.toPlainText()
        self.note_status.setStyleSheet("QLabel { color : green; }")
        self.note_status.setText("Note saved!")

    def on_selected(self, selected_index):
        self.note_status.setText("")
        # Get the path of the selected file
        fs = QtWidgets.QFileSystemModel()

        if not fs.isDir(selected_index):
            file_name = fs.fileName(selected_index)
            file_path = Path(fs.filePath(selected_index))

            ######################################
            # Video player
            ######################################
            # Stop current video and clear playlist
            self.mediaPlayer.stop()
            self.mediaPlaylist.clear()
            # Add selected video to playlist and initalise the media player
            logger.debug(
                f"New item selected. Adding to playlist -> {str(file_path.resolve())}"
            )
            self.mediaPlaylist.addMedia(QUrl.fromLocalFile(str(file_path.resolve())))
            self.mediaPlayer.setPlaylist(self.mediaPlaylist)

            # Set currently playing label
            self.video_title.setText(f"Currently playing : {str(file_path.resolve())}")

            # Get information for the selected video
            logger.debug(f"Loading video information for -> {file_name}")
            self.current_video: FileAttributes = [
                video
                for video in self.project_object.video_files
                if video.name == file_name
            ][0]

            map_file = self.current_video.output_files[0]
            graph_file = self.current_video.output_files[1]
            metadata_file = self.current_video.meta_files[1]

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

    # Set project options
    input_path = Path("H:\\DissertationDataset\\Nextbase312")
    output_path = Path("E:\\Output_Nextbase_312")

    # If project exists, load project
    if Path(output_path, "dashcam_investigator.json").exists():
        project_manager = ProjectManager()
        project_object = project_manager.load_existing_project(
            Path(output_path, "dashcam_investigator.json")
        )

    window = MainWindow(project_object=project_object)
    window.show()
    sys.exit(app.exec_())
