# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainwindow1.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

from PySide2.QtMultimediaWidgets import QVideoWidget


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1600, 1000)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.widget = QWidget(self.centralwidget)
        self.widget.setObjectName("widget")
        self.widget.setGeometry(QRect(10, 0, 1581, 941))
        self.app_layout = QHBoxLayout(self.widget)
        self.app_layout.setObjectName("app_layout")
        self.app_layout.setContentsMargins(0, 0, 0, 0)
        self.project_view_layout = QVBoxLayout()
        self.project_view_layout.setObjectName("project_view_layout")
        self.logo_label = QLabel(self.widget)
        self.logo_label.setObjectName("logo_label")
        font = QFont()
        font.setPointSize(15)
        font.setBold(True)
        font.setUnderline(False)
        self.logo_label.setFont(font)
        self.logo_label.setAlignment(Qt.AlignCenter)

        self.project_view_layout.addWidget(self.logo_label)

        self.dir_label = QLabel(self.widget)
        self.dir_label.setObjectName("dir_label")

        self.project_view_layout.addWidget(self.dir_label)

        self.dir_tree_view = QTreeView(self.widget)
        self.dir_tree_view.setObjectName("dir_tree_view")
        self.dir_tree_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        self.project_view_layout.addWidget(self.dir_tree_view)

        self.app_layout.addLayout(self.project_view_layout)

        self.main_view_layout = QVBoxLayout()
        self.main_view_layout.setObjectName("main_view_layout")
        self.video_player_layout = QVBoxLayout()
        self.video_player_layout.setObjectName("video_player_layout")
        self.video_player = QVideoWidget(self.widget)
        self.video_player.setObjectName("video_player")
        self.video_player.setMinimumSize(QSize(0, 450))

        self.video_player_layout.addWidget(self.video_player)

        self.player_controls = QWidget(self.widget)
        self.player_controls.setObjectName("player_controls")
        self.player_controls.setMinimumSize(QSize(1250, 50))
        self.player_controls.setMaximumSize(QSize(1250, 50))
        self.play_button = QPushButton(self.player_controls)
        self.play_button.setObjectName("play_button")
        self.play_button.setGeometry(QRect(480, 20, 71, 29))
        self.pause_button = QPushButton(self.player_controls)
        self.pause_button.setObjectName("pause_button")
        self.pause_button.setGeometry(QRect(560, 20, 93, 29))
        self.stop_button = QPushButton(self.player_controls)
        self.stop_button.setObjectName("stop_button")
        self.stop_button.setGeometry(QRect(660, 20, 93, 29))
        self.horizontal_slider = QSlider(self.player_controls)
        self.horizontal_slider.setObjectName("horizontal_slider")
        self.horizontal_slider.setGeometry(QRect(110, 0, 1050, 22))
        self.horizontal_slider.setMinimumSize(QSize(1050, 0))
        self.horizontal_slider.setMaximumSize(QSize(1050, 16777215))
        self.horizontal_slider.setOrientation(Qt.Horizontal)
        self.total_duration = QLineEdit(self.player_controls)
        self.total_duration.setObjectName("total_duration")
        self.total_duration.setGeometry(QRect(1180, 0, 61, 21))
        self.current_duration = QLineEdit(self.player_controls)
        self.current_duration.setObjectName("current_duration")
        self.current_duration.setGeometry(QRect(30, 0, 61, 21))

        self.video_player_layout.addWidget(self.player_controls)

        self.main_view_layout.addLayout(self.video_player_layout)

        self.data_tabs = QTabWidget(self.widget)
        self.data_tabs.setObjectName("data_tabs")
        sizePolicy = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.data_tabs.sizePolicy().hasHeightForWidth())
        self.data_tabs.setSizePolicy(sizePolicy)
        self.map_tab = QWidget()
        self.map_tab.setObjectName("map_tab")
        self.data_tabs.addTab(self.map_tab, "")
        self.metadata_tab = QWidget()
        self.metadata_tab.setObjectName("metadata_tab")
        self.data_tabs.addTab(self.metadata_tab, "")

        self.main_view_layout.addWidget(self.data_tabs)

        self.app_layout.addLayout(self.main_view_layout)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName("menubar")
        self.menubar.setGeometry(QRect(0, 0, 1600, 26))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        self.data_tabs.setCurrentIndex(0)

        QMetaObject.connectSlotsByName(MainWindow)

    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(
            QCoreApplication.translate("MainWindow", "Dashcam Investigator", None)
        )
        self.logo_label.setText(
            QCoreApplication.translate("MainWindow", "Dashcam Investigator", None)
        )
        self.dir_label.setText(
            QCoreApplication.translate("MainWindow", "Project files", None)
        )
        self.play_button.setText(QCoreApplication.translate("MainWindow", "Play", None))
        self.pause_button.setText(
            QCoreApplication.translate("MainWindow", "Pause", None)
        )
        self.stop_button.setText(QCoreApplication.translate("MainWindow", "Stop", None))
        self.data_tabs.setTabText(
            self.data_tabs.indexOf(self.map_tab),
            QCoreApplication.translate("MainWindow", "Map", None),
        )
        self.data_tabs.setTabText(
            self.data_tabs.indexOf(self.metadata_tab),
            QCoreApplication.translate("MainWindow", "Metadata", None),
        )

    # retranslateUi