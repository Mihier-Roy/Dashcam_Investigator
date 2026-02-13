# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'dialog.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(792, 362)
        self.buttonBox = QDialogButtonBox(Dialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setGeometry(QRect(440, 310, 341, 32))
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        self.input_edit = QTextEdit(Dialog)
        self.input_edit.setObjectName(u"input_edit")
        self.input_edit.setGeometry(QRect(160, 70, 571, 31))
        self.input_dir_label = QLabel(Dialog)
        self.input_dir_label.setObjectName(u"input_dir_label")
        self.input_dir_label.setGeometry(QRect(20, 69, 131, 31))
        self.input_dir_button = QPushButton(Dialog)
        self.input_dir_button.setObjectName(u"input_dir_button")
        self.input_dir_button.setGeometry(QRect(750, 70, 31, 29))
        self.output_dir_button = QPushButton(Dialog)
        self.output_dir_button.setObjectName(u"output_dir_button")
        self.output_dir_button.setGeometry(QRect(750, 130, 31, 29))
        self.output_dir_label = QLabel(Dialog)
        self.output_dir_label.setObjectName(u"output_dir_label")
        self.output_dir_label.setGeometry(QRect(20, 129, 121, 31))
        self.output_edit = QTextEdit(Dialog)
        self.output_edit.setObjectName(u"output_edit")
        self.output_edit.setGeometry(QRect(160, 130, 571, 31))
        self.case_label = QLabel(Dialog)
        self.case_label.setObjectName(u"case_label")
        self.case_label.setGeometry(QRect(20, 189, 121, 31))
        self.case_edit = QTextEdit(Dialog)
        self.case_edit.setObjectName(u"case_edit")
        self.case_edit.setGeometry(QRect(160, 190, 571, 31))
        self.investigator_edit = QTextEdit(Dialog)
        self.investigator_edit.setObjectName(u"investigator_edit")
        self.investigator_edit.setGeometry(QRect(160, 251, 571, 31))
        self.investigator_label = QLabel(Dialog)
        self.investigator_label.setObjectName(u"investigator_label")
        self.investigator_label.setGeometry(QRect(20, 250, 121, 31))
        self.input_dir_help = QLabel(Dialog)
        self.input_dir_help.setObjectName(u"input_dir_help")
        self.input_dir_help.setGeometry(QRect(160, 100, 571, 20))
        self.output_dir_help = QLabel(Dialog)
        self.output_dir_help.setObjectName(u"output_dir_help")
        self.output_dir_help.setGeometry(QRect(160, 160, 571, 20))
        self.case_help = QLabel(Dialog)
        self.case_help.setObjectName(u"case_help")
        self.case_help.setGeometry(QRect(160, 220, 571, 20))
        self.investigator_help = QLabel(Dialog)
        self.investigator_help.setObjectName(u"investigator_help")
        self.investigator_help.setGeometry(QRect(160, 280, 571, 20))
        self.new_project_label = QLabel(Dialog)
        self.new_project_label.setObjectName(u"new_project_label")
        self.new_project_label.setGeometry(QRect(330, 10, 131, 20))
        font = QFont()
        font.setPointSize(14)
        self.new_project_label.setFont(font)

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Dialog", None))
        self.input_dir_label.setText(QCoreApplication.translate("Dialog", u"Dashcam Directory", None))
        self.input_dir_button.setText(QCoreApplication.translate("Dialog", u"...", None))
        self.output_dir_button.setText(QCoreApplication.translate("Dialog", u"...", None))
        self.output_dir_label.setText(QCoreApplication.translate("Dialog", u"Ouput Directory", None))
        self.case_label.setText(QCoreApplication.translate("Dialog", u"Case Name", None))
        self.investigator_label.setText(QCoreApplication.translate("Dialog", u"Investigator Name", None))
        self.input_dir_help.setText(QCoreApplication.translate("Dialog", u"Select the directory where dashcam evidence is stored", None))
        self.output_dir_help.setText(QCoreApplication.translate("Dialog", u"Select the directory where output from the tool will be stored", None))
        self.case_help.setText(QCoreApplication.translate("Dialog", u"Enter the name of the case", None))
        self.investigator_help.setText(QCoreApplication.translate("Dialog", u"Enter your name", None))
        self.new_project_label.setText(QCoreApplication.translate("Dialog", u"New Project", None))
    # retranslateUi

