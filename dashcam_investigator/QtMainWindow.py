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


class Ui_DashcamInvestigator(object):
    def setupUi(self, DashcamInvestigator):
        if not DashcamInvestigator.objectName():
            DashcamInvestigator.setObjectName(u"DashcamInvestigator")
        DashcamInvestigator.resize(1600, 1000)
        self.actionNew_Project = QAction(DashcamInvestigator)
        self.actionNew_Project.setObjectName(u"actionNew_Project")
        self.actionOpen_Project = QAction(DashcamInvestigator)
        self.actionOpen_Project.setObjectName(u"actionOpen_Project")
        self.centralwidget = QWidget(DashcamInvestigator)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayoutWidget = QWidget(self.centralwidget)
        self.gridLayoutWidget.setObjectName(u"gridLayoutWidget")
        self.gridLayoutWidget.setGeometry(QRect(10, 0, 231, 941))
        self.left_grid = QGridLayout(self.gridLayoutWidget)
        self.left_grid.setObjectName(u"left_grid")
        self.left_grid.setSizeConstraint(QLayout.SetMaximumSize)
        self.left_grid.setContentsMargins(0, 0, 0, 0)
        self.label = QLabel(self.gridLayoutWidget)
        self.label.setObjectName(u"label")

        self.left_grid.addWidget(self.label, 1, 3, 1, 1, Qt.AlignLeft)

        self.dashcamInvestigatorLabel = QLabel(self.gridLayoutWidget)
        self.dashcamInvestigatorLabel.setObjectName(u"dashcamInvestigatorLabel")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.dashcamInvestigatorLabel.sizePolicy().hasHeightForWidth())
        self.dashcamInvestigatorLabel.setSizePolicy(sizePolicy)
        font = QFont()
        font.setPointSize(14)
        self.dashcamInvestigatorLabel.setFont(font)

        self.left_grid.addWidget(self.dashcamInvestigatorLabel, 0, 3, 1, 1, Qt.AlignHCenter|Qt.AlignTop)

        self.directory_tree_view = QTreeView(self.gridLayoutWidget)
        self.directory_tree_view.setObjectName(u"directory_tree_view")

        self.left_grid.addWidget(self.directory_tree_view, 3, 3, 1, 1)

        self.gridLayoutWidget_2 = QWidget(self.centralwidget)
        self.gridLayoutWidget_2.setObjectName(u"gridLayoutWidget_2")
        self.gridLayoutWidget_2.setGeometry(QRect(250, 0, 1341, 941))
        self.right_grid = QGridLayout(self.gridLayoutWidget_2)
        self.right_grid.setObjectName(u"right_grid")
        self.right_grid.setSizeConstraint(QLayout.SetMaximumSize)
        self.right_grid.setContentsMargins(0, 0, 0, 0)
        self.video_grid = QGridLayout()
        self.video_grid.setObjectName(u"video_grid")
        self.video_grid.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.QVideoWidget = QVideoWidget(self.gridLayoutWidget_2)
        self.QVideoWidget.setObjectName(u"QVideoWidget")
        sizePolicy1 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.QVideoWidget.sizePolicy().hasHeightForWidth())
        self.QVideoWidget.setSizePolicy(sizePolicy1)
        self.QVideoWidget.setMinimumSize(QSize(800, 450))
        self.QVideoWidget.setMaximumSize(QSize(16777215, 900))

        self.video_grid.addWidget(self.QVideoWidget, 0, 0, 1, 1)

        self.playerControls = QWidget(self.gridLayoutWidget_2)
        self.playerControls.setObjectName(u"playerControls")
        self.playerControls.setMinimumSize(QSize(1000, 50))
        self.playerControls.setMaximumSize(QSize(1000, 50))
        self.pushButton = QPushButton(self.playerControls)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setGeometry(QRect(330, 20, 71, 29))
        self.pushButton_2 = QPushButton(self.playerControls)
        self.pushButton_2.setObjectName(u"pushButton_2")
        self.pushButton_2.setGeometry(QRect(410, 20, 93, 29))
        self.pushButton_3 = QPushButton(self.playerControls)
        self.pushButton_3.setObjectName(u"pushButton_3")
        self.pushButton_3.setGeometry(QRect(510, 20, 93, 29))
        self.horizontalSlider = QSlider(self.playerControls)
        self.horizontalSlider.setObjectName(u"horizontalSlider")
        self.horizontalSlider.setGeometry(QRect(30, 0, 950, 22))
        self.horizontalSlider.setMinimumSize(QSize(950, 0))
        self.horizontalSlider.setMaximumSize(QSize(950, 16777215))
        self.horizontalSlider.setOrientation(Qt.Horizontal)

        self.video_grid.addWidget(self.playerControls, 1, 0, 1, 1, Qt.AlignHCenter|Qt.AlignBottom)


        self.right_grid.addLayout(self.video_grid, 0, 0, 1, 1)

        self.data_grid = QGridLayout()
        self.data_grid.setObjectName(u"data_grid")
        self.dataView = QTabWidget(self.gridLayoutWidget_2)
        self.dataView.setObjectName(u"dataView")
        sizePolicy2 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.dataView.sizePolicy().hasHeightForWidth())
        self.dataView.setSizePolicy(sizePolicy2)
        self.dataView.setMinimumSize(QSize(0, 100))
        self.map_tab = QWidget()
        self.map_tab.setObjectName(u"map_tab")
        self.dataView.addTab(self.map_tab, "")
        self.data_tab = QWidget()
        self.data_tab.setObjectName(u"data_tab")
        self.dataView.addTab(self.data_tab, "")

        self.data_grid.addWidget(self.dataView, 0, 0, 1, 1)


        self.right_grid.addLayout(self.data_grid, 1, 0, 1, 1)

        DashcamInvestigator.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(DashcamInvestigator)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1600, 26))
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName(u"menuFile")
        DashcamInvestigator.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(DashcamInvestigator)
        self.statusbar.setObjectName(u"statusbar")
        DashcamInvestigator.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menuFile.addAction(self.actionNew_Project)
        self.menuFile.addAction(self.actionOpen_Project)

        self.retranslateUi(DashcamInvestigator)

        self.dataView.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(DashcamInvestigator)
    # setupUi

    def retranslateUi(self, DashcamInvestigator):
        DashcamInvestigator.setWindowTitle(QCoreApplication.translate("DashcamInvestigator", u"MainWindow", None))
        self.actionNew_Project.setText(QCoreApplication.translate("DashcamInvestigator", u"New Project", None))
        self.actionOpen_Project.setText(QCoreApplication.translate("DashcamInvestigator", u"Open Project", None))
        self.label.setText(QCoreApplication.translate("DashcamInvestigator", u"Project files", None))
        self.dashcamInvestigatorLabel.setText(QCoreApplication.translate("DashcamInvestigator", u"Dashcam Investigator", None))
        self.pushButton.setText(QCoreApplication.translate("DashcamInvestigator", u"Play", None))
        self.pushButton_2.setText(QCoreApplication.translate("DashcamInvestigator", u"Pause", None))
        self.pushButton_3.setText(QCoreApplication.translate("DashcamInvestigator", u"Next", None))
        self.dataView.setTabText(self.dataView.indexOf(self.map_tab), QCoreApplication.translate("DashcamInvestigator", u"Tab 1", None))
        self.dataView.setTabText(self.dataView.indexOf(self.data_tab), QCoreApplication.translate("DashcamInvestigator", u"Tab 2", None))
        self.menuFile.setTitle(QCoreApplication.translate("DashcamInvestigator", u"File", None))
    # retranslateUi

