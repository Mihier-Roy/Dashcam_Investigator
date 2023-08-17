# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'DashInv_MainWindow.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

from qfluentwidgets import PushButton
from qfluentwidgets import PrimaryPushButton
from qfluentwidgets import ScrollArea
from qfluentwidgets import TitleLabel
from qfluentwidgets import NavigationInterface
from qfluentwidgets import Pivot
from qfluentwidgets import ProgressBar
from qfluentwidgets import LineEdit
from qfluentwidgets import ListWidget
from PySide2.QtMultimediaWidgets import QVideoWidget


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1200, 802)
        MainWindow.setMinimumSize(QSize(1200, 800))
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayoutWidget = QWidget(self.centralwidget)
        self.horizontalLayoutWidget.setObjectName(u"horizontalLayoutWidget")
        self.horizontalLayoutWidget.setGeometry(QRect(0, 0, 1201, 801))
        self.main_h_layout = QHBoxLayout(self.horizontalLayoutWidget)
        self.main_h_layout.setObjectName(u"main_h_layout")
        self.main_h_layout.setContentsMargins(0, 0, 0, 0)
        self.NavigationInterface = NavigationInterface(self.horizontalLayoutWidget)
        self.NavigationInterface.setObjectName(u"NavigationInterface")

        self.main_h_layout.addWidget(self.NavigationInterface)

        self.right_scroll_area_2 = ScrollArea(self.horizontalLayoutWidget)
        self.right_scroll_area_2.setObjectName(u"right_scroll_area_2")
        self.right_scroll_area_2.setWidgetResizable(True)
        self.right_scroll_widget = QWidget()
        self.right_scroll_widget.setObjectName(u"right_scroll_widget")
        self.right_scroll_widget.setGeometry(QRect(0, 0, 1142, 797))
        self.layoutWidget = QWidget(self.right_scroll_widget)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.layoutWidget.setGeometry(QRect(0, 0, 1141, 801))
        self.content_grid = QGridLayout(self.layoutWidget)
        self.content_grid.setObjectName(u"content_grid")
        self.content_grid.setContentsMargins(0, 0, 0, 0)
        self.file_info_v_layout = QVBoxLayout()
        self.file_info_v_layout.setObjectName(u"file_info_v_layout")
        self.file_info_v_layout.setContentsMargins(-1, 0, -1, -1)
        self.video_display_widget = QVideoWidget(self.layoutWidget)
        self.video_display_widget.setObjectName(u"video_display_widget")
        self.video_display_widget.setMinimumSize(QSize(0, 300))

        self.file_info_v_layout.addWidget(self.video_display_widget)

        self.playback_controls_spliter = QSplitter(self.layoutWidget)
        self.playback_controls_spliter.setObjectName(u"playback_controls_spliter")
        self.playback_controls_spliter.setOrientation(Qt.Horizontal)
        self.play_button = PrimaryPushButton(self.playback_controls_spliter)
        self.play_button.setObjectName(u"play_button")
        self.play_button.setMinimumSize(QSize(30, 0))
        self.play_button.setMaximumSize(QSize(30, 16777215))
        icon = QIcon()
        iconThemeName = u"PLAY"
        if QIcon.hasThemeIcon(iconThemeName):
            icon = QIcon.fromTheme(iconThemeName)
        else:
            icon.addFile(u".", QSize(), QIcon.Normal, QIcon.Off)
        
        self.play_button.setIcon(icon)
        self.playback_controls_spliter.addWidget(self.play_button)
        self.pause_button = PushButton(self.playback_controls_spliter)
        self.pause_button.setObjectName(u"pause_button")
        self.pause_button.setMinimumSize(QSize(30, 0))
        self.pause_button.setMaximumSize(QSize(30, 16777215))
        self.playback_controls_spliter.addWidget(self.pause_button)
        self.video_progress_bar = ProgressBar(self.playback_controls_spliter)
        self.video_progress_bar.setObjectName(u"video_progress_bar")
        self.video_progress_bar.setMaximumSize(QSize(16777215, 10))
        self.playback_controls_spliter.addWidget(self.video_progress_bar)
        self.video_duration_display = LineEdit(self.playback_controls_spliter)
        self.video_duration_display.setObjectName(u"video_duration_display")
        self.video_duration_display.setMaximumSize(QSize(35, 33))
        self.video_duration_display.setMouseTracking(False)
        self.video_duration_display.setAcceptDrops(False)
        self.video_duration_display.setAutoFillBackground(False)
        self.video_duration_display.setReadOnly(True)
        self.playback_controls_spliter.addWidget(self.video_duration_display)

        self.file_info_v_layout.addWidget(self.playback_controls_spliter)

        self.line_2 = QFrame(self.layoutWidget)
        self.line_2.setObjectName(u"line_2")
        self.line_2.setFrameShape(QFrame.HLine)
        self.line_2.setFrameShadow(QFrame.Sunken)

        self.file_info_v_layout.addWidget(self.line_2)

        self.video_info_pivot = Pivot(self.layoutWidget)
        self.video_info_pivot.setObjectName(u"video_info_pivot")
        self.video_info_pivot.setMinimumSize(QSize(210, 45))
        self.video_info_pivot.setMaximumSize(QSize(16777215, 45))

        self.file_info_v_layout.addWidget(self.video_info_pivot)

        self.video_info_stacked_widget = QStackedWidget(self.layoutWidget)
        self.video_info_stacked_widget.setObjectName(u"video_info_stacked_widget")
        self.page = QWidget()
        self.page.setObjectName(u"page")
        self.video_info_stacked_widget.addWidget(self.page)
        self.page_2 = QWidget()
        self.page_2.setObjectName(u"page_2")
        self.video_info_stacked_widget.addWidget(self.page_2)

        self.file_info_v_layout.addWidget(self.video_info_stacked_widget)


        self.content_grid.addLayout(self.file_info_v_layout, 0, 2, 1, 1)

        self.file_browser_v_layout_3 = QVBoxLayout()
        self.file_browser_v_layout_3.setObjectName(u"file_browser_v_layout_3")
        self.TitleLabel = TitleLabel(self.layoutWidget)
        self.TitleLabel.setObjectName(u"TitleLabel")

        self.file_browser_v_layout_3.addWidget(self.TitleLabel, 0, Qt.AlignLeft)

        self.file_list_widget = ListWidget(self.layoutWidget)
        self.file_list_widget.setObjectName(u"file_list_widget")

        self.file_browser_v_layout_3.addWidget(self.file_list_widget)

        self.TitleLabel_2 = TitleLabel(self.layoutWidget)
        self.TitleLabel_2.setObjectName(u"TitleLabel_2")

        self.file_browser_v_layout_3.addWidget(self.TitleLabel_2, 0, Qt.AlignLeft)

        self.file_properties_list_widget = ListWidget(self.layoutWidget)
        self.file_properties_list_widget.setObjectName(u"file_properties_list_widget")

        self.file_browser_v_layout_3.addWidget(self.file_properties_list_widget)


        self.content_grid.addLayout(self.file_browser_v_layout_3, 0, 0, 1, 1)

        self.line = QFrame(self.layoutWidget)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.VLine)
        self.line.setFrameShadow(QFrame.Sunken)

        self.content_grid.addWidget(self.line, 0, 1, 1, 1)

        self.right_scroll_area_2.setWidget(self.right_scroll_widget)

        self.main_h_layout.addWidget(self.right_scroll_area_2)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Dashcam Investigator", None))
        self.play_button.setText(QCoreApplication.translate("MainWindow", u"Primary push button", None))
        self.pause_button.setText(QCoreApplication.translate("MainWindow", u"Push button", None))
        self.TitleLabel.setText(QCoreApplication.translate("MainWindow", u"Video List", None))
        self.TitleLabel_2.setText(QCoreApplication.translate("MainWindow", u"Video Properties", None))
    # retranslateUi

