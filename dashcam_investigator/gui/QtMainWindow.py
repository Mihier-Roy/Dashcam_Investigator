# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainwindow.ui'
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
        MainWindow.resize(1600, 965)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.navigation_tab_widget = QTabWidget(self.centralwidget)
        self.navigation_tab_widget.setObjectName(u"navigation_tab_widget")
        self.navigation_tab_widget.setGeometry(QRect(0, 0, 1601, 941))
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.navigation_tab_widget.sizePolicy().hasHeightForWidth())
        self.navigation_tab_widget.setSizePolicy(sizePolicy)
        self.navigation_tab_widget.setTabPosition(QTabWidget.West)
        self.landing_tab = QWidget()
        self.landing_tab.setObjectName(u"landing_tab")
        self.widget = QWidget(self.landing_tab)
        self.widget.setObjectName(u"widget")
        self.widget.setGeometry(QRect(4, 60, 1561, 66))
        self.tool_header = QVBoxLayout(self.widget)
        self.tool_header.setObjectName(u"tool_header")
        self.tool_header.setContentsMargins(0, 0, 0, 0)
        self.tool_label = QLabel(self.widget)
        self.tool_label.setObjectName(u"tool_label")
        font = QFont()
        font.setPointSize(24)
        self.tool_label.setFont(font)
        self.tool_label.setAlignment(Qt.AlignCenter)

        self.tool_header.addWidget(self.tool_label)

        self.line = QFrame(self.widget)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)

        self.tool_header.addWidget(self.line)

        self.widget1 = QWidget(self.landing_tab)
        self.widget1.setObjectName(u"widget1")
        self.widget1.setGeometry(QRect(420, 240, 739, 281))
        self.landing_options_layout = QVBoxLayout(self.widget1)
        self.landing_options_layout.setObjectName(u"landing_options_layout")
        self.landing_options_layout.setContentsMargins(0, 0, 0, 0)
        self.welcome_label = QLabel(self.widget1)
        self.welcome_label.setObjectName(u"welcome_label")
        font1 = QFont()
        font1.setPointSize(14)
        self.welcome_label.setFont(font1)
        self.welcome_label.setAlignment(Qt.AlignCenter)

        self.landing_options_layout.addWidget(self.welcome_label)

        self.new_project_button = QPushButton(self.widget1)
        self.new_project_button.setObjectName(u"new_project_button")
        font2 = QFont()
        font2.setPointSize(11)
        self.new_project_button.setFont(font2)

        self.landing_options_layout.addWidget(self.new_project_button)

        self.or_label = QLabel(self.widget1)
        self.or_label.setObjectName(u"or_label")
        self.or_label.setFont(font1)
        self.or_label.setAlignment(Qt.AlignCenter)

        self.landing_options_layout.addWidget(self.or_label)

        self.existing_project_button = QPushButton(self.widget1)
        self.existing_project_button.setObjectName(u"existing_project_button")
        self.existing_project_button.setFont(font2)

        self.landing_options_layout.addWidget(self.existing_project_button)

        self.navigation_tab_widget.addTab(self.landing_tab, "")
        self.project_tab = QWidget()
        self.project_tab.setObjectName(u"project_tab")
        self.layoutWidget = QWidget(self.project_tab)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.layoutWidget.setGeometry(QRect(0, 0, 321, 941))
        self.project_view_layout = QVBoxLayout(self.layoutWidget)
        self.project_view_layout.setObjectName(u"project_view_layout")
        self.project_view_layout.setContentsMargins(0, 0, 0, 0)
        self.file_tab = QTabWidget(self.layoutWidget)
        self.file_tab.setObjectName(u"file_tab")
        sizePolicy1 = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.file_tab.sizePolicy().hasHeightForWidth())
        self.file_tab.setSizePolicy(sizePolicy1)
        self.file_tab.setMaximumSize(QSize(311, 925))
        self.directory_tab = QWidget()
        self.directory_tab.setObjectName(u"directory_tab")
        self.dir_tree_view = QTreeView(self.directory_tab)
        self.dir_tree_view.setObjectName(u"dir_tree_view")
        self.dir_tree_view.setGeometry(QRect(0, 0, 311, 891))
        sizePolicy2 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.dir_tree_view.sizePolicy().hasHeightForWidth())
        self.dir_tree_view.setSizePolicy(sizePolicy2)
        self.dir_tree_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.file_tab.addTab(self.directory_tab, "")
        self.videos_tab = QWidget()
        self.videos_tab.setObjectName(u"videos_tab")
        self.video_list_view = QListView(self.videos_tab)
        self.video_list_view.setObjectName(u"video_list_view")
        self.video_list_view.setGeometry(QRect(0, 0, 311, 891))
        self.video_list_view.setSpacing(3)
        self.file_tab.addTab(self.videos_tab, "")

        self.project_view_layout.addWidget(self.file_tab)

        self.layoutWidget1 = QWidget(self.project_tab)
        self.layoutWidget1.setObjectName(u"layoutWidget1")
        self.layoutWidget1.setGeometry(QRect(320, 0, 1254, 931))
        self.video_workarea = QVBoxLayout(self.layoutWidget1)
        self.video_workarea.setObjectName(u"video_workarea")
        self.video_workarea.setContentsMargins(0, 0, 0, 0)
        self.video_player_layout = QVBoxLayout()
        self.video_player_layout.setObjectName(u"video_player_layout")
        self.video_player = QVideoWidget(self.layoutWidget1)
        self.video_player.setObjectName(u"video_player")
        self.video_player.setMinimumSize(QSize(0, 430))

        self.video_player_layout.addWidget(self.video_player)

        self.video_title = QLabel(self.layoutWidget1)
        self.video_title.setObjectName(u"video_title")
        self.video_title.setAlignment(Qt.AlignCenter)

        self.video_player_layout.addWidget(self.video_title)

        self.player_controls = QWidget(self.layoutWidget1)
        self.player_controls.setObjectName(u"player_controls")
        self.player_controls.setMinimumSize(QSize(1200, 50))
        self.player_controls.setMaximumSize(QSize(1240, 50))
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
        self.horizontal_slider.setGeometry(QRect(90, 0, 1050, 22))
        self.horizontal_slider.setMinimumSize(QSize(1050, 0))
        self.horizontal_slider.setMaximumSize(QSize(1050, 16777215))
        self.horizontal_slider.setOrientation(Qt.Horizontal)
        self.total_duration = QLineEdit(self.player_controls)
        self.total_duration.setObjectName(u"total_duration")
        self.total_duration.setGeometry(QRect(1160, 0, 61, 21))
        self.current_duration = QLineEdit(self.player_controls)
        self.current_duration.setObjectName(u"current_duration")
        self.current_duration.setGeometry(QRect(10, 0, 61, 21))

        self.video_player_layout.addWidget(self.player_controls)


        self.video_workarea.addLayout(self.video_player_layout)

        self.data_tabs = QTabWidget(self.layoutWidget1)
        self.data_tabs.setObjectName(u"data_tabs")
        sizePolicy3 = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Expanding)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.data_tabs.sizePolicy().hasHeightForWidth())
        self.data_tabs.setSizePolicy(sizePolicy3)
        self.map_tab = QWidget()
        self.map_tab.setObjectName(u"map_tab")
        self.maps_web_view = QWebEngineView(self.map_tab)
        self.maps_web_view.setObjectName(u"maps_web_view")
        self.maps_web_view.setGeometry(QRect(-1, -1, 1231, 391))
        self.data_tabs.addTab(self.map_tab, "")
        self.metadata_tab = QWidget()
        self.metadata_tab.setObjectName(u"metadata_tab")
        self.metadata_table = QTableView(self.metadata_tab)
        self.metadata_table.setObjectName(u"metadata_table")
        self.metadata_table.setGeometry(QRect(1, 1, 1224, 391))
        self.metadata_table.horizontalHeader().setMinimumSectionSize(550)
        self.metadata_table.horizontalHeader().setDefaultSectionSize(631)
        self.metadata_table.horizontalHeader().setStretchLastSection(True)
        self.data_tabs.addTab(self.metadata_tab, "")
        self.graph_tab = QWidget()
        self.graph_tab.setObjectName(u"graph_tab")
        self.graph_web_view = QWebEngineView(self.graph_tab)
        self.graph_web_view.setObjectName(u"graph_web_view")
        self.graph_web_view.setGeometry(QRect(0, 0, 1231, 391))
        self.data_tabs.addTab(self.graph_tab, "")
        self.notes_tab = QWidget()
        self.notes_tab.setObjectName(u"notes_tab")
        self.layoutWidget_6 = QWidget(self.notes_tab)
        self.layoutWidget_6.setObjectName(u"layoutWidget_6")
        self.layoutWidget_6.setGeometry(QRect(960, 90, 251, 201))
        self.note_button_layout = QVBoxLayout(self.layoutWidget_6)
        self.note_button_layout.setObjectName(u"note_button_layout")
        self.note_button_layout.setContentsMargins(0, 0, 0, 0)
        self.flag_video_button = QPushButton(self.layoutWidget_6)
        self.flag_video_button.setObjectName(u"flag_video_button")
        sizePolicy4 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.MinimumExpanding)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.flag_video_button.sizePolicy().hasHeightForWidth())
        self.flag_video_button.setSizePolicy(sizePolicy4)

        self.note_button_layout.addWidget(self.flag_video_button)

        self.flag_description_label = QLabel(self.layoutWidget_6)
        self.flag_description_label.setObjectName(u"flag_description_label")
        self.flag_description_label.setAlignment(Qt.AlignCenter)

        self.note_button_layout.addWidget(self.flag_description_label)

        self.save_note_button = QPushButton(self.layoutWidget_6)
        self.save_note_button.setObjectName(u"save_note_button")
        sizePolicy4.setHeightForWidth(self.save_note_button.sizePolicy().hasHeightForWidth())
        self.save_note_button.setSizePolicy(sizePolicy4)

        self.note_button_layout.addWidget(self.save_note_button)

        self.save_note_label = QLabel(self.layoutWidget_6)
        self.save_note_label.setObjectName(u"save_note_label")
        self.save_note_label.setAlignment(Qt.AlignCenter)

        self.note_button_layout.addWidget(self.save_note_label)

        self.note_status = QLabel(self.layoutWidget_6)
        self.note_status.setObjectName(u"note_status")
        font3 = QFont()
        font3.setPointSize(12)
        self.note_status.setFont(font3)
        self.note_status.setAlignment(Qt.AlignCenter)

        self.note_button_layout.addWidget(self.note_status)

        self.layoutWidget_7 = QWidget(self.notes_tab)
        self.layoutWidget_7.setObjectName(u"layoutWidget_7")
        self.layoutWidget_7.setGeometry(QRect(10, 10, 931, 361))
        self.notes_layout = QVBoxLayout(self.layoutWidget_7)
        self.notes_layout.setObjectName(u"notes_layout")
        self.notes_layout.setContentsMargins(0, 0, 0, 0)
        self.notes_label = QLabel(self.layoutWidget_7)
        self.notes_label.setObjectName(u"notes_label")
        self.notes_label.setFont(font1)

        self.notes_layout.addWidget(self.notes_label)

        self.notes_textbox = QTextEdit(self.layoutWidget_7)
        self.notes_textbox.setObjectName(u"notes_textbox")
        self.notes_textbox.setFont(font3)

        self.notes_layout.addWidget(self.notes_textbox)

        self.data_tabs.addTab(self.notes_tab, "")

        self.video_workarea.addWidget(self.data_tabs)

        self.navigation_tab_widget.addTab(self.project_tab, "")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1600, 26))
        MainWindow.setMenuBar(self.menubar)

        self.retranslateUi(MainWindow)

        self.navigation_tab_widget.setCurrentIndex(1)
        self.file_tab.setCurrentIndex(1)
        self.data_tabs.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.tool_label.setText(QCoreApplication.translate("MainWindow", u"Dashcam Investigator", None))
        self.welcome_label.setText(QCoreApplication.translate("MainWindow", u"Welcome to the tool! Please select an action to perform", None))
        self.new_project_button.setText(QCoreApplication.translate("MainWindow", u"Create a new project", None))
        self.or_label.setText(QCoreApplication.translate("MainWindow", u"OR", None))
        self.existing_project_button.setText(QCoreApplication.translate("MainWindow", u"Open an existing project", None))
        self.navigation_tab_widget.setTabText(self.navigation_tab_widget.indexOf(self.landing_tab), QCoreApplication.translate("MainWindow", u"Welcome", None))
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
        self.flag_description_label.setText(QCoreApplication.translate("MainWindow", u"Flag a video for future review", None))
        self.save_note_button.setText(QCoreApplication.translate("MainWindow", u"Save Note", None))
        self.save_note_label.setText(QCoreApplication.translate("MainWindow", u"Save notes for the given video", None))
        self.note_status.setText("")
        self.notes_label.setText(QCoreApplication.translate("MainWindow", u"Enter notes for this video", None))
        self.notes_textbox.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Start typing here...", None))
        self.data_tabs.setTabText(self.data_tabs.indexOf(self.notes_tab), QCoreApplication.translate("MainWindow", u"Notes", None))
        self.navigation_tab_widget.setTabText(self.navigation_tab_widget.indexOf(self.project_tab), QCoreApplication.translate("MainWindow", u"Project Tab", None))
    # retranslateUi

