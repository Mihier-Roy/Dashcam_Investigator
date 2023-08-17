import logging
from pathlib import Path
import sys
from qfluentwidgets import ListWidget, TreeView, Pivot
from PySide2.QtWidgets import (
    QApplication,
    QMainWindow,
    QStackedWidget,
    QListWidgetItem,
    QFileSystemModel,
)
from PySide2.QtCore import Qt
from PySide2.QtGui import QScreen
from dashcam_investigator.project_manager.project_manager import ProjectManager
from fluent_gui.qt_models import PandasTableModel, VideoListModel, NavigationListModel
from fluent_gui.QtFluentMainWindow import Ui_MainWindow

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Initialise project objects
        self.project_manager = ProjectManager()
        self.project_object = None
        self.current_video = None

        # Move the application window to the center of the screen
        logger.debug("Moving window to the center of the screen")
        # Get current screen size
        screen_size = QScreen.availableGeometry(QApplication.primaryScreen())
        # Compute the  coordinates for the center of the screen
        x_coordinates = (screen_size.width() - self.width()) / 2
        y_coordinates = (screen_size.height() - self.height()) / 2 - 20
        self.move(x_coordinates, y_coordinates)

        ######################################
        # File tab navigation
        ######################################
        # Populate the video table view
        stands = [
            "白金之星",
            "绿色法皇",
            "天堂制造",
            "绯红之王",
            "银色战车",
            "疯狂钻石",
            "壮烈成仁",
            "败者食尘",
            "黑蚊子多",
            "杀手皇后",
            "金属制品",
            "石之自由",
            "砸瓦鲁多",
            "钢链手指",
            "臭氧宝宝",
            "华丽挚爱",
            "隐者之紫",
            "黄金体验",
            "虚无之王",
            "纸月之王",
            "骇人恶兽",
            "男子领域",
            "20世纪男孩",
            "牙 Act 4",
            "铁球破坏者",
            "性感手枪",
            "D4C • 爱之列车",
            "天生完美",
            "软又湿",
            "佩斯利公园",
            "奇迹于你",
            "行走的心",
            "护霜旅行者",
            "十一月雨",
            "调情圣手",
            "片刻静候",
        ]
        for stand in stands:
            item = QListWidgetItem(stand)
            # item.setIcon(QIcon(':/qfluentwidgets/images/logo.png'))
            # item.setCheckState(Qt.Unchecked)
            self.ui.file_list_widget.addItem(item)


def run():
    # TODO: Need to simplify the design - Look at that design website for it
    #   - [x] We can remove the tree view
    #   - [x] Move the file properties below the video selector
    #   - [ ] Show map, graph under the video
    #   - [ ] Another nav tab for a report browser
    # TODO: Port over more of the functionality
    logger.info("---Running Dashcam Investigator---")
    app = QApplication([])
    logger.debug("Initialising and displaying main window")
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
