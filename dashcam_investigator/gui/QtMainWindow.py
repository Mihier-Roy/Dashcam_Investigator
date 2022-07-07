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
from PySide2.QtWebEngineWidgets import QWebEngineView


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

        self.file_tab = QTabWidget(self.layoutWidget)
        self.file_tab.setObjectName(u"file_tab")
        self.directory_tab = QWidget()
        self.directory_tab.setObjectName(u"directory_tab")
        self.dir_tree_view = QTreeView(self.directory_tab)
        self.dir_tree_view.setObjectName(u"dir_tree_view")
        self.dir_tree_view.setGeometry(QRect(0, 0, 311, 841))
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.dir_tree_view.sizePolicy().hasHeightForWidth())
        self.dir_tree_view.setSizePolicy(sizePolicy)
        self.dir_tree_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.file_tab.addTab(self.directory_tab, "")
        self.videos_tab = QWidget()
        self.videos_tab.setObjectName(u"videos_tab")
        self.video_list_view = QListView(self.videos_tab)
        self.video_list_view.setObjectName(u"video_list_view")
        self.video_list_view.setGeometry(QRect(0, 0, 311, 861))
        self.video_list_view.setSpacing(3)
        self.file_tab.addTab(self.videos_tab, "")

        self.project_view_layout.addWidget(self.file_tab)


        self.app_layout.addLayout(self.project_view_layout)

        self.main_view_layout = QVBoxLayout()
        self.main_view_layout.setObjectName(u"main_view_layout")
        self.video_player_layout = QVBoxLayout()
        self.video_player_layout.setObjectName(u"video_player_layout")
        self.video_player = QVideoWidget(self.layoutWidget)
        self.video_player.setObjectName(u"video_player")
        self.video_player.setMinimumSize(QSize(0, 430))

        self.video_player_layout.addWidget(self.video_player)

        self.video_title = QLabel(self.layoutWidget)
        self.video_title.setObjectName(u"video_title")
        self.video_title.setAlignment(Qt.AlignCenter)

        self.video_player_layout.addWidget(self.video_title)

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
        sizePolicy1 = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.data_tabs.sizePolicy().hasHeightForWidth())
        self.data_tabs.setSizePolicy(sizePolicy1)
        self.map_tab = QWidget()
        self.map_tab.setObjectName(u"map_tab")
        self.maps_web_view = QWebEngineView(self.map_tab)
        self.maps_web_view.setObjectName(u"maps_web_view")
        self.maps_web_view.setGeometry(QRect(-1, -1, 1251, 391))
        self.data_tabs.addTab(self.map_tab, "")
        self.metadata_tab = QWidget()
        self.metadata_tab.setObjectName(u"metadata_tab")
        self.layoutWidget1 = QWidget(self.metadata_tab)
        self.layoutWidget1.setObjectName(u"layoutWidget1")
        self.layoutWidget1.setGeometry(QRect(0, 0, 1251, 391))
        self.metadata_table_layout = QHBoxLayout(self.layoutWidget1)
        self.metadata_table_layout.setObjectName(u"metadata_table_layout")
        self.metadata_table_layout.setContentsMargins(0, 0, 0, 0)
        self.metadata_table = QTableView(self.layoutWidget1)
        self.metadata_table.setObjectName(u"metadata_table")
        self.metadata_table.horizontalHeader().setMinimumSectionSize(550)
        self.metadata_table.horizontalHeader().setDefaultSectionSize(631)
        self.metadata_table.horizontalHeader().setStretchLastSection(True)

        self.metadata_table_layout.addWidget(self.metadata_table)

        self.data_tabs.addTab(self.metadata_tab, "")
        self.graph_tab = QWidget()
        self.graph_tab.setObjectName(u"graph_tab")
        self.graph_web_view = QWebEngineView(self.graph_tab)
        self.graph_web_view.setObjectName(u"graph_web_view")
        self.graph_web_view.setGeometry(QRect(0, 0, 1251, 391))
        self.data_tabs.addTab(self.graph_tab, "")
        self.notes_tab = QWidget()
        self.notes_tab.setObjectName(u"notes_tab")
        self.widget = QWidget(self.notes_tab)
        self.widget.setObjectName(u"widget")
        self.widget.setGeometry(QRect(950, 10, 291, 361))
        self.verticalLayout = QVBoxLayout(self.widget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.flag_video_button = QPushButton(self.widget)
        self.flag_video_button.setObjectName(u"flag_video_button")
        sizePolicy2 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.MinimumExpanding)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.flag_video_button.sizePolicy().hasHeightForWidth())
        self.flag_video_button.setSizePolicy(sizePolicy2)

        self.verticalLayout.addWidget(self.flag_video_button)

        self.save_note_button = QPushButton(self.widget)
        self.save_note_button.setObjectName(u"save_note_button")
        sizePolicy2.setHeightForWidth(self.save_note_button.sizePolicy().hasHeightForWidth())
        self.save_note_button.setSizePolicy(sizePolicy2)

        self.verticalLayout.addWidget(self.save_note_button)

        self.note_status = QLabel(self.widget)
        self.note_status.setObjectName(u"note_status")
        font1 = QFont()
        font1.setPointSize(12)
        self.note_status.setFont(font1)
        self.note_status.setAlignment(Qt.AlignCenter)

        self.verticalLayout.addWidget(self.note_status)

        self.widget1 = QWidget(self.notes_tab)
        self.widget1.setObjectName(u"widget1")
        self.widget1.setGeometry(QRect(10, 10, 931, 361))
        self.verticalLayout_2 = QVBoxLayout(self.widget1)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.label = QLabel(self.widget1)
        self.label.setObjectName(u"label")
        font2 = QFont()
        font2.setPointSize(14)
        self.label.setFont(font2)

        self.verticalLayout_2.addWidget(self.label)

        self.label_2 = QLabel(self.widget1)
        self.label_2.setObjectName(u"label_2")
        font3 = QFont()
        font3.setPointSize(7)
        self.label_2.setFont(font3)

        self.verticalLayout_2.addWidget(self.label_2)

        self.notes_textbox = QTextEdit(self.widget1)
        self.notes_textbox.setObjectName(u"notes_textbox")
        self.notes_textbox.setFont(font1)

        self.verticalLayout_2.addWidget(self.notes_textbox)

        self.data_tabs.addTab(self.notes_tab, "")

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

        self.file_tab.setCurrentIndex(1)
        self.data_tabs.setCurrentIndex(3)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Dashcam Investigator", None))
        self.logo_label.setText(QCoreApplication.translate("MainWindow", u"Dashcam Investigator", None))
        self.file_tab.setTabText(self.file_tab.indexOf(self.directory_tab), QCoreApplication.translate("MainWindow", u"Directory", None))
        self.file_tab.setTabText(self.file_tab.indexOf(self.videos_tab), QCoreApplication.translate("MainWindow", u"Videos", None))
        self.video_title.setText(QCoreApplication.translate("MainWindow", u"Currently playing : ", None))
        self.play_button.setText(QCoreApplication.translate("MainWindow", u"Play", None))
        self.pause_button.setText(QCoreApplication.translate("MainWindow", u"Pause", None))
        self.stop_button.setText(QCoreApplication.translate("MainWindow", u"Stop", None))
        self.data_tabs.setTabText(self.data_tabs.indexOf(self.map_tab), QCoreApplication.translate("MainWindow", u"Map", None))
        self.data_tabs.setTabText(self.data_tabs.indexOf(self.metadata_tab), QCoreApplication.translate("MainWindow", u"Metadata", None))
        self.data_tabs.setTabText(self.data_tabs.indexOf(self.graph_tab), QCoreApplication.translate("MainWindow", u"Speed Graph", None))
        self.flag_video_button.setText(QCoreApplication.translate("MainWindow", u"Flag Video", None))
        self.save_note_button.setText(QCoreApplication.translate("MainWindow", u"Save Note", None))
        self.note_status.setText("")
        self.label.setText(QCoreApplication.translate("MainWindow", u"Enter notes for this video", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Hit the save button to save the note.", None))
        self.notes_textbox.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Start typing here...", None))
        self.data_tabs.setTabText(self.data_tabs.indexOf(self.notes_tab), QCoreApplication.translate("MainWindow", u"Notes", None))
    # retranslateUi

