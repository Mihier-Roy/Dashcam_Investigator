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
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1600, 1000)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.layoutWidget = QWidget(self.centralwidget)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.layoutWidget.setGeometry(QRect(10, 0, 1581, 941))
        self.app_layout = QHBoxLayout(self.layoutWidget)
        self.app_layout.setObjectName(u"app_layout")
        self.app_layout.setContentsMargins(0, 0, 0, 0)
        self.project_view_layout = QVBoxLayout()
        self.project_view_layout.setObjectName(u"project_view_layout")
        self.logo_label = QLabel(self.layoutWidget)
        self.logo_label.setObjectName(u"logo_label")
        font = QFont()
        font.setPointSize(15)
        font.setBold(True)
        font.setUnderline(False)
        self.logo_label.setFont(font)
        self.logo_label.setAlignment(Qt.AlignCenter)

        self.project_view_layout.addWidget(self.logo_label)

        self.dir_label = QLabel(self.layoutWidget)
        self.dir_label.setObjectName(u"dir_label")

        self.project_view_layout.addWidget(self.dir_label)

        self.dir_tree_view = QTreeView(self.layoutWidget)
        self.dir_tree_view.setObjectName(u"dir_tree_view")
        self.dir_tree_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        self.project_view_layout.addWidget(self.dir_tree_view)


        self.app_layout.addLayout(self.project_view_layout)

        self.main_view_layout = QVBoxLayout()
        self.main_view_layout.setObjectName(u"main_view_layout")
        self.video_player_layout = QVBoxLayout()
        self.video_player_layout.setObjectName(u"video_player_layout")
        self.video_player = QVideoWidget(self.layoutWidget)
        self.video_player.setObjectName(u"video_player")
        self.video_player.setMinimumSize(QSize(0, 450))

        self.video_player_layout.addWidget(self.video_player)

        self.player_controls = QWidget(self.layoutWidget)
        self.player_controls.setObjectName(u"player_controls")
        self.player_controls.setMinimumSize(QSize(1250, 50))
        self.player_controls.setMaximumSize(QSize(1250, 50))
        self.play_button = QPushButton(self.player_controls)
        self.play_button.setObjectName(u"play_button")
        self.play_button.setGeometry(QRect(480, 20, 71, 29))
        self.pause_button = QPushButton(self.player_controls)
        self.pause_button.setObjectName(u"pause_button")
        self.pause_button.setGeometry(QRect(560, 20, 93, 29))
        self.stop_button = QPushButton(self.player_controls)
        self.stop_button.setObjectName(u"stop_button")
        self.stop_button.setGeometry(QRect(660, 20, 93, 29))
        self.horizontal_slider = QSlider(self.player_controls)
        self.horizontal_slider.setObjectName(u"horizontal_slider")
        self.horizontal_slider.setGeometry(QRect(110, 0, 1050, 22))
        self.horizontal_slider.setMinimumSize(QSize(1050, 0))
        self.horizontal_slider.setMaximumSize(QSize(1050, 16777215))
        self.horizontal_slider.setOrientation(Qt.Horizontal)
        self.total_duration = QLineEdit(self.player_controls)
        self.total_duration.setObjectName(u"total_duration")
        self.total_duration.setGeometry(QRect(1180, 0, 61, 21))
        self.current_duration = QLineEdit(self.player_controls)
        self.current_duration.setObjectName(u"current_duration")
        self.current_duration.setGeometry(QRect(30, 0, 61, 21))

        self.video_player_layout.addWidget(self.player_controls)


        self.main_view_layout.addLayout(self.video_player_layout)

        self.data_tabs = QTabWidget(self.layoutWidget)
        self.data_tabs.setObjectName(u"data_tabs")
        sizePolicy = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.data_tabs.sizePolicy().hasHeightForWidth())
        self.data_tabs.setSizePolicy(sizePolicy)
        self.map_tab = QWidget()
        self.map_tab.setObjectName(u"map_tab")
        self.data_tabs.addTab(self.map_tab, "")
        self.metadata_tab = QWidget()
        self.metadata_tab.setObjectName(u"metadata_tab")
        self.widget = QWidget(self.metadata_tab)
        self.widget.setObjectName(u"widget")
        self.widget.setGeometry(QRect(0, 0, 1251, 391))
        self.horizontalLayout = QHBoxLayout(self.widget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.metadata_table = QTableView(self.widget)
        self.metadata_table.setObjectName(u"metadata_table")
        self.metadata_table.horizontalHeader().setMinimumSectionSize(550)
        self.metadata_table.horizontalHeader().setDefaultSectionSize(631)
        self.metadata_table.horizontalHeader().setStretchLastSection(True)

        self.horizontalLayout.addWidget(self.metadata_table)

        self.gps_table = QTableView(self.widget)
        self.gps_table.setObjectName(u"gps_table")
        self.gps_table.horizontalHeader().setMinimumSectionSize(100)
        self.gps_table.horizontalHeader().setDefaultSectionSize(200)

        self.horizontalLayout.addWidget(self.gps_table)

        self.data_tabs.addTab(self.metadata_tab, "")

        self.main_view_layout.addWidget(self.data_tabs)


        self.app_layout.addLayout(self.main_view_layout)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1600, 26))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        self.data_tabs.setCurrentIndex(1)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Dashcam Investigator", None))
        self.logo_label.setText(QCoreApplication.translate("MainWindow", u"Dashcam Investigator", None))
        self.dir_label.setText(QCoreApplication.translate("MainWindow", u"Project files", None))
        self.play_button.setText(QCoreApplication.translate("MainWindow", u"Play", None))
        self.pause_button.setText(QCoreApplication.translate("MainWindow", u"Pause", None))
        self.stop_button.setText(QCoreApplication.translate("MainWindow", u"Stop", None))
        self.data_tabs.setTabText(self.data_tabs.indexOf(self.map_tab), QCoreApplication.translate("MainWindow", u"Map", None))
        self.data_tabs.setTabText(self.data_tabs.indexOf(self.metadata_tab), QCoreApplication.translate("MainWindow", u"Metadata", None))
    # retranslateUi

