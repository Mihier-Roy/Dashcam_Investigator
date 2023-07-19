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
from qfluentwidgets import NavigationInterface
from qfluentwidgets import Pivot
from qfluentwidgets import ProgressBar
from qfluentwidgets import LineEdit
from qfluentwidgets import ListView
from PySide2.QtMultimediaWidgets import QVideoWidget


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1200, 800)
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
        self.right_scroll_widget.setGeometry(QRect(0, 0, 1143, 797))
        self.horizontalLayoutWidget_2 = QWidget(self.right_scroll_widget)
        self.horizontalLayoutWidget_2.setObjectName(u"horizontalLayoutWidget_2")
        self.horizontalLayoutWidget_2.setGeometry(QRect(0, 0, 1141, 801))
        self.right_h_layout = QHBoxLayout(self.horizontalLayoutWidget_2)
        self.right_h_layout.setObjectName(u"right_h_layout")
        self.right_h_layout.setContentsMargins(0, 0, 0, 0)
        self.left_file_v_layout = QVBoxLayout()
        self.left_file_v_layout.setObjectName(u"left_file_v_layout")
        self.left_file_v_layout.setSizeConstraint(QLayout.SetMaximumSize)
        self.file_viewer_tabs = Pivot(self.horizontalLayoutWidget_2)
        self.file_viewer_tabs.setObjectName(u"file_viewer_tabs")
        self.file_viewer_tabs.setMaximumSize(QSize(200, 16777215))

        self.left_file_v_layout.addWidget(self.file_viewer_tabs)

        self.video_files_list_view = ListView(self.horizontalLayoutWidget_2)
        self.video_files_list_view.setObjectName(u"video_files_list_view")
        self.video_files_list_view.setMaximumSize(QSize(200, 16777215))

        self.left_file_v_layout.addWidget(self.video_files_list_view)


        self.right_h_layout.addLayout(self.left_file_v_layout)

        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.video_workarea_v_layout = QVBoxLayout()
        self.video_workarea_v_layout.setObjectName(u"video_workarea_v_layout")
        self.video_display_widget = QVideoWidget(self.horizontalLayoutWidget_2)
        self.video_display_widget.setObjectName(u"video_display_widget")
        self.video_display_widget.setMinimumSize(QSize(0, 300))

        self.video_workarea_v_layout.addWidget(self.video_display_widget, 0, Qt.AlignTop)

        self.playback_controls_h_layout = QHBoxLayout()
        self.playback_controls_h_layout.setObjectName(u"playback_controls_h_layout")
        self.play_button = PrimaryPushButton(self.horizontalLayoutWidget_2)
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

        self.playback_controls_h_layout.addWidget(self.play_button)

        self.pause_button = PushButton(self.horizontalLayoutWidget_2)
        self.pause_button.setObjectName(u"pause_button")
        self.pause_button.setMinimumSize(QSize(30, 0))
        self.pause_button.setMaximumSize(QSize(30, 16777215))

        self.playback_controls_h_layout.addWidget(self.pause_button)

        self.video_progress_bar = ProgressBar(self.horizontalLayoutWidget_2)
        self.video_progress_bar.setObjectName(u"video_progress_bar")
        self.video_progress_bar.setMaximumSize(QSize(16777215, 10))

        self.playback_controls_h_layout.addWidget(self.video_progress_bar)

        self.video_duration_display = LineEdit(self.horizontalLayoutWidget_2)
        self.video_duration_display.setObjectName(u"video_duration_display")
        self.video_duration_display.setMaximumSize(QSize(35, 33))
        self.video_duration_display.setMouseTracking(False)
        self.video_duration_display.setAcceptDrops(False)
        self.video_duration_display.setAutoFillBackground(False)
        self.video_duration_display.setReadOnly(True)

        self.playback_controls_h_layout.addWidget(self.video_duration_display)


        self.video_workarea_v_layout.addLayout(self.playback_controls_h_layout)


        self.verticalLayout_3.addLayout(self.video_workarea_v_layout)

        self.video_info_pivot = Pivot(self.horizontalLayoutWidget_2)
        self.video_info_pivot.setObjectName(u"video_info_pivot")
        self.video_info_pivot.setMinimumSize(QSize(210, 45))
        self.video_info_pivot.setMaximumSize(QSize(16777215, 45))

        self.verticalLayout_3.addWidget(self.video_info_pivot)

        self.video_info_scroll_area = ScrollArea(self.horizontalLayoutWidget_2)
        self.video_info_scroll_area.setObjectName(u"video_info_scroll_area")
        self.video_info_scroll_area.setWidgetResizable(True)
        self.scrollAreaWidgetContents_6 = QWidget()
        self.scrollAreaWidgetContents_6.setObjectName(u"scrollAreaWidgetContents_6")
        self.scrollAreaWidgetContents_6.setGeometry(QRect(0, 0, 562, 395))
        self.video_info_scroll_area.setWidget(self.scrollAreaWidgetContents_6)

        self.verticalLayout_3.addWidget(self.video_info_scroll_area)


        self.right_h_layout.addLayout(self.verticalLayout_3)

        self.right_scroll_area_2.setWidget(self.right_scroll_widget)

        self.main_h_layout.addWidget(self.right_scroll_area_2)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.play_button.setText(QCoreApplication.translate("MainWindow", u"Primary push button", None))
        self.pause_button.setText(QCoreApplication.translate("MainWindow", u"Push button", None))
    # retranslateUi

